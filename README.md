# Observee SDK FastAPI Wrapper

A FastAPI wrapper for the Observee SDK that exposes tool management functions through HTTP endpoints.

## Features

- **Filter Tools**: Find relevant tools using local embedding search
- **Get Tool Info**: Retrieve detailed information about specific tools
- **Execute Tools**: Run tools directly with provided parameters
- **Multiple API formats**: Both POST (with JSON body) and GET (with query parameters) support

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Observee API key as an environment variable:
```bash
export OBSERVEE_API_KEY="obs_your_key_here"
```

## Running the API

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### 1. Filter Tools

Find relevant tools based on a query using local embedding search.

**POST** `/filter-tools`
```json
{
  "query": "email management",
  "max_tools": 5,
  "filter_type": "local_embedding"
}
```

**GET** `/filter-tools?query=email%20management&max_tools=5`

### 2. Get Tool Information

Retrieve detailed information about a specific tool.

**POST** `/tool-info`
```json
{
  "tool_name": "gmail_search_emails"
}
```

**GET** `/tool-info/gmail_search_emails`

### 3. Execute Tool

Execute a tool directly with provided parameters.

**POST** `/execute-tool`
```json
{
  "tool_name": "youtube_get_transcript",
  "tool_input": {
    "video_url": "https://youtube.com/watch?v=example"
  }
}
```

## Response Formats

All endpoints return structured JSON responses with appropriate error handling.

### Filter Tools Response
```json
{
  "tools": [
    {
      "name": "tool_name",
      "description": "Tool description",
      "relevance_score": 0.85,
      "parameters": {...}
    }
  ],
  "count": 5
}
```

### Tool Info Response
```json
{
  "tool_info": {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {...}
  },
  "found": true
}
```

### Execute Tool Response
```json
{
  "result": "Tool execution result",
  "success": true,
  "error": null
}
```

## Environment Variables

- `OBSERVEE_API_KEY`: Your Observee API key (required)

## Error Handling

The API includes comprehensive error handling:
- 400: Bad Request (missing API key, invalid parameters)
- 500: Internal Server Error (SDK errors, execution failures)

All error responses include detailed error messages to help with debugging.

## Health Check

**GET** `/health` - Returns API health status

## Development

For development with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
