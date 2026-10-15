# Perspective API Alternative: Toxicity Detection MCP Server

This repository contains an MCP server for the stdio transport. The server gives AI agents one tool, `analyze_toxicity`. Use the tool to examine text before an agent publishes it.

The tool returns six scores from 0 to 1 and a flagged value for each text:

- `TOXICITY`, `SEVERE_TOXICITY`, `INSULT`, `PROFANITY`, `THREAT`, `IDENTITY_ATTACK`

The scores come from the open-source Detoxify model. The model is not an LLM. Thus, the same text always gets the same score. English only.

The request and response format is the same as the format of the Google Perspective API. Google stops the Perspective API on December 31, 2026.

## How the server operates

The server implementation is `server.py` in this repository. It uses only the Python standard library (Python 3.9 or later).

- The server reads JSON-RPC messages from stdin and writes the responses to stdout.
- The server answers `initialize`, `ping` and `tools/list` itself. These messages do not need a token.
- For `tools/call`, the server sends the texts to the toxicity API on Apify, and returns the scores.
- The toxicity API runs the Detoxify model. You pay for each call through your Apify account.

## Requirements

- Python 3.9 or later, or Docker
- An Apify API token in the `APIFY_TOKEN` environment variable

To get a token, open the Apify Console. Then go to **Settings** > **API & Integrations**.

## Installation

### Python

1. Clone the repository:

   ```bash
   git clone https://github.com/koyourmoon/perspective-api-alternative-mcp.git
   ```

2. Add the server to the configuration of your MCP client:

   ```json
   {
     "mcpServers": {
       "perspective-api-alternative": {
         "command": "python",
         "args": ["/path/to/perspective-api-alternative-mcp/server.py"],
         "env": { "APIFY_TOKEN": "<APIFY_TOKEN>" }
       }
     }
   }
   ```

### Docker

1. Build the image:

   ```bash
   docker build -t perspective-api-alternative-mcp .
   ```

2. Add the server to the configuration of your MCP client:

   ```json
   {
     "mcpServers": {
       "perspective-api-alternative": {
         "command": "docker",
         "args": ["run", "-i", "--rm", "-e", "APIFY_TOKEN", "perspective-api-alternative-mcp"],
         "env": { "APIFY_TOKEN": "<APIFY_TOKEN>" }
       }
     }
   }
   ```

## Tool: analyze_toxicity

| Parameter | Type | Description |
|---|---|---|
| `texts` | array of strings, required | 1 to 100 English texts to score |
| `attributes` | array of strings | Attributes to return. The default is all six. |
| `threshold` | number | `TOXICITY` score at which a text is flagged. The default is 0.5. |

Example result for one text:

```json
{
  "results": [
    {
      "text": "You are an idiot.",
      "scores": { "TOXICITY": 0.98, "INSULT": 0.95, "PROFANITY": 0.62 },
      "flagged": true,
      "billed_units": 1
    }
  ]
}
```

If a text looks non-English, the result has a `warning` field. The scores for that text are not reliable.

## Environment variables

| Name | Required | Description |
|---|---|---|
| `APIFY_TOKEN` | Yes, for `tools/call` | Your Apify API token |
| `PERSPECTIVE_ALT_URL` | No | A different URL for the toxicity API |

## Prices

- $0.50 for 1,000 text units. A text unit is each started 1,000 characters of a text. Most comments are 1 unit.
- Lower prices for Apify Bronze, Silver and Gold plans.
- The first call after an idle period of 60 seconds can take 10 to 30 seconds (cold start).

## Remote connection (optional)

You can also connect your MCP client directly to the toxicity API. This connection does not use `server.py`.

| Item | Value |
|---|---|
| Transport | Streamable HTTP |
| URL | `https://koyourmoon--perspective-api-alternative.apify.actor/mcp` |
| Authentication | `Authorization: Bearer <APIFY_TOKEN>` |

## Files

| File | Content |
|---|---|
| `server.py` | The MCP server |
| `Dockerfile` | The container image for the server |
| `glama.json` | The maintainer data for Glama |
| `server.json` | The entry for the official MCP Registry |

## Links

- Apify Store page: https://apify.com/koyourmoon/perspective-api-alternative
- Batch Actor for large jobs: https://apify.com/koyourmoon/toxicity-detector

## License

MIT. This project is not affiliated with Google or Jigsaw. "Perspective API" is a trademark of Google LLC.
