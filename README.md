# Robot Arm Agent

Agente de IA en lenguaje natural que controla un brazo robot mediante un servidor MCP. Construido con [AgentScope v1.0.18](https://github.com/agentscope-ai/agentscope) y un LLM local servido por vLLM.

## Arquitectura

```
Usuario (lenguaje natural)
        │
        ▼
  ReActAgent (AgentScope)          ◄──► ReMe (memoria persistente)
        │
        │  MCP (streamable HTTP)
        ▼
  MCP Server (localhost:8001)
        │
        ├── move_object()          ──► _send_to_arm() [MOCK → SDK real]
        └── get_workspace_status() ──► _send_to_arm() [MOCK → SDK real]

  AgentScope Studio (localhost:3000) ◄── trazas en tiempo real
```

El agente usa un loop **ReAct** (Reason + Act): razona sobre la instrucción, decide qué herramienta usar, la invoca vía MCP, y responde con el resultado. Entre sesiones, **ReMe** persiste el historial en disco y lo recupera como contexto.

## Estructura del proyecto

```
agente-personal/
├── main.py               # Entry point — loop interactivo async
├── config.py             # Modelo, formatter, toolkit (MCP) y memoria
├── reme_memory.py        # Adapter ReMeLight ↔ AgentScope LongTermMemoryBase
├── mcp_server/
│   └── server.py         # Servidor FastMCP con las tools del brazo
│                         #   └── _send_to_arm() ← reemplazar con SDK real
└── tools/
    └── robot_arm.py      # (legacy, reemplazado por MCP)
```

## Requisitos

- Python 3.12+
- Node.js 20+
- GPU con VRAM suficiente para el modelo (Qwen2.5-7B-AWQ requiere ~6GB)
- [vLLM](https://docs.vllm.ai/)
- [AgentScope](https://github.com/agentscope-ai/agentscope) v1.0.18
- [AgentScope Studio](https://github.com/agentscope-ai/agentscope-studio)

## Instalación

```bash
# Dependencias Python
python3 -m venv venv_ai
source venv_ai/bin/activate
pip install agentscope vllm reme-ai

# AgentScope Studio (requiere Node.js 20+)
sudo npm install -g @agentscope/studio
```

## Uso

Correr los cuatro servicios en terminales separadas:

### Terminal 1 — AgentScope Studio (dashboard)

```bash
as_studio
```

Abre el dashboard en `http://localhost:3000`. Muestra las trazas del agente, tool calls y mensajes en tiempo real bajo el proyecto **RobotArmAgent**.

### Terminal 2 — Servidor LLM

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

### Terminal 3 — MCP Server

```bash
source venv_ai/bin/activate
python3 mcp_server/server.py
```

Expone las tools del brazo robot en `http://localhost:8001/mcp`. El agente carga las tools dinámicamente desde este servidor al arrancar.

### Terminal 4 — Agente

```bash
source venv_ai/bin/activate
python3 main.py
```

### Ejemplos de instrucciones

```
mové la lapicera 5cm a la izquierda
cuántos objetos hay en el espacio de trabajo?
mové la taza 10cm hacia adelante
qué moviste en la sesión anterior?
```

## Herramientas disponibles (MCP)

| Herramienta | Descripción |
|---|---|
| `move_object(object_name, direction, distance_cm)` | Mueve un objeto en la dirección indicada |
| `get_workspace_status()` | Devuelve la posición actual de todos los objetos |

**Direcciones válidas:** `izquierda`, `derecha`, `adelante`, `atras`, `arriba`, `abajo`

**Objetos disponibles (mock):** `lapicera`, `taza`, `cuaderno`

## Memoria persistente (ReMe)

El agente recuerda acciones de sesiones anteriores gracias a **ReMe**. Los datos se almacenan en `.reme/`:

```
.reme/
├── MEMORY.md          # Resumen de largo plazo
├── memory/            # Diarios por fecha
└── dialog/            # Conversaciones en JSONL
```

El agente puede usar dos tools de memoria autónomamente:
- `retrieve_from_memory` — busca contexto relevante por keywords
- `record_to_memory` — guarda información importante para el futuro

## Configuración

Editá `config.py` para cambiar:

- `API_BASE` — URL del servidor vLLM
- `MODEL_NAME` — nombre del modelo
- `MCP_URL` — URL del servidor MCP
- `SYSTEM_PROMPT` — comportamiento del agente

## Integrar el SDK del brazo real

La función `_send_to_arm()` en `mcp_server/server.py` es el único punto de integración con el hardware. Reemplazá su cuerpo con las llamadas al SDK real:

```python
def _send_to_arm(command: dict) -> dict:
    from robot_sdk import ArmController
    arm = ArmController()
    return arm.execute(command)
```

El resto del sistema (agente, MCP, memoria) no requiere cambios.

## Ecosistema AgentScope

| Herramienta | Descripción | Instalación |
|---|---|---|
| **AgentScope** | Framework core multi-agente | `pip install agentscope` |
| **AgentScope Studio** | Dashboard visual con trazas y chat en tiempo real | `sudo npm install -g @agentscope/studio` |
| **AgentScope Samples** | Ejemplos listos para usar | `git clone github.com/agentscope-ai/agentscope-samples` |
| **AgentScope Runtime** | Runtime de producción con sandboxing y APIs cloud | `pip install agentscope-runtime` |
| **ReMe** | Memoria persistente (archivos + vectores) con búsqueda híbrida | `pip install reme-ai` |
| **CoPaw** | Asistente personal con integración a Slack, Discord, DingTalk, etc. | `git clone github.com/agentscope-ai/CoPaw` |
| **Trinity-RFT** | Framework para fine-tuning por refuerzo (RFT) de LLMs | `git clone github.com/agentscope-ai/Trinity-RFT` |
| **AgentScope Java** | Implementación Java del framework para entornos enterprise | Maven/Gradle |

**Integraciones built-in en AgentScope:**
- **MCP** — Clientes HTTP y StdIO para conectar con cualquier servidor MCP
- **A2A Protocol** — Comunicación interoperable entre agentes (Agent-to-Agent)
- **RAG** — Retrieval-Augmented Generation con soporte para RAGFlow y Dify
- **OpenTelemetry** — Trazas compatibles con Arize Phoenix, Langfuse, etc.
- **Evaluación** — RayEvaluator (paralelo) y GeneralEvaluator para benchmark de agentes

Documentación oficial: [doc.agentscope.io](https://doc.agentscope.io)
