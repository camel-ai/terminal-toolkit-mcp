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

Using uv (recommended):

```bash
cd camel_terminal_toolkit
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

Using pip:

```bash
cd camel_terminal_toolkit
pip install -e .
```

## Usage

### As an MCP Server

Start the server with stdio transport:

```bash
camel-terminal-mcp
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
camel-terminal-mcp --working-directory /tmp/workspace --timeout 60.0

# Start with safe mode disabled (not recommended)
camel-terminal-mcp --no-safe-mode
```

## Available Tools

The server exposes the following tools through MCP:

1. **shell_exec(id, command)**: Execute a shell command in a session
2. **shell_view(id)**: View the output history of a session  
3. **shell_wait(id, seconds)**: Wait for a running command to complete
4. **shell_write_to_process(id, input, press_enter)**: Send input to a running process
5. **shell_kill_process(id)**: Terminate a running process
6. **ask_user_for_help(id)**: Request human assistance

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

## License

Apache License 2.0 - see the CAMEL-AI project for full license details.

## Contributing

This project is part of the CAMEL-AI ecosystem. Please refer to the main CAMEL repository for contribution guidelines.