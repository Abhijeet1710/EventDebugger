import asyncio

from dotenv import load_dotenv

load_dotenv()

from ai_app.agents.investigation import (
    create_investigation_agent,
    format_investigation_result,
)


async def main():

    print("\n" + "=" * 60)
    print("AI PRODUCTION DEBUGGER")
    print("=" * 60)

    # Get query from user
    user_query = input(
        "\nEnter your investigation query along with service name:\n> "
    )

    if not user_query.strip():
        print("No query provided. Exiting.")
        return

    print("\n[1] Creating investigation agent...")

    agent = await create_investigation_agent()

    print("[1] Investigation agent created successfully")

    print("\n[2] Starting investigation...")

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query,
                }
            ]
        }
    )

    print("[2] Investigation completed")

    investigation = result["messages"][-1].content

    # print("\n" + "-" * 60)
    # print("RAW INVESTIGATION RESULT")
    # print("-" * 60)

    # print(investigation)

    print("\n[3] Formatting investigation result...")

    structured_result = await format_investigation_result(
        investigation
    )

    print("[3] Formatting completed")

    print("\n" + "=" * 60)
    print("STRUCTURED INVESTIGATION RESULT")
    print("=" * 60)

    print(structured_result.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("INVESTIGATION FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())