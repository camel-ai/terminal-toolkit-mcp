# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
"""MCP Server Example

This example demonstrates how to use the MCP (Managed Code Processing) server
with CAMEL agents for file operations.

Setup:
1. Install Node.js and npm

2. Install MCP filesystem server globally:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   ```

Usage:
1. Run this script to start an MCP filesystem server
2. The server will only operate within the specified directory
3. All paths in responses will be relative to maintain privacy
"""

import asyncio

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType, ModelType
from camel.utils.mcp_client import MCPClient


async def mcp_client_example():
    config = {
        "command": "uvx",
        "args": ["terminal-toolkit-mcp"],
    }
    async with MCPClient(config) as client:
        mcp_tools = await client.list_mcp_tools()
        print("Available MCP tools:", [tool.name for tool in mcp_tools.tools])
        # Use shell_exec to list directory contents instead
        call_tool_result = await client.call_tool(
            "shell_exec", {"id": "main", "command": "ls -la"}
        )
        print("Directory Contents:")
        print(call_tool_result.content[0].text)

'''
Available MCP tools: ['shell_exec', 'shell_view', 'shell_wait', 'shell_write_to_process', 'shell_kill_process', 'ask_user_for_help']
Directory Contents:
total 0
drwxr-xr-x@  3 jinx0a  1840429327   96 Aug 21 15:16 .
drwxr-xr-x@ 12 jinx0a  1840429327  384 Aug 21 15:00 ..
drwxr-xr-x@  9 jinx0a  1840429327  288 Aug 21 15:16 .initial_env
'''


async def mcp_toolkit_example():
    # Use either config path or config dict to initialize the MCP toolkit.
    # 1. Use config path:
    config = {
        "mcpServers": {
            "terminal-toolkit-mcp": {
                "command": "uvx",
                "args": ["terminal-toolkit-mcp"],
            }
        }
    }

    # Connect to all MCP servers.
    async with MCPToolkit(config_dict=config) as mcp_toolkit:
        sys_msg = "You are a helpful assistant"
        model = ModelFactory.create(
            model_platform=ModelPlatformType.DEFAULT,
            model_type=ModelType.DEFAULT,
        )
        camel_agent = ChatAgent(
            system_message=sys_msg,
            model=model,
            tools=[*mcp_toolkit.get_tools()],
        )
        user_msg = "Use terminal to find out what's the current date"
        response = await camel_agent.astep(user_msg)
        print(response.msgs[0].content)
        print(response.info['tool_calls'])
'''
The current date and time is Thu Aug 21 15:18:39 +03 2025.
[ToolCallingRecord(tool_name='shell_exec', args={'id': 'session1', 'command': 'date'}, result='Thu Aug 21 15:18:39 +03 2025\n', tool_call_id='call_6pVGuMM1cA4b0BKkknIOLTMZ', images=None)]
'''

if __name__ == "__main__":
    asyncio.run(mcp_client_example())
    asyncio.run(mcp_toolkit_example())

