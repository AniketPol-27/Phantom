import os
import structlog

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


logger = structlog.get_logger(__name__)


PHANTOM_MCP_URL = os.getenv(
    "PHANTOM_MCP_URL",
    "http://localhost:8080/mcp",    
)


class PhantomMCPClient:

    def __init__(self, server_url: str = PHANTOM_MCP_URL):
        self.server_url = server_url.rstrip("/")

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
        headers: dict | None = None,
    ):

        logger.info(
            "phantom_mcp.call_tool",
            tool=tool_name,
        )

        async with streamablehttp_client(
            self.server_url,
            headers=headers,
        ) as (
            read_stream,
            write_stream,
            _,
        ):

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments=arguments,
                )

                logger.info(
                    "phantom_mcp.tool_complete",
                    tool=tool_name,
                )

                return result


phantom_mcp_client = PhantomMCPClient()
