import asyncio
import os
from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel


load_dotenv()


# ============================================================
# 1. SERVICE CONFIGURATION
# ============================================================

SERVICE_CONFIGS = {
    "ingestion-service": {
        "serviceId": "ingestion-service_123456789",
        "serviceName": "ingestion-service",

        "splunk": {
            "index": "ing_service",
            "source": "ing",
            "sourcetype": "log4j"
        },
        
        "eventIdentifier": {
            "field": "eventId",
            "source": "message",
            "searchMode": "contains"
        },

        "stages": [
            {
                "stageName": "Request Received",
                "stageType": "RECEIVED",
                "stepValue": "Request received",
                "order": 1
            },
            {
                "stageName": "Validation",
                "stageType": "VALIDATION",
                "stepValue": "validate complete",
                "order": 2
            },
            {
                "stageName": "Filter",
                "stageType": "FILTER",
                "stepValue": "filter complete",
                "order": 3
            },
            {
                "stageName": "Transformation",
                "stageType": "TRANSFORM",
                "stepValue": "transform complete",
                "order": 4
            },
            {
                "stageName": "Outbound",
                "stageType": "PUBLISH",
                "stepValue": "outbound complete",
                "order": 5
            }
        ]
    }
}


# ============================================================
# 2. STRUCTURED RESPONSE MODELS
# ============================================================
#
# NOTE:
# We are keeping these models defined because we will use them
# later for the final structured response.
#
# We are NOT passing InvestigationResult to ChatOpenAI or
# create_agent yet.
# ============================================================

class StageResult(BaseModel):
    stage: str

    status: Literal[
        "SUCCESS",
        "FAILED",
        "NOT_FOUND",
        "FILTERED_OUT",
        "NOT_REACHED",
        "UNKNOWN"
    ]

    timestamp: str | None = None
    evidence: str | None = None
    description: str | None = None


class InvestigationResult(BaseModel):
    event_id: str

    service: str

    overall_status: Literal[
        "SUCCESS",
        "FAILED",
        "NOT_FOUND",
        "UNKNOWN"
    ]

    stages: list[StageResult]

    summary: str


# ============================================================
# 3. SERVICE CONFIG TOOL
# ============================================================

@tool
def get_service_config(service_name: str) -> dict:
    """
    Get the onboarding configuration for a service.

    The configuration contains:
    - Splunk index
    - Splunk source
    - Splunk sourcetype
    - Event identifier field
    - Processing stages
    """

    print(f"\nTOOL → get_service_config({service_name})")

    config = SERVICE_CONFIGS.get(service_name)

    if not config:
        return {
            "error": f"Service '{service_name}' is not onboarded."
        }

    return config


# ============================================================
# 4. MODEL
# ============================================================
#
# IMPORTANT:
# Do NOT use:
#
# ChatOpenAI(...).with_structured_output(...)
#
# create_agent needs the original ChatOpenAI instance so that
# LangChain can call bind_tools() on it.
# ============================================================

model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0
)

# ============================================================
# 5. RESULT FORMATTER MODEL
# ============================================================

result_model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0
).with_structured_output(InvestigationResult)

# ============================================================
# 6. RESULT FORMATTER PROMPT
# ============================================================

RESULT_FORMATTER_PROMPT = """
    You are the result formatting component of an AI Production
    Investigation system.

    Convert the investigation findings into the required
    InvestigationResult structure.

    Rules:

    - Use ONLY information contained in the investigation findings.
    - Do not invent logs.
    - Do not invent timestamps.
    - Do not invent stage execution.
    - Do not invent filter criteria.
    - Do not perform root cause analysis.
    - Preserve the distinction between observed facts and likely explanations.

    Stage status rules:

    SUCCESS:
    The stage has direct evidence of successful completion.

    FAILED:
    There is explicit evidence of an error or failure associated with
    that stage.

    NOT_REACHED:
    The evidence shows that processing stopped before this stage.

    FILTERED_OUT:
    Use only when the Filter stage was successfully reached and there
    is evidence that processing stopped there because the event was
    filtered out.

    UNKNOWN:
    There is insufficient evidence to determine the stage outcome.

    Overall status:

    SUCCESS:
    All configured stages completed successfully.

    FAILED:
    There is explicit evidence of a processing failure.

    NOT_FOUND:
    No evidence of the event exists in Splunk.

    UNKNOWN:
    The evidence is insufficient to determine the outcome.

    Do not add information that is not present in the investigation
    findings.

    ============================================================
    ERROR PLACEMENT AND TIMELINE
    ============================================================

    The "stages" array represents the chronological processing timeline.

    Configured processing stages must normally appear in their configured
    order.

    However, explicit error events from the logs must be inserted into
    the timeline at their actual chronological position.

    Example configured stages:

    1. Request Received
    2. Validation
    3. Filter
    4. Transformation
    5. Outbound

    Observed evidence:

    Request Received
    Validation
    Filter
    ERROR
    (no Transformation)
    (no Outbound)

    The output must be:

    Request Received       SUCCESS
    Validation             SUCCESS
    Filter                 SUCCESS
    ERROR                  FAILED
    Transformation         NOT_REACHED
    Outbound               NOT_REACHED

    Do NOT put ERROR at the end of the array.

    The ERROR entry must be positioned according to its timestamp relative
    to the configured stages.

    For an explicit error event use:

    stage = "ERROR"
    status = "FAILED"

    Use the actual error timestamp when available.

    Use the actual error message as evidence.

    Do not invent an error description.

    ============================================================
    PRECEDING STAGE DESCRIPTION
    ============================================================

    When an explicit error occurs after a successfully completed stage
    and before the next configured stage, update the description of the
    preceding successful stage.

    For example:

    Filter:
    status = SUCCESS

    description:
    "Filter completed successfully. An explicit error was subsequently
    observed before Transformation was reached."

    The description must clearly indicate that the error occurred after
    the stage.

    Do NOT claim that the error occurred inside the preceding stage unless
    the logs explicitly establish that.

    ============================================================
    NOT_REACHED STAGES
    ============================================================

    If an explicit error occurs before a later configured stage and there
    is no evidence that the later stage was reached:

    mark the later stage as NOT_REACHED.

    For example:

    ERROR occurs after Filter and before Transformation.

    Then:

    Transformation → NOT_REACHED
    Outbound → NOT_REACHED

    Do not mark Transformation as FAILED unless there is explicit evidence
    that the error occurred during Transformation.

    ============================================================
    OVERALL STATUS
    ============================================================

    If an explicit processing error is present for the event:

    overall_status = FAILED

    Do not require a later stage failure log when an explicit error already
    establishes that processing failed.
"""

# ============================================================
# 7. SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
    You are an AI Production Investigation Agent.

    Your job is to investigate events processed by onboarded services.

    Your primary question is:

    "What happened to this event?"

    You have access to:

    1. get_service_config
    2. splunk_run_query

    ============================================================
    INVESTIGATION PROCESS
    ============================================================

    Follow this process:

    1. Identify the service from the user's request.

    2. Retrieve the service configuration using:
    get_service_config

    3. Read the service configuration carefully.

    4. Identify the event ID.

    5. Read the configured Splunk information:
    - index
    - source
    - sourcetype

    6. Read the configured event identifier field.

    7. Construct an SPL query for the specific event.

    8. Use:
    splunk_run_query

    to retrieve the event's logs from Splunk.

    9. Retrieve enough logs to reconstruct the processing flow.

    10. Order the logs chronologically using _time.

    11. Map the retrieved logs to the configured processing stages.

    12. Determine what happened at each stage.

    13. Explain the final observed outcome.

    ============================================================
    SPLUNK QUERY REQUIREMENTS
    ============================================================

    Always use the service configuration when constructing the query.

    The query should use:

    - configured index
    - configured source
    - configured sourcetype
    - configured event identifier field

    For example, if the configuration says:

    index = ing_service
    source = ing
    sourcetype = log4j
    event identifier field = eventId

    and the event ID is:

    evt-123

    then construct an appropriate query targeting that event.

    Sort the results chronologically using:

    _time

    Do not perform broad searches when a specific event ID is available.

    Do not query unrelated services.

    Do not call unrelated Splunk administrative tools.

    Use splunk_run_query for the actual log investigation.

    When retrieving Splunk results, preserve explicit ERROR/exception
    events as investigation evidence.

    Do not discard an error simply because it does not match one of the
    configured stage stepValue values.

    For every explicit error event, preserve:
    - timestamp
    - severity
    - message
    - logger when available
    - relevant event identifier

    The error must remain available to the final result formatter so it
    can be positioned chronologically between configured stages.

    ============================================================
    EVIDENCE RULES
    ============================================================

    Base conclusions only on retrieved evidence.

    Do NOT:

    - invent logs
    - invent timestamps
    - invent stage execution
    - invent errors
    - invent filter criteria
    - invent technical causes
    - perform root cause analysis

    Missing logs do NOT automatically mean failure.

    Absence of evidence is not automatically evidence of failure.

    Clearly distinguish:

    OBSERVED FACT

    from:

    LIKELY EXPLANATION

    ============================================================
    STAGE STATUS
    ============================================================

    For each configured stage, reason about its status.

    SUCCESS:

    Use when there is evidence that the stage completed successfully.

    FAILED:

    Use when there is explicit evidence of an error or failure at that stage.

    NOT_REACHED:

    Use when the evidence shows that processing stopped before
    a later configured stage.

    UNKNOWN:

    Use when there is insufficient evidence to determine what
    happened at that stage.

    FILTERED_OUT:

    Use for the Filter stage when:

    1. The Filter stage was successfully reached.
    2. There is no evidence of any subsequent processing stage.

    In this situation, the event was MOST LIKELY filtered out.

    However:

    - Do not claim this as a confirmed fact unless the logs explicitly
    prove filtering.
    - Do not invent the exact filter criteria.
    - Explain that the event most likely did not meet the filter criteria.

    ============================================================
    FILTER HANDLING
    ============================================================

    If the logs show:

    Request Received
    Validation
    Filter

    but there are no Transformation or Outbound logs:

    DO NOT say:

    "Transformation failed."

    DO NOT say:

    "Outbound failed."

    Instead, reason that:

    - Request Received was reached.
    - Validation was reached.
    - Filter was reached.
    - No subsequent stage was observed.
    - Therefore the event most likely stopped at the Filter stage.
    - The event was most likely filtered out.
    - The exact filter criteria are not known unless the logs explicitly
    provide them.

    ============================================================
    FAILURE HANDLING
    ============================================================

    If a log explicitly contains an error or failure at a stage:

    classify that stage as FAILED.

    Do NOT infer failure merely because a later log is missing.

    For example:

    If Validation succeeded but there is no Filter log,

    do NOT automatically say:

    "Filter failed."

    Instead, state that there is insufficient evidence to determine
    what happened at the Filter stage.

    ============================================================
    OVERALL OUTCOME
    ============================================================

    SUCCESS:

    Use when the event is evidenced to have completed all configured
    processing stages.

    FAILED:

    Use when there is explicit evidence of a processing failure.

    NOT_FOUND:

    Use when there is no evidence that the event exists in Splunk.

    UNKNOWN:

    Use when available evidence is insufficient to determine the outcome.

    ============================================================
    RESPONSE
    ============================================================

    Provide a clear investigation result.

    Include:

    - splunk query which was ran to get the logs
    - event ID
    - service
    - chronological processing timeline
    - stages observed
    - evidence from the logs
    - final observed outcome
    - If there is any error, specify the error message clrearly and bind it with stages and how it impacted other stages
    - distinction between confirmed facts and likely explanations

    Do not perform root cause analysis.

    Do not speculate about technical causes.

    Answer the question:

    "What happened to this event?"
"""


# ============================================================
# 8. CREATE SPLUNK MCP CLIENT + AGENT
# ============================================================

async def create_investigation_agent():

    print("\nConnecting to Splunk MCP...")

    # --------------------------------------------------------
    # Connect to the official Splunk MCP Server through
    # mcp-remote.
    # --------------------------------------------------------

    mcp_client = MultiServerMCPClient(
        {
            "splunk": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "mcp-remote",
                    os.environ["SPLUNK_MCP_URL"],
                    "--header",
                    (
                        "Authorization: Bearer "
                        f"{os.environ['SPLUNK_MCP_TOKEN']}"
                    ),
                ],
            }
        }
    )

    # --------------------------------------------------------
    # Discover tools exposed by Splunk MCP.
    # --------------------------------------------------------

    splunk_tools = await mcp_client.get_tools()

    # --------------------------------------------------------
    # For V1, we only expose splunk_run_query.
    #
    # Splunk MCP exposes many other tools, but our investigation
    # agent does not need them yet.
    # --------------------------------------------------------

    splunk_query_tool = next(
        tool
        for tool in splunk_tools
        if tool.name == "splunk_run_query"
    )

    print("\nUsing Splunk MCP tool:")
    print(f"  - {splunk_query_tool.name}")

    # --------------------------------------------------------
    # Create LangChain agent.
    #
    # IMPORTANT:
    # model is the raw ChatOpenAI instance.
    # --------------------------------------------------------

    agent = create_agent(
        model=model,
        tools=[
            get_service_config,
            splunk_query_tool,
        ],
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


# ============================================================
# 9. RUN INVESTIGATION
# ============================================================

async def main():

    agent = await create_investigation_agent()

    print("\n")
    print("=" * 60)
    print("STARTING INVESTIGATION")
    print("=" * 60)

    # --------------------------------------------------------
    # User investigation request
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Step 1: Get the investigation agent's findings
    # --------------------------------------------------------

    investigation = result["messages"][-1].content

    print("\n")
    print("=" * 60)
    print("RAW INVESTIGATION")
    print("=" * 60)

    print(investigation)

    # --------------------------------------------------------
    # Step 2: Convert findings into structured output
    # --------------------------------------------------------

    structured_result = await result_model.ainvoke(
        [
            {
                "role": "system",
                "content": RESULT_FORMATTER_PROMPT,
            },
            {
                "role": "user",
                "content": investigation,
            },
        ]
    )

    # --------------------------------------------------------
    # Step 3: Print structured result
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("STRUCTURED INVESTIGATION RESULT")
    print("=" * 60)

    print(
        structured_result.model_dump_json(
            indent=2
        )
    )

# ============================================================
# 8. APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())