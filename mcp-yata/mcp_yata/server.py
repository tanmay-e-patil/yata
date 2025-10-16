import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import NotificationOptions
from .tools import setup_todo_tools
from .config import settings


def create_server() -> Server:
    """Create and configure the MCP server"""
    server = Server(settings.server_name)
    
    # Setup todo tools
    setup_todo_tools(server)
    
    return server


async def main():
    """Main entry point"""
    server = create_server()
    
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=settings.server_name,
                server_version=settings.server_version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())