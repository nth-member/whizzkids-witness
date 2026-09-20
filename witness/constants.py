"""Settings shared by the command line and the research layer."""

MODEL = "claude-opus-5"

# The server-side search tool.  Held here so the CLI can name a default model
# without importing the SDK: reading the ledger must work on a machine that has
# no API key and no anthropic package installed.
SEARCH_TOOL = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 8,
}
