# 🔧 MCP Tools Customizadas - Criar Suas Próprias Ferramentas

## O que são SDK MCP Tools?

**SDK MCP Tools** são ferramentas customizadas que rodam **in-process** (no mesmo processo Python), sem necessidade de servidor externo.

## Anatomia de uma Tool

### **1. Decorator @tool**

```python
from claude_agent_sdk import tool

@tool(
    name="nome_da_tool",           # ID único
    description="O que ela faz",   # Claude usa isso para decidir quando usar
    input_schema={"param": str}    # Schema dos parâmetros
)
async def minha_tool(args):
    """Implementação da ferramenta."""
    # args é um dict com os parâmetros
    resultado = args["param"].upper()

    # Retornar dict com content
    return {
        "content": [
            {"type": "text", "text": f"Resultado: {resultado}"}
        ]
    }
```

### **2. Input Schema**

**Opção 1: Dict simples** (recomendado)
```python
@tool("greet", "Cumprimentar usuário", {"name": str, "age": int})
async def greet(args):
    return {"content": [{"type": "text", "text": f"Oi {args['name']}, {args['age']} anos!"}]}
```

**Opção 2: JSON Schema completo**
```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Nome do usuário"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150}
    },
    "required": ["name"]
}

@tool("greet_v2", "Cumprimentar com validação", schema)
async def greet_v2(args):
    # ...
```

**Opção 3: TypedDict** (type-safe)
```python
from typing import TypedDict

class GreetInput(TypedDict):
    name: str
    age: int

@tool("greet_v3", "Cumprimentar type-safe", GreetInput)
async def greet_v3(args: GreetInput):
    # args tem tipos!
    return {"content": [{"type": "text", "text": f"Oi {args['name']}!"}]}
```

### **3. Return Format**

**Sucesso:**
```python
return {
    "content": [
        {"type": "text", "text": "Resultado aqui"}
    ]
}
```

**Erro:**
```python
return {
    "content": [
        {"type": "text", "text": "Erro: divisão por zero"}
    ],
    "is_error": True  # Marca como erro
}
```

**Múltiplos content blocks:**
```python
return {
    "content": [
        {"type": "text", "text": "Primeiro bloco"},
        {"type": "text", "text": "Segundo bloco"},
    ]
}
```

## Criar Servidor MCP

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

# Definir tools
@tool("add", "Somar números", {"a": float, "b": float})
async def add(args):
    result = args["a"] + args["b"]
    return {"content": [{"type": "text", "text": f"Soma: {result}"}]}

@tool("multiply", "Multiplicar", {"a": float, "b": float})
async def multiply(args):
    result = args["a"] * args["b"]
    return {"content": [{"type": "text", "text": f"Produto: {result}"}]}

# Criar servidor
calculator = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[add, multiply]
)
```

## Usar Tools com Claude

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Configurar
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},     # Registrar servidor
    allowed_tools=["add", "multiply"],    # Permitir tools
)

# Usar
async with ClaudeSDKClient(options=options) as client:
    await client.query("Quanto é 5 + 3?")

    async for msg in client.receive_response():
        print(msg)  # Claude usará a tool "add" automaticamente
```

## Exemplos Completos

### **Exemplo 1: Calculadora Científica**

```python
import math
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("sqrt", "Raiz quadrada", {"number": float})
async def sqrt_tool(args):
    if args["number"] < 0:
        return {
            "content": [{"type": "text", "text": "Erro: número negativo"}],
            "is_error": True
        }

    result = math.sqrt(args["number"])
    return {"content": [{"type": "text", "text": f"√{args['number']} = {result}"}]}

@tool("sin", "Seno de um ângulo em radianos", {"radians": float})
async def sin_tool(args):
    result = math.sin(args["radians"])
    return {"content": [{"type": "text", "text": f"sin({args['radians']}) = {result:.4f}"}]}

# Criar servidor
math_server = create_sdk_mcp_server(
    name="math",
    version="1.0.0",
    tools=[sqrt_tool, sin_tool]
)
```

### **Exemplo 2: Database Tool**

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

# Estado da aplicação (in-memory database)
users_db = []

@tool("add_user", "Adicionar usuário ao DB", {"name": str, "email": str})
async def add_user(args):
    user = {"id": len(users_db) + 1, "name": args["name"], "email": args["email"]}
    users_db.append(user)

    return {"content": [{"type": "text", "text": f"Usuário #{user['id']} criado"}]}

@tool("list_users", "Listar todos usuários", {})
async def list_users(args):
    if not users_db:
        return {"content": [{"type": "text", "text": "Nenhum usuário cadastrado"}]}

    user_list = "\n".join([f"{u['id']}: {u['name']} ({u['email']})" for u in users_db])
    return {"content": [{"type": "text", "text": f"Usuários:\n{user_list}"}]}

@tool("search_user", "Buscar usuário por nome", {"query": str})
async def search_user(args):
    query = args["query"].lower()
    results = [u for u in users_db if query in u["name"].lower()]

    if not results:
        return {"content": [{"type": "text", "text": "Nenhum resultado"}]}

    user_list = "\n".join([f"{u['id']}: {u['name']} ({u['email']})" for u in results])
    return {"content": [{"type": "text", "text": f"Encontrados:\n{user_list}"}]}

# Criar servidor
db_server = create_sdk_mcp_server(
    name="userdb",
    version="1.0.0",
    tools=[add_user, list_users, search_user]
)

# Usar
options = ClaudeAgentOptions(
    mcp_servers={"db": db_server},
    allowed_tools=["add_user", "list_users", "search_user"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Adicione um usuário chamado João com email joao@example.com")
    # Claude usará add_user automaticamente

    await client.query("Liste todos os usuários")
    # Claude usará list_users
```

### **Exemplo 3: Web Scraper Tool**

```python
import httpx
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("fetch_url", "Buscar conteúdo de URL", {"url": str})
async def fetch_url(args):
    """Busca HTML de uma URL."""
    url = args["url"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()

            content = response.text[:5000]  # Limitar a 5000 chars

            return {
                "content": [
                    {"type": "text", "text": f"URL: {url}\n\nConteúdo:\n{content}"}
                ]
            }

    except httpx.HTTPError as e:
        return {
            "content": [{"type": "text", "text": f"Erro HTTP: {str(e)}"}],
            "is_error": True
        }

@tool("extract_links", "Extrair links de HTML", {"html": str})
async def extract_links(args):
    """Extrai links de HTML."""
    import re

    html = args["html"]
    links = re.findall(r'href=["\']([^"\']+)["\']', html)

    links_text = "\n".join(links[:20])  # Primeiros 20 links

    return {"content": [{"type": "text", "text": f"Links encontrados:\n{links_text}"}]}

# Criar servidor
web_server = create_sdk_mcp_server(
    name="web",
    version="1.0.0",
    tools=[fetch_url, extract_links]
)
```

## Acesso ao Estado da Aplicação

**Vantagem do SDK MCP:** Tools têm acesso direto ao estado do seu app!

```python
# Estado global da aplicação
class AppState:
    def __init__(self):
        self.data = {}
        self.counter = 0

app_state = AppState()

@tool("increment", "Incrementar contador", {})
async def increment(args):
    app_state.counter += 1
    return {"content": [{"type": "text", "text": f"Contador: {app_state.counter}"}]}

@tool("set_data", "Definir dados", {"key": str, "value": str})
async def set_data(args):
    app_state.data[args["key"]] = args["value"]
    return {"content": [{"type": "text", "text": f"Salvo: {args['key']} = {args['value']}"}]}

@tool("get_data", "Obter dados", {"key": str})
async def get_data(args):
    value = app_state.data.get(args["key"], "Não encontrado")
    return {"content": [{"type": "text", "text": f"{args['key']} = {value}"}]}

# Tools compartilham o mesmo app_state!
```

## Múltiplos Servidores

```python
# Criar vários servidores
calculator = create_sdk_mcp_server("calc", tools=[add, multiply])
database = create_sdk_mcp_server("db", tools=[add_user, list_users])
web = create_sdk_mcp_server("web", tools=[fetch_url])

# Usar todos
options = ClaudeAgentOptions(
    mcp_servers={
        "calc": calculator,
        "db": database,
        "web": web,
    },
    allowed_tools=[
        "add", "multiply",      # Do calculator
        "add_user", "list_users",  # Do database
        "fetch_url",            # Do web
    ],
)

async with ClaudeSDKClient(options=options) as client:
    # Claude pode usar TODAS as ferramentas
    await client.query("Adicione um usuário e depois calcule 5 + 3")
```

## Error Handling

```python
@tool("divide", "Dividir números", {"a": float, "b": float})
async def divide(args):
    """Divisão com error handling."""
    try:
        if args["b"] == 0:
            return {
                "content": [{"type": "text", "text": "❌ Erro: divisão por zero"}],
                "is_error": True
            }

        result = args["a"] / args["b"]
        return {"content": [{"type": "text", "text": f"Resultado: {result}"}]}

    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"❌ Erro inesperado: {str(e)}"}],
            "is_error": True
        }
```

## Best Practices

### ✅ **DO:**

1. **Sempre validar inputs:**
```python
@tool("get_user", "...", {"user_id": int})
async def get_user(args):
    user_id = args.get("user_id")

    if not user_id or user_id < 1:
        return {"content": [{"type": "text", "text": "ID inválido"}], "is_error": True}

    # Continuar...
```

2. **Limitar tamanho de outputs:**
```python
@tool("read_file", "...", {"path": str})
async def read_file(args):
    content = open(args["path"]).read()

    # Truncar se muito grande
    if len(content) > 10000:
        content = content[:10000] + "\n... (truncado)"

    return {"content": [{"type": "text", "text": content}]}
```

3. **Usar async quando fizer I/O:**
```python
@tool("fetch", "...", {"url": str})
async def fetch(args):
    async with httpx.AsyncClient() as client:
        response = await client.get(args["url"])  # Async I/O
        return {"content": [{"type": "text", "text": response.text}]}
```

### ❌ **DON'T:**

1. **Não bloquear com sync I/O:**
```python
# ❌ RUIM
@tool("bad_fetch", "...", {"url": str})
async def bad_fetch(args):
    import requests
    response = requests.get(args["url"])  # SYNC em função async!
    return {"content": [{"type": "text", "text": response.text}]}
```

2. **Não retornar objetos complexos:**
```python
# ❌ RUIM
@tool("get_user", "...", {"id": int})
async def get_user(args):
    user = User(id=args["id"], name="João")
    return {"content": user}  # Não é serializável!

# ✅ BOM
async def get_user(args):
    user = User(id=args["id"], name="João")
    return {"content": [{"type": "text", "text": f"User: {user.name}"}]}
```

3. **Não fazer operações muito longas:**
```python
# ❌ RUIM
@tool("process_big_data", "...", {})
async def process_big_data(args):
    # Processamento de 10 minutos
    await process_millions_of_records()  # Timeout!

# ✅ BOM
@tool("start_processing", "...", {})
async def start_processing(args):
    # Iniciar processamento em background
    asyncio.create_task(process_millions_of_records())
    return {"content": [{"type": "text", "text": "Processamento iniciado"}]}
```

## Exemplo Real: Neo4j Tool

```python
from claude_agent_sdk import tool, create_sdk_mcp_server
from neo4j import AsyncGraphDatabase

# Conexão global
driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

@tool("create_node", "Criar nó no Neo4j", {"label": str, "name": str})
async def create_node(args):
    """Cria nó no Neo4j."""
    async with driver.session() as session:
        result = await session.run(
            "CREATE (n:$label {name: $name}) RETURN id(n) as node_id",
            label=args["label"],
            name=args["name"]
        )
        record = await result.single()
        node_id = record["node_id"]

        return {"content": [{"type": "text", "text": f"Nó criado: ID {node_id}"}]}

@tool("search_nodes", "Buscar nós", {"query": str})
async def search_nodes(args):
    """Busca nós no Neo4j."""
    async with driver.session() as session:
        result = await session.run(
            "MATCH (n) WHERE n.name CONTAINS $query RETURN n.name as name LIMIT 10",
            query=args["query"]
        )

        nodes = []
        async for record in result:
            nodes.append(record["name"])

        if not nodes:
            return {"content": [{"type": "text", "text": "Nenhum resultado"}]}

        return {"content": [{"type": "text", "text": "\n".join(nodes)}]}

# Servidor
neo4j_server = create_sdk_mcp_server(
    name="neo4j",
    version="1.0.0",
    tools=[create_node, search_nodes]
)

# Usar
options = ClaudeAgentOptions(
    mcp_servers={"neo4j": neo4j_server},
    allowed_tools=["create_node", "search_nodes"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Crie um nó chamado 'Claude SDK' e busque por 'SDK'")
    # Claude usará as tools automaticamente!
```

## Vantagens vs MCP Servers Externos

| Aspecto | SDK MCP (in-process) | Servidor MCP Externo |
|---------|----------------------|----------------------|
| **Performance** | ⚡ Rápido (sem IPC) | Lento (subprocess + IPC) |
| **Deploy** | ✅ Simples (1 processo) | Complexo (2+ processos) |
| **Debug** | ✅ Fácil (mesmo processo) | Difícil (outro processo) |
| **Estado** | ✅ Acesso direto ao app | ❌ Precisa serializar |
| **Setup** | ✅ Apenas Python | Precisa configurar subprocess |

## Quando Usar SDK MCP vs Servidor Externo

### **Use SDK MCP (in-process) quando:**
- ✅ Tool é simples
- ✅ Precisa de acesso ao estado do app
- ✅ Quer deployment simplificado
- ✅ Performance é importante

### **Use Servidor Externo quando:**
- Tool precisa rodar em linguagem diferente
- Tool é fornecida por terceiros
- Quer isolamento de processo
- Tool já existe como servidor MCP

## Combinando SDK MCP com Servidores Externos

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

# Tool in-process
@tool("local_calc", "Calculadora local", {"a": float, "b": float})
async def local_calc(args):
    return {"content": [{"type": "text", "text": f"Soma: {args['a'] + args['b']}"}]}

local_server = create_sdk_mcp_server("local", tools=[local_calc])

# Configurar com ambos
options = ClaudeAgentOptions(
    mcp_servers={
        "local": local_server,  # In-process
        "external": {           # Servidor externo
            "type": "stdio",
            "command": "python",
            "args": ["external_server.py"]
        }
    },
    allowed_tools=["local_calc", "external_tool"],
)
```

## Debugging de Tools

### **Log de chamadas:**

```python
@tool("debug_tool", "Tool com debug", {"input": str})
async def debug_tool(args):
    print(f"🔍 Tool chamada com: {args}")

    result = args["input"].upper()

    print(f"🔍 Tool retornando: {result}")

    return {"content": [{"type": "text", "text": result}]}
```

### **Inspect do schema:**

```python
# Ver schema gerado
from mcp.server import Server

server = Server("test")

@tool("test", "Test tool", {"a": float, "b": str})
async def test_tool(args):
    return {"content": [{"type": "text", "text": "ok"}]}

# Schema gerado automaticamente
print(test_tool.input_schema)
# {'a': <class 'float'>, 'b': <class 'str'>}
```

## Ver Também

- `01_CONCEITOS_FUNDAMENTAIS.md` - Introdução
- `02_CLAUDESDKCLIENT_COMPLETO.md` - API do cliente
- `06_PADROES_USO.md` - Padrões com tools
- `07_TROUBLESHOOTING.md` - Problemas comuns
