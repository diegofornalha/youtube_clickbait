#!/usr/bin/env python3
"""Testes automatizados do sistema de chat."""

import sys
import asyncio
from pathlib import Path

# Adicionar SDK ao path
sdk_path = Path(__file__).parent.parent / "claude-agent-sdk-python"
sys.path.insert(0, str(sdk_path))


async def test_imports():
    """Teste 1: Verificar todos os imports."""
    print("🧪 Teste 1: Imports")

    try:
        from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
        print("  ✅ Claude SDK")

        from fastapi import FastAPI, WebSocket
        print("  ✅ FastAPI")

        from pydantic import BaseModel
        print("  ✅ Pydantic")

        import uvicorn
        print("  ✅ Uvicorn")

        print("✅ Teste 1 PASSOU\n")
        return True

    except ImportError as e:
        print(f"❌ Teste 1 FALHOU: {e}\n")
        return False


async def test_claude_sdk_connection():
    """Teste 2: Conectar com Claude SDK."""
    print("🧪 Teste 2: Conexão com Claude SDK")

    try:
        from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

        options = ClaudeAgentOptions(
            system_prompt="Você é um assistente de teste. Responda apenas 'OK' para qualquer pergunta.",
            model="claude-sonnet-4-5",
            max_turns=1,
        )

        print("  🔗 Conectando ao Claude SDK...")

        async with ClaudeSDKClient(options=options) as client:
            await client.query("teste")

            print("  ⏳ Aguardando resposta...")

            response_received = False
            async for msg in client.receive_response():
                response_received = True
                print(f"  📨 Recebeu mensagem: {type(msg).__name__}")

            if response_received:
                print("✅ Teste 2 PASSOU\n")
                return True
            else:
                print("❌ Teste 2 FALHOU: Nenhuma resposta recebida\n")
                return False

    except Exception as e:
        print(f"❌ Teste 2 FALHOU: {e}\n")
        return False


async def test_streaming_functionality():
    """Teste 3: Funcionalidade de streaming."""
    print("🧪 Teste 3: Streaming de respostas")

    try:
        from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

        options = ClaudeAgentOptions(
            system_prompt="Responda de forma muito concisa.",
            max_turns=1,
        )

        chunks_received = 0
        text_received = ""

        async with ClaudeSDKClient(options=options) as client:
            await client.query("Diga apenas: Python é incrível")

            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            chunks_received += 1
                            text_received += block.text
                            print(f"  📦 Chunk {chunks_received}: {len(block.text)} chars")

        print(f"  📊 Total de chunks: {chunks_received}")
        print(f"  📝 Texto recebido: {text_received[:100]}")

        if chunks_received > 0 and text_received:
            print("✅ Teste 3 PASSOU\n")
            return True
        else:
            print("❌ Teste 3 FALHOU: Nenhum chunk recebido\n")
            return False

    except Exception as e:
        print(f"❌ Teste 3 FALHOU: {e}\n")
        return False


async def test_backend_process_function():
    """Teste 4: Função process_with_claude do backend."""
    print("🧪 Teste 4: Função process_with_claude")

    try:
        # Importar função do backend
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from server import process_with_claude

        chunks = []
        final_result = None

        async for chunk in process_with_claude("Diga apenas: teste"):
            chunks.append(chunk)
            print(f"  📦 {chunk.get('type')}: {str(chunk)[:80]}")

            if chunk.get('type') == 'result':
                final_result = chunk

        if final_result and final_result.get('content'):
            print(f"  📊 Total de chunks: {len(chunks)}")
            print(f"  💰 Custo: ${final_result.get('cost', 0):.4f}")
            print("✅ Teste 4 PASSOU\n")
            return True
        else:
            print("❌ Teste 4 FALHOU: Nenhum resultado final\n")
            return False

    except Exception as e:
        print(f"❌ Teste 4 FALHOU: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 TESTES AUTOMATIZADOS - CLAUDE CHAT")
    print("=" * 60)
    print()

    results = []

    # Teste 1: Imports
    results.append(await test_imports())

    # Teste 2: Conexão SDK
    results.append(await test_claude_sdk_connection())

    # Teste 3: Streaming
    results.append(await test_streaming_functionality())

    # Teste 4: Backend function
    results.append(await test_backend_process_function())

    # Resumo
    print("=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passou: {passed}/{total}")
    print(f"❌ Falhou: {total - passed}/{total}")
    print()

    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Sistema pronto para uso!")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        print("🔧 Corrija os erros antes de usar em produção")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
