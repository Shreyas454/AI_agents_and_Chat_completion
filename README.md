# AI Agents & Chat Completion — Learning Journey

This repo is my progression from raw chat completion calls to fully tool-using
AI agents, using the [Groq](https://groq.com) API and Google's
[Agent Development Kit (ADK)](https://google.github.io/adk-docs/). Each file
maps to a concept I worked through, in order.

## 1. Chat completion basics

- [`tokens_demo.py`](tokens_demo.py) — same prompt at `max_completion_tokens` of 10, 50,
  and 200, to see the model's output get cut off mid-thought vs. finish naturally.
- [`tempreture_demo.py`](tempreture_demo.py) — same prompt run twice at `temperature=0`
  (identical output both times) and twice at `temperature=1.5` (different output each
  time). This is what taught me temperature controls randomness, not "creativity" in
  the abstract — `0` is deterministic, higher values sample more freely.
- [`roles_demo.py`](roles_demo.py) — the core lesson of the whole repo: **the API is
  stateless**. Asking "What is my name?" in a fresh call with no prior messages fails,
  even after telling the model my name one call earlier. Only resending the full
  message history (`user` → `assistant` → `user`) as the `messages` array gives the
  model memory. There's no session on the server side — the client owns the
  conversation.
- [`chatbot.py`](chatbot.py) — put that together into an actual REPL: a growing
  `conversation_history` list, a system prompt to give the bot a persona, plus
  `top_p` and `stop` sequences, and a streaming variant (`stream=True`) that prints
  tokens as they arrive instead of waiting for the full response.

## 2. Structured output

- [`structured_demo.py`](structured_demo.py) — instead of letting the model reply in
  free text, force it to return parseable JSON matching an exact schema
  (`response_format={"type": "json_object", ...}`). This is what makes an LLM usable
  as a function in a larger program: you stop parsing prose and start getting a
  `dict` back with `json.loads()`.

## 3. Tool calling

- [`tools_demo.py`](tools_demo.py) — the step from "the model talks" to "the model
  acts." Two fake tools (`get_weather`, `search_hotels`) are described to the model as
  JSON schemas. The model doesn't run them — it returns a `tool_calls` response asking
  *me* to run them, and I feed the result back in a `role: "tool"` message so it can
  use that data in its next reply. This request → execute → feed-back cycle, repeated
  in a loop, is the entire mechanism behind every agent below.

## 4. AI agents

An "agent" here is just: the tool-calling loop from step 3, running until the model
stops asking for tools and gives a final answer, instead of stopping after one round.

- [`coding_agent_cli/`](coding_agent_cli/) — a hand-rolled coding agent with tools to
  read, list, edit, and search files in a workspace, wired to a `while` loop that
  keeps calling the model until it returns a plain-text answer instead of a
  `tool_calls` response ([`agent.py`](coding_agent_cli/agent.py)).
- [`ADK/`](ADK/) — the same idea (`weather_agent`, `hotel_agent`, `coding_agent`)
  rebuilt on top of Google's ADK framework instead of hand-rolled loop code.

## Two coding agents, two approaches

The repo has two coding agents on purpose, to see the same problem solved with and
without a framework:

| | [`coding_agent_cli/`](coding_agent_cli/) | [`ADK/coding_agent/`](ADK/coding_agent/) |
|---|---|---|
| **Framework** | None — plain `groq` SDK | Google ADK (`google.adk.agents.llm_agent.Agent`) |
| **The agent loop** | Written by hand in [`agent.py`](coding_agent_cli/agent.py): a `while` loop that calls `client.chat.completions.create(...)`, checks `finish_reason == "tool_calls"`, executes the matching Python function, appends a `role: "tool"` message with the result, and loops back — capped by `MAX_ITERATIONS` | Handled internally by ADK's `Agent` runtime — I just declare `tools=[...]` and ADK runs the request → execute → feed-back cycle itself |
| **Tool schemas** | Written by hand as raw JSON in `TOOLS_SCHEMA` (name, description, JSON-schema parameters) | Generated automatically by ADK from each tool function's **docstring and type hints** — no schema written by me |
| **Model access** | Talks to Groq directly via the `groq` SDK (`Groq().chat.completions.create`) | Goes through ADK's `LiteLlm(model="groq/llama-3.3-70b-versatile")` adapter, which is what lets ADK talk to non-Gemini models |
| **Conversation history** | A plain Python list I build and pass in on every call, persisted to disk myself via `sessions.py` | Managed internally by ADK's session system |
| **What this taught me** | Exactly what an "agent" is under the hood — there's no magic, just a loop and JSON | How much of that loop is boilerplate you can hand to a framework once you understand what it's doing |

In short: `coding_agent_cli` is the agent loop built from first principles so I could
see every moving part; `ADK/coding_agent` is the same agent with the loop, schema
generation, and session handling delegated to a framework, once I trusted what was
happening underneath.

## Setup

```bash
pip install groq python-dotenv google-adk
```

Each subfolder expects its own `.env` with the relevant API key(s) (`GROQ_API_KEY`,
and for ADK's Gemini-based agents, `GOOGLE_API_KEY`) — these are gitignored and not
included in this repo.
