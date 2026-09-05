import os

from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_splunk_query_tool():

    print("\nConnecting to Splunk MCP...")

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

    splunk_tools = await mcp_client.get_tools()

    splunk_query_tool = next(
        tool
        for tool in splunk_tools
        if tool.name == "splunk_run_query"
    )

    print("\nUsing Splunk MCP tool:")
    print(f"  - {splunk_query_tool.name}")

    return splunk_query_tool