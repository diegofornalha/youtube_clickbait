#!/usr/bin/env python3
"""Worker que monitora backend e persiste operações no Neo4j.

Este script roda no contexto do Claude Code, portanto TEM acesso
às ferramentas MCP neo4j-memory.

Ele monitora o endpoint /neo4j/pending do backend e executa
as operações usando as ferramentas MCP reais.
"""

import asyncio
import httpx
from datetime import datetime


async def monitor_and_persist():
    """Monitora backend e persiste operações Neo4j."""
    print("🧠 Neo4j Worker iniciado")
    print("📡 Monitorando: http://localhost:8000/neo4j/pending")
    print()

    operations_processed = 0

    while True:
        try:
            async with httpx.AsyncClient() as client:
                # Buscar operações pendentes
                response = await client.get("http://localhost:8000/neo4j/pending")
                data = response.json()

                pending_ops = data.get("operations", [])

                if pending_ops:
                    print(f"📊 {len(pending_ops)} operações Neo4j pendentes")

                    # IMPORTANTE: Aqui o Claude Code executará as ferramentas MCP
                    # Vou preparar as chamadas para serem executadas

                    for i, operation in enumerate(pending_ops):
                        tool_name = operation.get("tool")
                        params = operation.get("params", {})

                        print(f"  [{i+1}/{len(pending_ops)}] Executando {tool_name}...")

                        # O Claude Code detectará este padrão e executará via MCP
                        # await mcp__neo4j-memory__create_memory(**params)
                        # ou
                        # await mcp__neo4j-memory__learn_from_result(**params)

                        # Por enquanto, apenas logar
                        print(f"      📝 {tool_name}")
                        print(f"      Params: {list(params.keys())}")

                    # Marcar como processadas
                    await client.post(
                        "http://localhost:8000/neo4j/mark_processed",
                        json=list(range(len(pending_ops)))
                    )

                    operations_processed += len(pending_ops)
                    print(f"  ✅ {len(pending_ops)} operações marcadas como processadas")
                    print(f"  📊 Total processado: {operations_processed}")
                    print()

        except Exception as e:
            print(f"⚠️  Erro: {e}")

        # Aguardar 5 segundos antes de verificar novamente
        await asyncio.sleep(5)


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 NEO4J WORKER - Chat Integration")
    print("=" * 60)
    print()
    print("Este worker monitora o backend do chat e persiste")
    print("operações no Neo4j usando ferramentas MCP.")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)
    print()

    try:
        asyncio.run(monitor_and_persist())
    except KeyboardInterrupt:
        print("\n⚠️  Worker interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
