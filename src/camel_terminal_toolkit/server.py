#!/usr/bin/env python3
"""CAMEL Terminal Toolkit MCP Server."""

import logging
import sys
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from camel.toolkits.terminal_toolkit import TerminalToolkit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("CAMEL Terminal Toolkit")

# Global terminal toolkit instance
terminal_toolkit: Optional[TerminalToolkit] = None
toolkit_kwargs: Dict[str, Any] = {}


def initialize_toolkit() -> None:
    """Initialize the terminal toolkit."""
    global terminal_toolkit
    if not terminal_toolkit:
        logger.info("Initializing Terminal Toolkit")
        terminal_toolkit = TerminalToolkit(**toolkit_kwargs)


# Register all terminal toolkit functions as MCP tools
def register_tools() -> None:
    """Register all terminal toolkit functions as MCP tools."""
    initialize_toolkit()
    
    # Get all function tools from the terminal toolkit
    function_tools = terminal_toolkit.get_tools()
    
    for func_tool in function_tools:
        func = func_tool.func
        func_name = func.__name__
        
        # Register the function with FastMCP
        mcp.tool()(func)


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
    try:
        args = parse_args()
        
        # Set global toolkit kwargs
        global toolkit_kwargs
        toolkit_kwargs = args["toolkit_kwargs"]
        
        logger.info("Starting CAMEL Terminal Toolkit MCP Server")
        
        # Register all tools
        register_tools()
        
        # Run the server with stdio transport
        mcp.run("stdio")
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()