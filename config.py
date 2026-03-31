"""Agent and model configuration."""

from agentscope.formatter import OpenAIChatFormatter
from agentscope.mcp import HttpStatelessClient
from agentscope.model import OpenAIChatModel
from agentscope.tool import Toolkit
from reme.reme_light import ReMeLight

from reme_memory import ReMeLongTermMemory

API_BASE = "http://localhost:8000/v1"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct-AWQ"
REME_WORKING_DIR = ".reme"
MCP_URL = "http://localhost:8001/mcp"

# Comando para iniciar vLLM con soporte de tool calls:
# python3 -m vllm.entrypoints.openai.api_server \
#   --model Qwen/Qwen2.5-7B-Instruct-AWQ \
#   --quantization awq \
#   --gpu-memory-utilization 0.85 \
#   --max-model-len 4096 \
#   --max-num-seqs 16 \
#   --enforce-eager \
#   --enable-auto-tool-choice \
#   --tool-call-parser hermes

SYSTEM_PROMPT = """\
Sos un operador de brazo robotico. Tu trabajo es interpretar instrucciones \
del usuario en lenguaje natural y usar tus herramientas para controlar el \
brazo robot.

Reglas:
- Siempre consulta el estado del espacio de trabajo antes de mover algo \
si no estas seguro de que objetos hay disponibles.
- Confirma la operacion al usuario despues de ejecutarla.
- Si la instruccion es ambigua, pedi aclaracion.
- Responde siempre en español.
"""


def create_model() -> OpenAIChatModel:
    return OpenAIChatModel(
        model_name=MODEL_NAME,
        api_key="not-needed",
        client_kwargs={"base_url": API_BASE},
    )


def create_formatter() -> OpenAIChatFormatter:
    return OpenAIChatFormatter()


async def create_toolkit() -> Toolkit:
    """Create the agent toolkit by loading tools from the MCP server."""
    toolkit = Toolkit()
    mcp_client = HttpStatelessClient(
        name="RobotArmServer",
        transport="streamable_http",
        url=MCP_URL,
    )
    await toolkit.register_mcp_client(mcp_client)
    return toolkit


def create_long_term_memory() -> tuple[ReMeLight, ReMeLongTermMemory]:
    """Create ReMe persistent memory backed by the local LLM."""
    reme = ReMeLight(
        working_dir=REME_WORKING_DIR,
        llm_api_key="not-needed",
        llm_base_url=API_BASE,
        default_as_llm_config={
            "model_name": MODEL_NAME,
            "api_key": "not-needed",
            "client_kwargs": {"base_url": API_BASE},
        },
        default_file_store_config={
            "fts_enabled": True,
            "vector_enabled": False,
        },
        enable_load_env=False,
    )
    return reme, ReMeLongTermMemory(reme)
