# Streamlit MCP Agent

> **Note**  
> My main profession is as a network engineer. I develop software as a hobby, with the philosophy of "if it works, that's good enough."  
> Therefore, there may be immature aspects in code quality and design, but I appreciate your understanding.

Streamlit MCP Agent is a Streamlit application that provides a chat interface with AI agents utilizing the Model Context Protocol (MCP). It uses AWS's Strands Agents framework. It integrates various tools via MCP clients to realize an interactive AI assistant.

## Project Overview

This application provides the following main features:

- **MCP Integration**: Supports multiple MCP clients, allowing AI agents to utilize external tools
- **Streaming Responses**: Displays AI responses in real-time streaming
- **Chat Interface**: User-friendly chat UI based on Streamlit
- **Session Management**: Maintains chat history and session state reset functionality
- **Tool Execution**: Executes tools via MCP and displays results

Although many MCP-compatible clients have been released recently, most are for personal use, so I created this to make it suitable for publishing as a web app within a company.

## Required Environment and Dependencies

### System Requirements
- Python 3.13 or higher
- uv (Python package manager)

### Dependencies
- `ollama>=0.5.4`: Integration with Ollama models (required only if using Ollama with the default settings)
- `strands-agents>=1.9.1`: AI agent framework
- `streamlit>=1.49.1`: Web application UI

### Additional Requirements
- Ollama server: Uses `http://localhost:11434` by default
- MCP configuration file: Define MCP client settings in `param/mcp.json`

## Installation and Execution Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/applemk2-git/streamlit-mcp-agent.git
cd streamlit-mcp-agent
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Run the Application
```bash
uv streamlit run agent.py
```

Once the application starts, access `http://localhost:8501` in your browser.

### 4. Model Server Setup (Optional)
If running with the default settings, an Ollama server is required. If not running, start it:
```bash
ollama serve
```

Uses `gpt-oss:20b` as the default model. Change `DEFAULT_MODEL_ID` in `agent.py` as needed.

## Usage Examples

### Basic Usage
1. After starting the application, select the MCP to use from the sidebar
2. Enter a message in the chat input field
3. The AI agent generates a response utilizing MCP tools

### Sample Conversation
```
User: Please tell me the current weather
Assistant: [Retrieves weather information using MCP tools and displays the result]
```

### MCP Configuration Examples
`param/mcp.json` supports the following 3 transport types:

#### 1. stdio (Standard Input/Output)
Example notation. Please rewrite according to the actual MCP you use.
```json
{
  "aws-documentation-mcp": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["awslabs.aws-documentation-mcp-server@latest"]
  }
}
```

#### 2. streamable-http (HTTP Streaming)
Example notation. Please rewrite according to the actual MCP you use. Remote hosts are also OK, not just localhost.
```json
{
  "api-server": {
    "transport": "streamable-http",
    "url": "http://localhost:3000/mcp"
  }
}
```

#### 3. sse (Server-Sent Events)
Example notation. Please rewrite according to the actual MCP you use. Remote hosts are also OK, not just localhost.
```json
{
  "sse-server": {
    "transport": "sse",
    "url": "http://localhost:3000/sse-mcp"
  }
}
```

Multiple MCP servers can be defined separated by commas.

### About Default MCP Settings
`param/mcp.json` includes the following default settings:

- **aws-documentation-mcp**: Official MCP server provided by AWS (actually works)
  - Provides AWS documentation search functionality

**Note**: The examples for streamable-http and sse are listed as references for notation, but they are dummy settings that do not actually work. When using actual MCP servers, change to appropriate URLs or commands.

## Feature Details

### MCP Client Support
- **stdio**: Standard input/output-based MCP clients
- **streamable-http**: HTTP streaming-based MCP clients
- **sse**: Server-Sent Events-based MCP clients

### Error Handling
- Warning display when MCP client initialization fails
- Proper handling of tool execution errors
- Safe management of session state

### Customization
- Change system prompt (`DEFAULT_SYSTEM_PROMPT`)
- Change model settings (`DEFAULT_MODEL_HOST`, `DEFAULT_MODEL_ID`)
- Change MCP configuration file path (`MCP_CONFIG_PATH`)

## License

This project is licensed under Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Notes

- Initial execution may take time for MCP client initialization
- External API-using MCP tools require appropriate authentication credentials
- Ensure Ollama server is running in development environment

## About Model Settings

This project shows an example using Ollama, but this is just one example. For available models and how to use each model, refer to the [Model Providers section of the Strands Agents documentation](https://strandsagents.com/latest/documentation/docs/) and configure appropriately for each.

You can use different model providers by changing the following parts in `agent.py`:

### Changing Configuration Constants
- `DEFAULT_MODEL_HOST`: Model server host URL
- `DEFAULT_MODEL_ID`: Model ID to use
- `DEFAULT_SYSTEM_PROMPT`: System prompt
- `MODEL`: Model

### Changing Model Object
Changing the above constants alone is insufficient. You also need to change the model object in the `create_agent` function to the appropriate model provider:

```python
# Current OllamaModel example
model=OllamaModel(
    host=DEFAULT_MODEL_HOST,
    model_id=DEFAULT_MODEL_ID,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)
```

When using other model providers (e.g., OpenAI, Anthropic, etc.), change to the corresponding model class and set the necessary parameters. Refer to the Strands Agents documentation for detailed configuration methods.
