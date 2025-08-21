# CAMEL Terminal Toolkit MCP Server

This is a standalone MCP (Model Context Protocol) server that exports the CAMEL Terminal Toolkit functionality. It allows LLM clients to execute terminal commands safely through the MCP protocol.

## Features

- **Shell Execution**: Execute shell commands in managed sessions
- **Session Management**: Create and manage multiple shell sessions
- **Safe Mode**: Restrict dangerous operations and enforce working directory boundaries
- **Interactive Support**: Support for interactive commands (Linux/macOS only)
- **Process Management**: Control running processes (view, wait, write input, kill)
- **Human Takeover**: Request human assistance when needed

## Installation

### Option 1: Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`, which will automatically install and run it:

```bash
uvx terminal-toolkit-mcp
```

### Option 2: Using pip

```bash
pip install terminal-toolkit-mcp
```

### Option 3: Development Installation

```bash
git clone https://github.com/camel-ai/terminal-toolkit-mcp.git
cd terminal-toolkit-mcp
pip install -e .
```

## Usage

### As an MCP Server

Start the server with stdio transport:

```bash
terminal-toolkit-mcp
```

### Command Line Options

- `--working-directory PATH`: Set the working directory for operations
- `--timeout SECONDS`: Set timeout for operations (default: 20.0)
- `--safe-mode` / `--no-safe-mode`: Enable/disable safe mode (default: enabled)
- `--interactive`: Enable interactive mode for commands requiring input
- `--transport {stdio}`: Set transport type (currently only stdio supported)

### Example

```bash
# Start with custom working directory and increased timeout
terminal-toolkit-mcp --working-directory /tmp/workspace --timeout 60.0

# Start with safe mode disabled (not recommended)
terminal-toolkit-mcp --no-safe-mode
```

## Available Tools

The server exposes the following tools through MCP:

1. **shell_exec(id, command)**: Execute a shell command in a session
2. **shell_view(id)**: View the output history of a session  
3. **shell_wait(id, seconds)**: Wait for a running command to complete
4. **shell_write_to_process(id, input, press_enter)**: Send input to a running process
5. **shell_kill_process(id)**: Terminate a running process
6. **ask_user_for_help(id)**: Request human assistance

## MCP Client Configuration

To use this server with MCP clients, you need to configure your client to connect to the terminal toolkit server. Here are examples for different scenarios:

### For Claude Desktop

Add this configuration to your Claude Desktop settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "terminal-toolkit": {
      "command": "uvx",
      "args": ["terminal-toolkit-mcp"]
    }
  }
}
```

### For CAMEL Framework

#### Option 1: Using MCPClient (Direct Connection)

```python
import asyncio
from camel.utils.mcp_client import MCPClient

async def main():
    config = {
        "command": "uvx",
        "args": ["terminal-toolkit-mcp"]
    }
    
    async with MCPClient(config) as client:
        # List available tools
        tools = await client.list_mcp_tools()
        print("Available tools:", [tool.name for tool in tools.tools])
        
        # Execute a shell command
        result = await client.call_tool(
            "shell_exec", 
            {"id": "main", "command": "ls -la"}
        )
        print("Command output:", result.content[0].text)

asyncio.run(main())
```

#### Option 2: Using MCPToolkit (Recommended for Agents)

```python
import asyncio
from pathlib import Path
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType, ModelType

async def main():
    # Configuration for terminal toolkit
    config = {
        "mcpServers": {
            "terminal-toolkit": {
                "command": "uvx",
                "args": ["terminal-toolkit-mcp"]
            }
        }
    }
    
    # Connect to MCP server
    async with MCPToolkit(config=config) as mcp_toolkit:
        # Create an agent with terminal tools
        model = ModelFactory.create(
            model_platform=ModelPlatformType.DEFAULT,
            model_type=ModelType.DEFAULT,
        )
        
        agent = ChatAgent(
            system_message="You are a helpful assistant with terminal access.",
            model=model,
            tools=[*mcp_toolkit.get_tools()],
        )
        
        # Use the agent
        response = await agent.astep(
            "List the files in the current directory and show their sizes"
        )
        print(response.msgs[0].content)

asyncio.run(main())
```

### Configuration Options

You can customize the server behavior by passing additional arguments:

```json
{
  "mcpServers": {
    "terminal-toolkit": {
      "command": "uvx",
      "args": [
        "terminal-toolkit-mcp",
        "--working-directory", "/path/to/workspace",
        "--timeout", "30.0",
        "--safe-mode"
      ]
    }
  }
}
```

Available configuration options:
- `--working-directory PATH`: Set the working directory for terminal operations
- `--timeout SECONDS`: Set timeout for operations (default: 20.0)
- `--safe-mode` / `--no-safe-mode`: Enable/disable safe mode (default: enabled)
- `--interactive`: Enable interactive mode for commands requiring input

### Alternative Installation Methods

If you have the package installed locally, you can also use:

```json
{
  "mcpServers": {
    "terminal-toolkit": {
      "command": "terminal-toolkit-mcp"
    }
  }
}
```

Or if you prefer the legacy executable name:

```json
{
  "mcpServers": {
    "terminal-toolkit": {
      "command": "uvx",
      "args": ["--from", "terminal-toolkit-mcp", "camel-terminal-mcp"]
    }
  }
}
```

## Complete Usage Examples

### Example 1: Basic Terminal Operations

```python
import asyncio
from camel.utils.mcp_client import MCPClient

async def terminal_example():
    config = {
        "command": "uvx",
        "args": ["terminal-toolkit-mcp"]
    }
    
    async with MCPClient(config) as client:
        # Start a shell session and run commands
        session_id = "demo"
        
        # List directory contents
        result = await client.call_tool(
            "shell_exec", 
            {"id": session_id, "command": "pwd && ls -la"}
        )
        print("Directory listing:")
        print(result.content[0].text)
        
        # Create a file and check it
        await client.call_tool(
            "shell_exec",
            {"id": session_id, "command": "echo 'Hello MCP!' > test.txt"}
        )
        
        result = await client.call_tool(
            "shell_exec",
            {"id": session_id, "command": "cat test.txt"}
        )
        print("File contents:")
        print(result.content[0].text)
        
        # Clean up
        await client.call_tool(
            "shell_exec",
            {"id": session_id, "command": "rm test.txt"}
        )

asyncio.run(terminal_example())
```

### Example 2: Interactive Process Management

```python
import asyncio
from camel.utils.mcp_client import MCPClient

async def interactive_example():
    config = {
        "command": "uvx",
        "args": ["terminal-toolkit-mcp", "--interactive"]
    }
    
    async with MCPClient(config) as client:
        session_id = "interactive"
        
        # Start an interactive process (e.g., Python REPL)
        await client.call_tool(
            "shell_exec",
            {"id": session_id, "command": "python3"}
        )
        
        # Send input to the running process
        await client.call_tool(
            "shell_write_to_process",
            {
                "id": session_id,
                "input": "print('Hello from Python!')",
                "press_enter": True
            }
        )
        
        # Wait and view output
        await client.call_tool("shell_wait", {"id": session_id, "seconds": 1})
        
        result = await client.call_tool("shell_view", {"id": session_id})
        print("Python output:")
        print(result.content[0].text)
        
        # Exit Python
        await client.call_tool(
            "shell_write_to_process",
            {"id": session_id, "input": "exit()", "press_enter": True}
        )

asyncio.run(interactive_example())
```

### Example 3: Agent with Terminal Access

```python
import asyncio
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType, ModelType

async def agent_example():
    config = {
        "mcpServers": {
            "terminal": {
                "command": "uvx",
                "args": ["terminal-toolkit-mcp"]
            }
        }
    }
    
    async with MCPToolkit(config=config) as mcp_toolkit:
        model = ModelFactory.create(
            model_platform=ModelPlatformType.DEFAULT,
            model_type=ModelType.DEFAULT,
        )
        
        agent = ChatAgent(
            system_message="You are a helpful coding assistant with terminal access. "
                         "Use the terminal tools to help users with their tasks.",
            model=model,
            tools=[*mcp_toolkit.get_tools()],
        )
        
        # Example tasks
        tasks = [
            "Create a simple Python script that prints 'Hello World' and run it",
            "Check the current Git status and show me the recent commits",
            "Find all Python files in the current directory and count the lines of code"
        ]
        
        for task in tasks:
            print(f"\n🤖 Task: {task}")
            response = await agent.astep(task)
            print(f"📝 Response: {response.msgs[0].content}")

asyncio.run(agent_example())
```

## Safety Features

When safe mode is enabled (default):

- Commands are restricted to the working directory
- Dangerous system commands are blocked
- File operations are limited to the workspace
- Network commands are prohibited

## Development

### Setup Development Environment

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff check .
ruff format .
```

## Troubleshooting

### Common Issues

#### 1. "An executable named `terminal-toolkit-mcp` is not provided"

If you see this error, it means the package isn't properly installed or uvx is using a cached version. Try:

```bash
# Clear uvx cache and reinstall
uvx --from terminal-toolkit-mcp==0.1.2 terminal-toolkit-mcp --help

# Or use the legacy executable name
uvx --from terminal-toolkit-mcp camel-terminal-mcp --help
```

#### 2. MCP Connection Failed

Ensure the server starts correctly:

```bash
# Test the server directly
terminal-toolkit-mcp --help

# Check if uvx can run it
uvx terminal-toolkit-mcp --help
```

#### 3. Permission Denied Errors

In safe mode (default), some operations might be restricted. You can:

- Use `--working-directory` to set an appropriate workspace
- Disable safe mode with `--no-safe-mode` (not recommended for production)

#### 4. Tool Parameter Validation Errors

Make sure to provide all required parameters:

```python
# Correct usage
await client.call_tool("shell_exec", {"id": "session1", "command": "ls"})

# Missing required 'id' parameter will cause an error
await client.call_tool("shell_exec", {"command": "ls"})  # ❌ Error
```

### Debug Mode

Enable verbose logging by setting the environment variable:

```bash
export PYTHONPATH=.
python -m camel_terminal_toolkit.server --help
```

## License

Apache License 2.0 - see the CAMEL-AI project for full license details.

## Contributing

This project is part of the CAMEL-AI ecosystem. Please refer to the main CAMEL repository for contribution guidelines.

## Changelog

### v0.1.2
- **Complete MCP configuration documentation**: Added comprehensive guides for Claude Desktop, CAMEL Framework, and other MCP clients
- **Working examples**: Added complete usage examples for basic operations, interactive processes, and agent integration
- **Troubleshooting guide**: Added detailed troubleshooting section with common issues and solutions
- **Verified PyPI integration**: Confirmed simple configuration `uvx terminal-toolkit-mcp` works with PyPI package
- **Enhanced client examples**: Updated examples with actual working output demonstrations

### v0.1.1
- Fixed executable name configuration
- Added support for both `terminal-toolkit-mcp` and `camel-terminal-mcp` executables
- Updated documentation with comprehensive MCP configuration examples
- Improved client configuration examples

### v0.1.0
- Initial release
- Basic terminal toolkit functionality
- MCP server implementation
- Safe mode and interactive support