"""MCP server for robot arm control.

Exposes two tools via the Model Context Protocol:
- move_object: pick up an object and move it in a direction
- get_workspace_status: query the current position of all objects

The hardware interface (_send_to_arm) is mocked until the physical
robot arm SDK is integrated.

Run with:
    python3 mcp_server/server.py
"""

import logging
import random

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

MCP_HOST = "127.0.0.1"
MCP_PORT = 8001

# ---------------------------------------------------------------------------
# Simulated workspace state (replaced by hardware SDK state in production)
# ---------------------------------------------------------------------------

_workspace: dict[str, dict[str, float]] = {
    "lapicera": {"x": 10.0, "y": 5.0, "z": 0.0},
    "taza": {"x": 25.0, "y": 10.0, "z": 0.0},
    "cuaderno": {"x": 40.0, "y": 15.0, "z": 0.0},
}

_DIRECTION_MAP: dict[str, tuple[str, int]] = {
    "izquierda": ("x", -1),
    "derecha": ("x", 1),
    "adelante": ("y", 1),
    "atras": ("y", -1),
    "arriba": ("z", 1),
    "abajo": ("z", -1),
}

# ---------------------------------------------------------------------------
# Hardware interface (MOCKED — replace with real SDK calls)
# ---------------------------------------------------------------------------


def _send_to_arm(command: dict) -> dict:
    """Send a command to the physical robot arm.

    TODO: Replace this mock with the actual robot arm SDK call, e.g.:
        from robot_sdk import ArmController
        arm = ArmController()
        return arm.execute(command)

    Args:
        command: Dict with keys 'action', 'object', 'axis', 'delta_cm'.

    Returns:
        Dict with 'success' bool and 'grip_force' float.
    """
    logger.info("MOCK arm command: %s", command)
    return {
        "success": True,
        "grip_force": round(random.uniform(0.5, 2.0), 2),
    }


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="RobotArmServer",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
)


@mcp.tool()
def move_object(object_name: str, direction: str, distance_cm: float) -> str:
    """Move an object in the workspace using the robot arm.

    Args:
        object_name: The name of the object to move
            (e.g. "lapicera", "taza", "cuaderno").
        direction: The direction to move the object.
            One of: izquierda, derecha, adelante, atras, arriba, abajo.
        distance_cm: The distance in centimeters to move the object
            (between 0.1 and 50).

    Returns:
        A string describing the result of the operation.
    """
    object_key = object_name.lower().strip()
    if object_key not in _workspace:
        available = ", ".join(_workspace.keys())
        return (
            f"Error: objeto '{object_name}' no encontrado. "
            f"Disponibles: {available}"
        )

    dir_key = direction.lower().strip()
    if dir_key not in _DIRECTION_MAP:
        valid = ", ".join(_DIRECTION_MAP.keys())
        return f"Error: direccion '{direction}' no valida. Validas: {valid}"

    if not (0 < distance_cm <= 50):
        return (
            f"Error: distancia {distance_cm}cm fuera de rango "
            f"(debe ser entre 0.1 y 50 cm)."
        )

    axis, sign = _DIRECTION_MAP[dir_key]
    old_pos = _workspace[object_key].copy()

    result = _send_to_arm({
        "action": "move",
        "object": object_key,
        "axis": axis,
        "delta_cm": sign * distance_cm,
    })

    if not result["success"]:
        return f"Error: el brazo no pudo completar el movimiento."

    _workspace[object_key][axis] += sign * distance_cm
    new_pos = _workspace[object_key]

    return (
        f"Operacion exitosa. '{object_name}' movido {distance_cm}cm "
        f"hacia {direction}.\n"
        f"Posicion anterior: x={old_pos['x']:.1f}, "
        f"y={old_pos['y']:.1f}, z={old_pos['z']:.1f}\n"
        f"Posicion actual:   x={new_pos['x']:.1f}, "
        f"y={new_pos['y']:.1f}, z={new_pos['z']:.1f}\n"
        f"Fuerza de agarre: {result['grip_force']}N"
    )


@mcp.tool()
def get_workspace_status() -> str:
    """Get the current position of all objects in the workspace.

    Returns:
        A string listing every object and its current coordinates.
    """
    if not _workspace:
        return "El espacio de trabajo esta vacio."

    lines = ["Estado actual del espacio de trabajo:"]
    for name, pos in _workspace.items():
        lines.append(
            f"  - {name}: x={pos['x']:.1f}cm, "
            f"y={pos['y']:.1f}cm, z={pos['z']:.1f}cm"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"Iniciando MCP server en http://{MCP_HOST}:{MCP_PORT}/mcp")
    mcp.run(transport="streamable-http")
