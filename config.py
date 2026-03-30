"""Agent and model configuration."""

from agentscope.formatter import OpenAIChatFormatter
from agentscope.model import OpenAIChatModel
from agentscope.tool import Toolkit

from tools.robot_arm import get_workspace_status, move_object

API_BASE = "http://localhost:8000/v1"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct-AWQ"

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


def create_toolkit() -> Toolkit:
    toolkit = Toolkit()
    toolkit.register_tool_function(move_object)
    toolkit.register_tool_function(get_workspace_status)
    return toolkit
