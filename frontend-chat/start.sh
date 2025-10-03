#!/bin/bash
# Script para iniciar o Claude Chat

echo "🚀 Iniciando Claude Chat..."
echo

# Verificar se está no diretório correto
if [ ! -f "backend/server.py" ]; then
    echo "❌ Erro: Execute este script do diretório frontend-chat/"
    exit 1
fi

# Verificar dependências
echo "📦 Verificando dependências..."
python3 -c "from fastapi import FastAPI; from claude_agent_sdk import ClaudeSDKClient" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências faltando. Instalando..."
    pip3 install -q -r requirements.txt
    pip3 install -q -e ../claude-agent-sdk-python
fi

echo "✅ Dependências OK"
echo

# Iniciar servidor
echo "🌐 Iniciando servidor backend..."
echo "📡 WebSocket: ws://localhost:8000/ws/chat"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🌍 Frontend: Abra frontend/index.html no navegador"
echo
echo "Pressione Ctrl+C para parar"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

cd backend && python3 server.py
