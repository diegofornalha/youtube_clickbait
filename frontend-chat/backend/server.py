#!/usr/bin/env python3
"""Backend do chat com Claude SDK - Streaming real."""

import sys
from pathlib import Path
from datetime import datetime
from typing import AsyncIterator
import json
import uuid

# Adicionar claude-agent-sdk ao path
sdk_path = Path(__file__).parent.parent.parent / "claude-agent-sdk-python"
sys.path.insert(0, str(sdk_path))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ThinkingBlock,
    ResultMessage,
)

from code_runner import get_code_runner

app = FastAPI(title="Claude Chat API", version="1.0.0")

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento de conversas (em memória)
conversations = {}

# Sessões ativas do Claude (mantém contexto)
active_sessions = {}


class Message(BaseModel):
    """Mensagem do chat."""
    role: str
    content: str
    timestamp: str
    thinking: str | None = None


class Conversation(BaseModel):
    """Conversa completa."""
    id: str
    messages: list[Message]
    created_at: str


class ChatRequest(BaseModel):
    """Request de mensagem."""
    message: str
    conversation_id: str | None = None


class CodeExecutionRequest(BaseModel):
    """Request para executar código."""
    code: str
    language: str = "python"


@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "Claude Chat API"}


# Queue de operações Neo4j pendentes
neo4j_operations_queue = []


@app.get("/neo4j/pending")
async def get_pending_neo4j_operations():
    """Retorna operações Neo4j pendentes para execução externa."""
    return {
        "operations": neo4j_operations_queue,
        "count": len(neo4j_operations_queue)
    }


@app.post("/neo4j/mark_processed")
async def mark_neo4j_operations_processed(operation_ids: list[int]):
    """Marca operações como processadas."""
    global neo4j_operations_queue

    # Remover operações processadas
    neo4j_operations_queue = [
        op for i, op in enumerate(neo4j_operations_queue)
        if i not in operation_ids
    ]

    return {"success": True, "remaining": len(neo4j_operations_queue)}


@app.get("/conversations")
async def list_conversations():
    """Lista todas as conversas."""
    return {
        "conversations": [
            {
                "id": conv_id,
                "message_count": len(conv.messages),
                "created_at": conv.created_at,
                "last_message": conv.messages[-1].content[:100] if conv.messages else ""
            }
            for conv_id, conv in conversations.items()
        ]
    }


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retorna uma conversa específica."""
    if conversation_id not in conversations:
        return {"error": "Conversation not found"}, 404

    return conversations[conversation_id]


@app.get("/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str):
    """Exporta conversa em formato Markdown."""
    if conversation_id not in conversations:
        return {"error": "Conversation not found"}, 404

    conv = conversations[conversation_id]

    # Gerar markdown
    md_content = f"""# 💬 Conversa com Claude

**Data:** {conv.created_at}
**ID:** {conversation_id}
**Mensagens:** {len(conv.messages)}

---

"""

    for i, msg in enumerate(conv.messages, 1):
        role_emoji = "👤" if msg.role == "user" else "🤖"
        role_name = "Você" if msg.role == "user" else "Claude"

        md_content += f"## {role_emoji} {role_name} ({msg.timestamp})\n\n"
        md_content += f"{msg.content}\n\n"

        if msg.thinking:
            md_content += f"*💭 Pensamento: {msg.thinking}*\n\n"

        md_content += "---\n\n"

    return {
        "markdown": md_content,
        "filename": f"conversa_{conversation_id[:8]}.md"
    }


@app.post("/execute/code")
async def execute_code(request: CodeExecutionRequest):
    """Executa código Python de forma segura."""
    if request.language != "python":
        return {"error": "Apenas Python é suportado por enquanto"}, 400

    runner = get_code_runner()
    result = runner.run(request.code)

    return result


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket para chat com streaming."""
    await websocket.accept()

    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_text()
            request = json.loads(data)

            message = request.get("message", "")
            conversation_id = request.get("conversation_id") or str(uuid.uuid4())

            # Criar conversa se não existir
            if conversation_id not in conversations:
                conversations[conversation_id] = Conversation(
                    id=conversation_id,
                    messages=[],
                    created_at=datetime.now().isoformat()
                )

            # Adicionar mensagem do usuário
            user_message = Message(
                role="user",
                content=message,
                timestamp=datetime.now().isoformat()
            )
            conversations[conversation_id].messages.append(user_message)

            # Enviar confirmação
            await websocket.send_json({
                "type": "user_message_saved",
                "conversation_id": conversation_id
            })

            # Processar com Claude SDK (passar conversation_id para manter contexto)
            try:
                async for chunk in process_with_claude(message, conversation_id):
                    await websocket.send_json(chunk)

                    # Salvar mensagem do assistant
                    if chunk.get("type") == "result":
                        assistant_message = Message(
                            role="assistant",
                            content=chunk.get("content", ""),
                            timestamp=datetime.now().isoformat(),
                            thinking=chunk.get("thinking")
                        )
                        conversations[conversation_id].messages.append(assistant_message)

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })

    except WebSocketDisconnect:
        print("Cliente desconectado")


async def process_with_claude(message: str, conversation_id: str | None = None) -> AsyncIterator[dict]:
    """Processa mensagem com Claude SDK e retorna chunks.

    Args:
        message: Mensagem do usuário
        conversation_id: ID da conversa (mantém contexto se fornecido)
    """

    # Configurar Claude com continue_conversation para manter contexto
    options = ClaudeAgentOptions(
        system_prompt=(
            "Você é um assistente útil e conciso. "
            "Responda em português de forma clara e objetiva. "
            "Use markdown para formatar respostas. "
            "Lembre-se de informações mencionadas anteriormente na conversa."
        ),
        model="claude-sonnet-4-5",
        max_turns=10,
        continue_conversation=True,  # ← MANTÉM CONTEXTO!
        resume=conversation_id if conversation_id else None,  # Resume sessão anterior
    )

    full_content = ""
    thinking_content = ""

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(message)

            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            # Enviar chunk de texto
                            full_content += block.text

                            yield {
                                "type": "text_chunk",
                                "content": block.text,
                                "full_content": full_content
                            }

                        elif isinstance(block, ThinkingBlock):
                            # Enviar pensamento
                            thinking_content += block.thinking

                            yield {
                                "type": "thinking",
                                "content": block.thinking
                            }

                elif isinstance(msg, ResultMessage):
                    # Enviar resultado final
                    result_data = {
                        "type": "result",
                        "content": full_content,
                        "thinking": thinking_content if thinking_content else None,
                        "cost": msg.total_cost_usd,
                        "duration_ms": msg.duration_ms,
                        "num_turns": msg.num_turns,
                        "is_error": msg.is_error
                    }

                    # Enfileirar aprendizado no Neo4j
                    neo4j_operations_queue.append({
                        "tool": "mcp__neo4j-memory__learn_from_result",
                        "params": {
                            "task": f"Chat response generated",
                            "result": f"{msg.num_turns} turns, {msg.duration_ms}ms, ${msg.total_cost_usd:.4f}",
                            "success": not msg.is_error,
                            "category": "chat_interaction"
                        },
                        "timestamp": datetime.now().isoformat()
                    })

                    yield result_data

    except Exception as e:
        yield {
            "type": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando Claude Chat Server...")
    print("📡 WebSocket: ws://localhost:8000/ws/chat")
    print("📊 API Docs: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
