import os

from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_splunk_query_tool():
    mcp_client = MultiServerMCPClient(
        {
            "splunk": {
                "transport": "stdio",
                "command": "sh",
                "args": [
                    "-c",
                    (
                        "npx -y mcp-remote "
                        f"'{os.environ['SPLUNK_MCP_URL']}' "
                        "--header "
                        f"'Authorization: Bearer "
                        f"{os.environ['SPLUNK_MCP_TOKEN']}' "
                        "2>/dev/null"
                    ),
                ],
            }
        }
    )

    splunk_tools = await mcp_client.get_tools()

    return next(
        tool
        for tool in splunk_tools
        if tool.name == "splunk_run_query"
    )