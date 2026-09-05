import asyncio

import typer
from dotenv import load_dotenv
from InquirerPy import inquirer
from rich.console import Console
from rich.text import Text

load_dotenv()

from ai_app.agents.investigation import (
    create_investigation_agent,
    format_investigation_result,
)
from ai_app.config.services import SERVICE_CONFIGS


app = typer.Typer(
    name="ai-debug",
    help="AI Production Debugger",
    add_completion=False,
)

console = Console()


# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------

def print_header() -> None:
    console.print()

    console.print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        style="dim",
    )

    console.print(
        " AI PRODUCTION DEBUGGER",
        style="bold",
    )

    console.print(
        " Production Event Investigation",
        style="dim",
    )

    console.print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        style="dim",
    )

    console.print()
    
    console.print(
        " Guide: Select a service, enter your investigation query, and explore the results.",
        style="bold",
    )

    console.print(
        " ↑/↓ Navigate   Enter Select   Ctrl+C Exit",
        style="dim",
    )

    console.print()


# -------------------------------------------------------------------
# Service selector
# -------------------------------------------------------------------

def select_service() -> str:

    services = list(SERVICE_CONFIGS.keys())

    if not services:
        console.print(
            "[bold red]No services are currently onboarded.[/bold red]"
        )
        raise typer.Exit(code=1)

    choices = [
        {
            "name": service,
            "value": service,
        }
        for service in services
    ]

    # console.print(
    #     " Select a service",
    #     style="bold",
    # )

    # console.print()

    return inquirer.select(
        message="",
        choices=choices,
        pointer="❯",
        qmark="",
        amark="",
    ).execute()


# -------------------------------------------------------------------
# Status helpers
# -------------------------------------------------------------------

def get_status_text(status: str) -> Text:

    if status == "SUCCESS":
        return Text("● SUCCESS", style="bold green")

    if status == "FAILED":
        return Text("● FAILED", style="bold red")

    if status == "NOT_FOUND":
        return Text("● NOT FOUND", style="bold yellow")

    return Text("● UNKNOWN", style="bold yellow")


def get_timeline_symbol(status: str) -> Text:

    if status == "SUCCESS":
        return Text("✓", style="green")

    if status in ("FAILED", "FILTERED_OUT"):
        return Text("✗", style="red")

    if status == "NOT_REACHED":
        return Text("○", style="yellow")

    return Text("?", style="yellow")


# -------------------------------------------------------------------
# Investigation summary
# -------------------------------------------------------------------

def print_summary(result) -> None:

    console.print(
        f" Event     [bold]{result.event_id}[/bold]"
    )

    console.print(
        f" Service   [bold]{result.service}[/bold]"
    )

    console.print(
        " Status    ",
        end="",
    )

    console.print(
        get_status_text(result.overall_status)
    )

    console.print()

    console.print(
        f" {result.summary}"
    )

    console.print()

# -------------------------------------------------------------------
# Investigation summary
# -------------------------------------------------------------------

def print_query(result) -> None:
    if not getattr(result, "query", None):
        return

    console.print(
        " INVESTIGATION QUERY",
        style="bold",
    )

    console.print()

    console.print(
        f" {result.query}",
        style="dim",
    )

    console.print()

# -------------------------------------------------------------------
# Timeline
# -------------------------------------------------------------------

def print_timeline(result) -> None:

    console.print(
        " PROCESSING TIMELINE",
        style="bold",
    )

    console.print()

    for index, item in enumerate(result.timeline):

        symbol = get_timeline_symbol(item.status)

        timestamp = item.timestamp or "--"

        if "T" in timestamp:
            timestamp = timestamp.replace("T", " ")

        console.print(
            f" {symbol}  "
            f"{item.name:<25} "
            f"{item.status:<15} "
            f"[dim]{timestamp}[/dim]"
        )

        if index < len(result.timeline) - 1:
            console.print(" │")


# -------------------------------------------------------------------
# Evidence
# -------------------------------------------------------------------

def show_evidence(item) -> None:

    console.clear()

    console.print()

    console.print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        style="dim",
    )

    console.print(
        f" {item.name}",
        style="bold",
    )

    console.print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        style="dim",
    )

    console.print()

    if item.timestamp:

        timestamp = item.timestamp.replace("T", " ")

        console.print(
            " Timestamp",
            style="bold",
        )

        console.print(
            f" {timestamp}"
        )

        console.print()

    if item.evidence:

        console.print(
            " Evidence",
            style="bold",
        )

        console.print(
            f" {item.evidence}"
        )

        console.print()

    if item.description:

        console.print(
            " Details",
            style="bold",
        )

        console.print(
            f" {item.description}"
        )

    console.print()

    console.print(
        " Press Enter to return to timeline",
        style="dim",
    )

    input()


# -------------------------------------------------------------------
# Interactive timeline
# -------------------------------------------------------------------

def interactive_timeline(result) -> None:

    choices = []

    for item in result.timeline:

        symbol = {
            "SUCCESS": "✓",
            "FAILED": "✗",
            "FILTERED_OUT": "✗",
            "NOT_REACHED": "○",
            "UNKNOWN": "?",
            "NOT_FOUND": "?",
        }.get(item.status, "?")

        choices.append(
            {
                "name": (
                    f"{symbol}  "
                    f"{item.name:<25} "
                    f"{item.status}"
                ),
                "value": item,
            }
        )

    choices.append(
        {
            "name": "←  I'm Good",
            "value": "__exit__",
        }
    )

    while True:

        console.print()

        try:

            selected = inquirer.select(
                message="",
                choices=choices,
                pointer="❯",
                qmark="",
                amark="",
            ).execute()

        except KeyboardInterrupt:
            console.clear()
            return

        if selected == "__exit__":
            console.clear()
            return

        show_evidence(selected)

        console.clear()

        console.clear()

        print_header()
        print_summary(result)
        print_query(result)
        print_timeline(result)


# -------------------------------------------------------------------
# Async investigation
# -------------------------------------------------------------------

async def run_investigation(
    service_name: str,
    user_query: str,
):

    agent = await create_investigation_agent()

    investigation_query = (
        f"Service: {service_name}\n"
        f"Investigation request: {user_query}"
    )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": investigation_query,
                }
            ]
        }
    )

    investigation = result["messages"][-1].content

    structured_result = await format_investigation_result(
        investigation
    )

    return structured_result


# -------------------------------------------------------------------
# Main investigation
# -------------------------------------------------------------------

def investigate(
    service_name: str,
    user_query: str,
) -> None:

    try:

        with console.status(
            "[bold]Investigating event...[/bold]",
            spinner="dots",
        ):

            structured_result = asyncio.run(
                run_investigation(
                    service_name,
                    user_query,
                )
            )

    except KeyboardInterrupt:

        console.clear()

        console.print(
            "[yellow]Investigation cancelled.[/yellow]"
        )

        return

    except Exception as exc:

        console.print()

        console.print(
            "Investigation failed:",
            style="bold red",
        )

        console.print(
            str(exc),
            style="red",
        )

        raise typer.Exit(code=1)

    console.clear()

    print_header()
    print_summary(structured_result)
    print_query(structured_result)
    print_timeline(structured_result)

    interactive_timeline(structured_result)


# -------------------------------------------------------------------
# CLI command
# -------------------------------------------------------------------

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

    # ---------------------------------------------------------------
    # 1. Select service
    # ---------------------------------------------------------------

    service_name = select_service()

    console.print()

    console.print(
        f" Service selected: [bold]{service_name}[/bold]"
    )

    console.print()

    # ---------------------------------------------------------------
    # 2. Get investigation query
    # ---------------------------------------------------------------

    if query:

        user_query = query

    else:

        user_query = typer.prompt(
            "What would you like to investigate?"
        )

    if not user_query.strip():

        console.print(
            "[bold red]No investigation query provided.[/bold red]"
        )

        raise typer.Exit(code=1)

    # ---------------------------------------------------------------
    # 3. Investigate
    # ---------------------------------------------------------------

    investigate(
        service_name,
        user_query,
    )


if __name__ == "__main__":
    app()