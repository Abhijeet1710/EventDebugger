import asyncio
import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main():

    splunk_url = os.environ["SPLUNK_MCP_URL"]
    splunk_token = os.environ["SPLUNK_MCP_TOKEN"]

    client = MultiServerMCPClient(
        {
            "splunk": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "mcp-remote",
                    splunk_url,
                    "--header",
                    f"Authorization: Bearer {splunk_token}",
                ],
            }
        }
    )

    tools = await client.get_tools()

    print("\n" + "=" * 60)
    print("SPLUNK MCP CONNECTION SUCCESSFUL")
    print("=" * 60)

    print(f"\nNumber of tools: {len(tools)}")

    print("\nAvailable tools:\n")

    for tool in tools:
        print(f"Name: {tool.name}")
        print(f"Description: {tool.description}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())