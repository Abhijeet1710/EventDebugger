import asyncio

from dotenv import load_dotenv

load_dotenv()

from ai_app.agents.investigation import (
    create_investigation_agent,
    format_investigation_result,
)


async def main():

    agent = await create_investigation_agent()

    print("\n")
    print("=" * 60)
    print("STARTING INVESTIGATION")
    print("=" * 60)

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Investigate event evt-12345 for the "
                        "ingestion-service. Tell me what happened "
                        "to this event."
                    ),
                }
            ]
        }
    )

    investigation = result["messages"][-1].content

    structured_result = await format_investigation_result(
        investigation
    )

    print("\n")
    print("=" * 60)
    print("STRUCTURED INVESTIGATION RESULT")
    print("=" * 60)

    print(
        structured_result.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    asyncio.run(main())