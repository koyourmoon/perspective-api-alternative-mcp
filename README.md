# Perspective API Alternative: Toxicity Detection MCP Server

This MCP server gives AI agents a tool to examine text before they publish it. The tool returns six scores from 0 to 1 and a flagged value for each text:

- `TOXICITY`, `SEVERE_TOXICITY`, `INSULT`, `PROFANITY`, `THREAT`, `IDENTITY_ATTACK`

The model is the open-source Detoxify model. It is not an LLM. Thus, the same text always gets the same score. English only.

The same server is also a direct replacement for the Google Perspective API. Google stops the Perspective API on December 31, 2026.

This repository holds the data that MCP directories show. The server runs on Apify: https://apify.com/koyourmoon/perspective-api-alternative

## Connection

| Item | Value |
|---|---|
| Transport | Streamable HTTP |
| URL | `https://koyourmoon--perspective-api-alternative.apify.actor/mcp` |
| Authentication | `Authorization: Bearer <APIFY_TOKEN>` |

Get an Apify token in the Apify Console: **Settings** > **API & Integrations**.

## Client configuration (example)

```json
{
  "mcpServers": {
    "perspective-api-alternative": {
      "type": "http",
      "url": "https://koyourmoon--perspective-api-alternative.apify.actor/mcp",
      "headers": { "Authorization": "Bearer <APIFY_TOKEN>" }
    }
  }
}
```

## Prices

- $0.50 for 1,000 text units. A text unit is each started 1,000 characters of a text. Most comments are 1 unit.
- Lower prices for Apify Bronze, Silver and Gold plans.
- The first request after an idle period of 60 seconds can take 10 to 30 seconds (cold start).

## Links

- Apify Store page: https://apify.com/koyourmoon/perspective-api-alternative
- Batch Actor for large jobs: https://apify.com/koyourmoon/toxicity-detector
