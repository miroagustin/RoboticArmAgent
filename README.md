# Robot Arm Agent

Agente de IA en lenguaje natural que controla un brazo robot mediante un servidor MCP. Construido con [AgentScope v1.0.18](https://github.com/modelscope/agentscope) y un LLM local servido por vLLM.

## Arquitectura

```
Usuario (lenguaje natural)
        │
        ▼
  ReActAgent (AgentScope)
        │
        ├── move_object()          ──► MCP Server (mock → brazo físico)
        └── get_workspace_status() ──► MCP Server (mock → brazo físico)
```

El agente usa un loop **ReAct** (Reason + Act): razona sobre la instrucción del usuario, decide qué herramienta usar, la ejecuta, y responde con el resultado.

## Estructura del proyecto

```
agente-personal/
├── main.py           # Entry point — loop interactivo async
├── config.py         # Modelo, formatter y toolkit
└── tools/
    ├── __init__.py
    └── robot_arm.py  # Tools del brazo (mockeadas, reemplazar con MCP real)
```

## Requisitos

- Python 3.12+
- GPU con VRAM suficiente para el modelo (Qwen2.5-7B-AWQ requiere ~6GB)
- [vLLM](https://docs.vllm.ai/)
- [AgentScope](https://github.com/modelscope/agentscope) v1.0.18

## Instalación

```bash
python3 -m venv venv_ai
source venv_ai/bin/activate
pip install agentscope ollama vllm
```

## Uso

### 1. Iniciar el servidor LLM

```bash
python3 -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct-AWQ \
  --quantization awq \
  --gpu-memory-utilization 0.85 \
  --max-model-len 4096 \
  --max-num-seqs 16 \
  --enforce-eager \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

> Los flags `--enable-auto-tool-choice` y `--tool-call-parser hermes` son **obligatorios** para que el agente pueda usar herramientas.

### 2. Correr el agente

```bash
source venv_ai/bin/activate
python3 main.py
```

### Ejemplos de instrucciones

```
mové la lapicera 5cm a la izquierda
cuántos objetos hay en el espacio de trabajo?
mové la taza 10cm hacia adelante
```

## Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `move_object(object_name, direction, distance_cm)` | Mueve un objeto en la dirección indicada |
| `get_workspace_status()` | Devuelve la posición actual de todos los objetos |

**Direcciones válidas:** `izquierda`, `derecha`, `adelante`, `atras`, `arriba`, `abajo`

**Objetos disponibles (mock):** `lapicera`, `taza`, `cuaderno`

## Configuración

Editá `config.py` para cambiar:

- `API_BASE` — URL del servidor vLLM
- `MODEL_NAME` — nombre del modelo
- `SYSTEM_PROMPT` — comportamiento del agente

## Integración con MCP real

Las tools en `tools/robot_arm.py` están mockeadas. Para conectar con un servidor MCP real, reemplazar el cuerpo de `move_object` y `get_workspace_status` con llamadas al cliente MCP:

```python
from agentscope.mcp import HttpStatelessClient

mcp_client = HttpStatelessClient(base_url="http://your-mcp-server")
toolkit.register_mcp_client(mcp_client)
```
