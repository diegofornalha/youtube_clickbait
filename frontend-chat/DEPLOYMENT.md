# 🚀 Deployment Guide - Claude Chat

## Opções de Deploy

### **Opção 1: Local (Desenvolvimento)** ✅

```bash
cd frontend-chat
./start.sh
open frontend/index.html
```

**Vantagens:**
- ✅ Rápido para testar
- ✅ Sem custos
- ✅ Debug fácil

**Desvantagens:**
- ❌ Apenas local
- ❌ Não escalável

---

### **Opção 2: Docker Compose (Recomendado)** 🐳

#### **1. Criar Dockerfile:**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Claude SDK (assumindo que está no parent)
COPY ../claude-agent-sdk-python /claude-sdk
RUN pip install -e /claude-sdk

# Copy backend
COPY backend/ .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **2. Criar docker-compose.yml:**

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
    restart: unless-stopped

  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

volumes:
  neo4j_data:
```

#### **3. Deploy:**

```bash
# Build e start
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Parar
docker-compose down
```

**Acesse:**
- Frontend: http://localhost
- Backend: http://localhost:8000
- Neo4j: http://localhost:7474

---

### **Opção 3: Cloud (Produção)** ☁️

#### **Backend (Heroku):**

```bash
# heroku.yml
build:
  docker:
    web: Dockerfile

run:
  web: uvicorn server:app --host=0.0.0.0 --port=${PORT}
```

```bash
# Deploy
heroku create claude-chat-backend
heroku config:set ANTHROPIC_API_KEY=your_key
git push heroku main
```

#### **Frontend (Vercel/Netlify):**

```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod --dir=frontend
```

#### **Neo4j (Neo4j Aura):**

```bash
# Criar cluster no Neo4j Aura (cloud.neo4j.com)
# Copiar connection string
# Atualizar backend com credenciais
```

---

### **Opção 4: VPS (DigitalOcean, AWS, etc)** 🖥️

#### **1. Provision Server:**

```bash
# Ubuntu 22.04 LTS
sudo apt update
sudo apt install -y python3.10 python3-pip nginx
```

#### **2. Setup Backend:**

```bash
cd /opt
git clone <seu-repo>
cd claude-chat/frontend-chat

pip3 install -r requirements.txt
pip3 install -e ../claude-agent-sdk-python

# Criar service
sudo nano /etc/systemd/system/claude-chat.service
```

**Service file:**
```ini
[Unit]
Description=Claude Chat Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/claude-chat/frontend-chat/backend
Environment="ANTHROPIC_API_KEY=your_key"
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable claude-chat
sudo systemctl start claude-chat
```

#### **3. Setup Nginx:**

```nginx
# /etc/nginx/sites-available/claude-chat
server {
    listen 80;
    server_name chat.seudominio.com;

    # Frontend
    location / {
        root /opt/claude-chat/frontend-chat/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/claude-chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **4. SSL (Let's Encrypt):**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d chat.seudominio.com
```

---

## 🔐 Variáveis de Ambiente

### **Obrigatórias:**

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### **Opcionais:**

```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Server
PORT=8000
HOST=0.0.0.0
DEBUG=false

# Rate limiting
MAX_REQUESTS_PER_MINUTE=60

# Costs
MAX_COST_PER_DAY=10.00
```

---

## 📊 Monitoramento em Produção

### **Backend Logs:**

```bash
# Systemd logs
sudo journalctl -u claude-chat -f

# Docker logs
docker-compose logs -f backend

# File logs
tail -f /var/log/claude-chat/backend.log
```

### **Métricas:**

```bash
# Requisições
curl http://localhost:8000/metrics

# Health check
curl http://localhost:8000/

# Neo4j queue
curl http://localhost:8000/neo4j/pending
```

---

## 🛡️ Segurança em Produção

### **1. Rate Limiting:**

```python
# Adicionar ao server.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ws/chat")
@limiter.limit("60/minute")
async def websocket_chat(...):
    ...
```

### **2. CORS:**

```python
# Restringir origins em produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seudominio.com"],  # Específico!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **3. API Key Protection:**

```python
# Adicionar auth header
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket, api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("BACKEND_API_KEY"):
        await websocket.close(code=1008)
        return
    ...
```

---

## 📈 Escalabilidade

### **Load Balancer (Nginx):**

```nginx
upstream claude_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api/ {
        proxy_pass http://claude_backend;
    }
}
```

### **Redis para Sessions:**

```python
# Substituir conversations dict por Redis
import redis

r = redis.Redis(host='localhost', port=6379)

# Salvar
r.set(f"conv:{conversation_id}", json.dumps(conversation))

# Recuperar
data = r.get(f"conv:{conversation_id}")
conversation = json.loads(data)
```

---

## 💰 Custos Estimados

### **Cloud Hosting:**

| Serviço | Custo/mês | Alternativa Grátis |
|---------|-----------|---------------------|
| **Backend (Heroku)** | $7-25 | Fly.io (grátis) |
| **Frontend (Vercel)** | $0 | Sempre grátis |
| **Neo4j (Aura)** | $65 | Neo4j Desktop (local) |
| **Total** | $72-90 | $0 (self-hosted) |

### **API Usage (Claude):**

- Sonnet 4.5: ~$3 por 1M tokens input
- Uso médio: ~2K tokens/mensagem
- Custo: ~$0.006 por mensagem
- 1.000 msgs/mês ≈ $6

**Total estimado:** $78-96/mês para produção

---

## ✅ Checklist Pré-Deploy

- [ ] ANTHROPIC_API_KEY configurada
- [ ] CORS restrito para domínio específico
- [ ] Rate limiting ativado
- [ ] Logs configurados
- [ ] SSL/HTTPS ativado
- [ ] Backup configurado
- [ ] Monitoring ativado (ex: Sentry)
- [ ] Neo4j rodando (se usar)
- [ ] Tests passando (12/12)
- [ ] Docs atualizadas

---

## 🧪 Testar Deploy

```bash
# Health check
curl https://seudominio.com/api/

# WebSocket
wscat -c wss://seudominio.com/ws/chat

# Frontend
open https://seudominio.com
```

---

**Criado pelo Claude Code Agent** 🤖
**Status:** Production-ready ✅
