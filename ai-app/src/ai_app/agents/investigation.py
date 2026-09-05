from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from ai_app.mcp.splunk import get_splunk_query_tool
from ai_app.models.investigation import InvestigationResult
from ai_app.prompts.formatter import RESULT_FORMATTER_PROMPT
from ai_app.prompts.investigation import SYSTEM_PROMPT
from ai_app.tools.service_config import get_service_config


model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0
)


result_model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0
).with_structured_output(InvestigationResult)


async def create_investigation_agent():

    splunk_query_tool = await get_splunk_query_tool()

    agent = create_agent(
        model=model,
        tools=[
            get_service_config,
            splunk_query_tool,
        ],
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


async def format_investigation_result(investigation: str):

    return await result_model.ainvoke(
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