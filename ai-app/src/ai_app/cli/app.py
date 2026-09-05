import asyncio

import typer
from dotenv import load_dotenv

load_dotenv()

from ai_app.agents.investigation import (
    create_investigation_agent,
    format_investigation_result,
)

app = typer.Typer(
    name="ai-debug",
    help="AI Production Debugger",
    add_completion=False,
)


def print_header() -> None:
    print()
    print("=" * 60)
    print("              AI PRODUCTION DEBUGGER")
    print("=" * 60)


def print_timeline(result) -> None:
    print()
    print("-" * 60)
    print("PROCESSING TIMELINE")
    print("-" * 60)

    for item in result.timeline:
        if item.type == "ERROR":
            symbol = "✗"
        elif item.status == "SUCCESS":
            symbol = "✓"
        elif item.status == "FILTERED_OUT":
            symbol = "✗"
        elif item.status == "NOT_REACHED":
            symbol = "○"
        elif item.status == "FAILED":
            symbol = "✗"
        else:
            symbol = "?"

        timestamp = item.timestamp or "--"

        print(
            f"{symbol} "
            f"{item.name:<25} "
            f"{item.status:<15} "
            f"{timestamp}"
        )


def print_details(result) -> None:
    print()
    print("-" * 60)
    print("INVESTIGATION")
    print("-" * 60)

    print(f"Event ID : {result.event_id}")
    print(f"Service  : {result.service}")
    print(f"Status   : {result.overall_status}")

    print()
    print("Summary:")
    print(result.summary)

    print()
    print("Query:")
    print(result.query)


def print_evidence(result) -> None:
    print()
    print("-" * 60)
    print("EVIDENCE")
    print("-" * 60)

    for item in result.timeline:
        if not item.evidence:
            continue

        print()
        print(f"[{item.name}]")

        if item.timestamp:
            print(f"Timestamp: {item.timestamp}")

        print(f"Evidence : {item.evidence}")

        if item.description:
            print(f"Details  : {item.description}")


async def investigate(user_query: str) -> None:
    print()
    print("Investigating...")

    agent = await create_investigation_agent()

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

    investigation = result["messages"][-1].content

    structured_result = await format_investigation_result(
        investigation
    )

    print_details(structured_result)
    print_timeline(structured_result)
    print_evidence(structured_result)

    print()
    print("=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)
    print()


@app.command()
def run(
    query: str | None = typer.Argument(
        None,
        help="Investigation query.",
    )
) -> None:
    """
    Investigate a production event using natural language.
    """

    print_header()

    if query:
        user_query = query
    else:
        user_query = typer.prompt(
            "What would you like to investigate?"
        )

    if not user_query.strip():
        typer.echo("No investigation query provided.")
        raise typer.Exit(code=1)

    try:
        asyncio.run(investigate(user_query))

    except KeyboardInterrupt:
        print()
        print("Investigation cancelled.")

    except Exception as exc:
        print()
        print("=" * 60)
        print("INVESTIGATION FAILED")
        print("=" * 60)
        print()
        print(f"Error: {exc}")
        print()

        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()