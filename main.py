"""Robot arm agent — controls a robot arm via natural language."""

import asyncio

import agentscope
from agentscope.agent import ReActAgent, UserAgent
from agentscope.message import Msg

from config import (
    SYSTEM_PROMPT,
    create_formatter,
    create_model,
    create_toolkit,
)


async def main() -> None:
    agentscope.init()

    agent = ReActAgent(
        name="RobotOperator",
        sys_prompt=SYSTEM_PROMPT,
        model=create_model(),
        formatter=create_formatter(),
        toolkit=create_toolkit(),
        max_iters=5,
    )

    user = UserAgent(name="User")

    print("=== Robot Arm Agent ===")
    print("Escribi instrucciones para el brazo robot.")
    print("Ejemplo: 'mové la lapicera 5cm a la izquierda'")
    print("Escribi 'salir' para terminar.\n")

    msg = None
    while True:
        msg = await user(msg)
        if msg.get_text_content().strip().lower() in ("salir", "exit", "quit"):
            print("Chau!")
            break
        msg = await agent(msg)


if __name__ == "__main__":
    asyncio.run(main())
