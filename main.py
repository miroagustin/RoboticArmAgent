"""Robot arm agent — controls a robot arm via natural language."""

import asyncio

import agentscope
from agentscope.agent import ReActAgent, UserAgent

from config import (
    SYSTEM_PROMPT,
    create_formatter,
    create_long_term_memory,
    create_model,
    create_toolkit,
)


async def main() -> None:
    studio_url = "http://localhost:3000"
    try:
        agentscope.init(
            project="RobotArmAgent",
            name="robot-arm-session",
            studio_url=studio_url,
            logging_path="logs/agentscope.log",
        )
        print(f"AgentScope Studio conectado en {studio_url}")
    except Exception:
        agentscope.init(
            project="RobotArmAgent",
            name="robot-arm-session",
            logging_path="logs/agentscope.log",
        )
        print("AgentScope Studio no disponible, corriendo sin dashboard.")

    reme, long_term_memory = create_long_term_memory()
    await reme.start()

    try:
        agent = ReActAgent(
            name="RobotOperator",
            sys_prompt=SYSTEM_PROMPT,
            model=create_model(),
            formatter=create_formatter(),
            toolkit=await create_toolkit(),
            long_term_memory=long_term_memory,
            long_term_memory_mode="agent_control",
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
    finally:
        try:
            await reme.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
