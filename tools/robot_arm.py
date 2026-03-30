"""Mocked robot arm tools that simulate MCP server calls.

These tools will eventually call a real MCP server that controls
a physical robot arm. For now, they simulate the operations and
return realistic responses.
"""

import logging
import random

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

logger = logging.getLogger(__name__)

# Simulated workspace state
_workspace: dict[str, dict[str, float]] = {
    "lapicera": {"x": 10.0, "y": 5.0, "z": 0.0},
    "taza": {"x": 25.0, "y": 10.0, "z": 0.0},
    "cuaderno": {"x": 40.0, "y": 15.0, "z": 0.0},
}


def move_object(
    object_name: str,
    direction: str,
    distance_cm: float,
) -> ToolResponse:
    """Move an object in the workspace using the robot arm.

    This tool instructs the robot arm to pick up an object and
    move it in the specified direction by a given distance.

    Args:
        object_name (str): The name of the object to move
            (e.g. "lapicera", "taza", "cuaderno").
        direction (str): The direction to move the object.
            One of: "izquierda", "derecha", "adelante", "atras",
            "arriba", "abajo".
        distance_cm (float): The distance in centimeters to move
            the object.

    Returns:
        ToolResponse: The result of the robot arm operation.
    """
    object_key = object_name.lower().strip()

    if object_key not in _workspace:
        return ToolResponse(content=[TextBlock(
            type="text",
            text=f"Error: objeto '{object_name}' no encontrado en el "
                 f"espacio de trabajo. Objetos disponibles: "
                 f"{', '.join(_workspace.keys())}",
        )])

    direction_map = {
        "izquierda": ("x", -1),
        "derecha": ("x", 1),
        "adelante": ("y", 1),
        "atras": ("y", -1),
        "arriba": ("z", 1),
        "abajo": ("z", -1),
    }

    dir_key = direction.lower().strip()
    if dir_key not in direction_map:
        return ToolResponse(content=[TextBlock(
            type="text",
            text=f"Error: direccion '{direction}' no valida. "
                 f"Direcciones validas: {', '.join(direction_map.keys())}",
        )])

    if distance_cm <= 0 or distance_cm > 50:
        return ToolResponse(content=[TextBlock(
            type="text",
            text=f"Error: distancia {distance_cm}cm fuera de rango. "
                 f"Debe ser entre 0.1 y 50 cm.",
        )])

    axis, sign = direction_map[dir_key]
    old_pos = _workspace[object_key].copy()
    _workspace[object_key][axis] += sign * distance_cm
    new_pos = _workspace[object_key]

    # Simulate occasional arm feedback
    grip_force = round(random.uniform(0.5, 2.0), 2)

    logger.info(
        "MCP mock: moved '%s' %s %.1fcm | %s -> %s",
        object_name, direction, distance_cm, old_pos, new_pos,
    )

    return ToolResponse(content=[TextBlock(
        type="text",
        text=(
            f"Operacion exitosa. "
            f"Objeto '{object_name}' movido {distance_cm}cm "
            f"hacia {direction}.\n"
            f"Posicion anterior: x={old_pos['x']:.1f}, "
            f"y={old_pos['y']:.1f}, z={old_pos['z']:.1f}\n"
            f"Posicion actual: x={new_pos['x']:.1f}, "
            f"y={new_pos['y']:.1f}, z={new_pos['z']:.1f}\n"
            f"Fuerza de agarre: {grip_force}N"
        ),
    )])


def get_workspace_status() -> ToolResponse:
    """Get the current status of all objects in the workspace.

    Returns the position of every object the robot arm can interact with.

    Returns:
        ToolResponse: A description of all objects and their positions.
    """
    if not _workspace:
        return ToolResponse(content=[TextBlock(
            type="text",
            text="El espacio de trabajo esta vacio.",
        )])

    lines = ["Estado actual del espacio de trabajo:"]
    for name, pos in _workspace.items():
        lines.append(
            f"  - {name}: x={pos['x']:.1f}cm, "
            f"y={pos['y']:.1f}cm, z={pos['z']:.1f}cm"
        )

    return ToolResponse(content=[TextBlock(
        type="text",
        text="\n".join(lines),
    )])
