---
name: Streamlit preview verification
description: Product stack constraint and preview verification lesson for SmartQuote AI.
---

Keep SmartQuote AI in Python and Streamlit. Do not replace it with React to fit the original workspace template.

**Why:** The user explicitly selected Streamlit and reiterated this constraint when requesting preview repair.

**How to apply:** Fix routing and run configuration around the existing app rather than rebuilding its interface.

A healthy Streamlit process or HTTP response is not sufficient evidence that the Replit preview works. Verify the public routed URL renders the dashboard and establishes its WebSocket connection.

**Why:** The initial build was reported successful based only on syntax and startup logs, but the workspace router had no root route to Streamlit. A stale process also survived removal of the old workflow.

**How to apply:** Check routing and process ownership when repairing preview failures; test the rendered dashboard through the public preview before claiming success.
