#!/usr/bin/env python3
"""CAMEL Terminal Toolkit MCP Server."""

import asyncio
import inspect
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
from pydantic import BaseModel

from camel.toolkits.terminal_toolkit import TerminalToolkit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create server instance
server = Server("camel-terminal-toolkit")

# Global terminal toolkit instance
terminal_toolkit: Optional[TerminalToolkit] = None
toolkit_kwargs: Dict[str, Any] = {}


def initialize_toolkit() -> None:
    """Initialize the terminal toolkit."""
    global terminal_toolkit
    if not terminal_toolkit:
        logger.info("Initializing Terminal Toolkit")
        terminal_toolkit = TerminalToolkit(**toolkit_kwargs)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    if not terminal_toolkit:
        initialize_toolkit()
        
    tools = []
    function_tools = terminal_toolkit.get_tools()
    
    for func_tool in function_tools:
        # Extract function info
        func = func_tool.func
        func_name = func.__name__
        func_doc = func.__doc__ or f"Execute {func_name}"
        
        # Get function signature for parameters
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # Default type
            param_desc = f"Parameter {param_name}"
            
            # Try to get type info
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
            
            param_info = {"type": param_type, "description": param_desc}
            
            # Handle optional parameters
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            
            parameters[param_name] = param_info
        
        tool = Tool(
            name=func_name,
            description=func_doc.split('\n')[0].strip(),
            inputSchema={
                "type": "object",
                "properties": parameters,
                "required": [
                    name for name, param in sig.parameters.items()
                    if param.default == inspect.Parameter.empty
                ],
            }
        )
        tools.append(tool)
        
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Call a tool."""
    if not terminal_toolkit:
        initialize_toolkit()
        
    try:
        # Find the tool function
        function_tools = terminal_toolkit.get_tools()
        target_func = None
        
        for func_tool in function_tools:
            if func_tool.func.__name__ == name:
                target_func = func_tool.func
                break
        
        if not target_func:
            return [TextContent(
                type="text",
                text=f"Tool '{name}' not found"
            )]
        
        # Call the function
        result = target_func(**arguments)
        
        # Handle the result
        if isinstance(result, str):
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=str(result))]
            
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error calling tool {name}: {str(e)}"
        )]


def parse_args() -> Dict[str, Any]:
    """Parse command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CAMEL Terminal Toolkit MCP Server"
    )
    parser.add_argument(
        "--working-directory",
        help="Working directory for terminal operations"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Timeout for terminal operations (default: 20.0)"
    )
    parser.add_argument(
        "--safe-mode",
        action="store_true",
        default=True,
        help="Enable safe mode (default: True)"
    )
    parser.add_argument(
        "--no-safe-mode",
        dest="safe_mode",
        action="store_false",
        help="Disable safe mode"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode (default: False)"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    
    args = parser.parse_args()
    
    # Convert to toolkit kwargs
    toolkit_kwargs = {
        "timeout": args.timeout,
        "safe_mode": args.safe_mode,
        "interactive": args.interactive,
    }
    
    if args.working_directory:
        toolkit_kwargs["working_directory"] = args.working_directory
    
    return {
        "toolkit_kwargs": toolkit_kwargs,
        "transport_type": args.transport,
    }


def main() -> None:
    """Main entry point."""
    async def async_main() -> None:
        try:
            args = parse_args()
            
            # Set global toolkit kwargs
            global toolkit_kwargs
            toolkit_kwargs = args["toolkit_kwargs"]
            
            logger.info("Starting CAMEL Terminal Toolkit MCP Server")
            
            # Run the server with stdio transport
            await stdio_server(server)
            
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)
    
    asyncio.run(async_main())


if __name__ == "__main__":
    main()