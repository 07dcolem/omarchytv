# Voice assistant relay (`> ask` on the TV)

The TV recognises speech with Android's own recogniser and sends the text to the PC over
the paired link (event `ask`, see PROTOCOL.md §6). The PC asks an AI and streams the answer back
(`answer` chunks). The TV shows it and can read it aloud.
**The TV never contacts an AI service and never holds a key.**

## Which AI answers: signed-in tools first, keys last

The plugin reuses the AI tools you already use on the Omarchy PC, with their own login. You don't
have to create an API key. `omarchy-link ai providers` shows what it found. The same list is pushed to
the TV (`PUT /v1/ai/providers`), where Settings → Assistant lets you pick one.

| id | Kind | Uses | Detected when | Streaming | Notes |
|---|---|---|---|---|---|
| `claude-code` | cli | **Claude Code** `claude -p` (your Pro/Max login) | `claude` on PATH and its login file exists | yes | `--tools "" --strict-mcp-config --max-turns 1 --system-prompt …`; model `haiku` by default |
| `codex` | cli | **OpenAI Codex CLI** `codex exec --json` (your ChatGPT login) | `codex login status` succeeds | no (whole message) | `--sandbox read-only -c mcp_servers={}`, empty temp dir |
| `grok-cli` | cli | **xAI Grok Build CLI** `grok -p` (`grok login`) | `grok` on PATH and `~/.grok/auth.json` exists | no | `--max-turns 1 --no-memory --no-subagents --no-plan --disable-web-search` |
| `gemini-cli` | cli | **Gemini CLI** `gemini -p --output-format stream-json` | `gemini` on PATH and its Google login file exists | yes | Google moved free/Google One users to Antigravity CLI in June 2026 |
| `ollama` | local | **ollama** `/api/chat` on this PC (or `OLLAMA_HOST`) | the server answers and has a model | yes | no account at all |
| `claude-api` | api | Anthropic Messages API | `key` resolves | yes | fallback, needs a key |
| `grok-api` | api | xAI API `/v1/chat/completions` | `key` resolves | yes | fallback, needs a key |
| `chatgpt-api` | api | OpenAI API `/v1/chat/completions` | `key` resolves | yes | fallback, needs a key |
| `<your id>` | api | any OpenAI-compatible endpoint (LM Studio, llama.cpp, vLLM, OpenRouter…) | `baseUrl` + `model` set | yes | plain `http://` only to this PC or the LAN |
| — | — | **Grok Bot** (the Grok Bot assistant app) | never | — | **Unsupported.** Its only official way in is a webhook *routine*: a POST starts a run and returns 200 with no answer, and the result appears in the Grok Bot chat. There is no request/reply API. Its internal gateway is undocumented and would need its private token, so it is deliberately not used. |

Order: explicit entries in `assistant.json`, then auto-detected tools. CLI tools come first, then local, then API.
The first one is the default unless `default` says otherwise. The TV may pick any listed id for each question.

## `~/.config/omarchy-link/assistant.json` (optional)

Nothing is needed if a supported CLI is signed in. Example with every option:

```json
{
  "default": "claude-code",
  "autoDetect": true,
  "disabled": ["gemini_cli"],
  "memory": { "turns": 6, "minutes": 15 },
  "timeoutSeconds": 90,
  "providers": [
    { "type": "claude_code", "id": "claude-code", "model": "sonnet" },
    { "type": "codex", "id": "codex", "model": "gpt-6-luna" },
    { "type": "ollama", "id": "ollama", "model": "llama3.2" },
    { "type": "openai_compatible", "id": "lmstudio", "name": "LM Studio",
      "baseUrl": "http://192.168.1.20:1234/v1", "model": "qwen3-8b" },
    { "type": "xai_api", "id": "grok-api", "key": "env:XAI_API_KEY" },
    { "type": "anthropic_api", "id": "claude-api", "key": "file:~/.config/omarchy-link/keys/anthropic" },
    { "type": "openai_api", "id": "chatgpt-api", "key": "cmd:pass show openai" }
  ]
}
```

- `key` takes `env:NAME`, `file:PATH` (the file must be chmod 600) or `cmd:ARGV` (e.g. a password
  manager). A literal key is accepted only if assistant.json itself is chmod 600.
- `systemPrompt` replaces the built-in TV prompt: at most three short sentences, the user's
  language, plain text, no tools.
- `bin` points a CLI type at a specific binary. `name` changes the label shown on the TV.
- `minIntervalSeconds` (default 3) is the minimum gap between questions.
- `"assistant": false` in `config.json` turns the relay off. The TV then gets `answer_error disabled`.

## Memory

Each TV `session` keeps the last 6 question/answer pairs, in RAM only, for 15 minutes after its
last use (at most 32 sessions, about 6000 characters each). For CLI tools the history is passed
inside the prompt, so no CLI session files are created or resumed. Nothing is written to disk.

## Safety

The text comes from a microphone in the living room. Treat it as untrusted:

- Only a paired TV can send `ask` (authenticated, sealed socket). The PC opens no port.
- CLI agents run with tools off and MCP servers off, in an empty temporary directory, with stdin
  closed. They run in their own process group and are killed on timeout. Codex additionally runs in its read-only sandbox.
- Text is capped at 2000 characters. Answers are capped at 16 KiB and markdown is stripped.
  The rate limit is 1 question per 3 s and 20 per minute. Two questions can run at once at most.
- API keys stay on the PC. The TV sees provider ids, names and models only.

## Try it without a TV

```
omarchy-link ai providers
omarchy-link ai ask "what's a good film for tonight?"
omarchy-link ai ask --provider codex "e domani che tempo fa a Roma?"
```

## Adding a provider

Create `lib/omarchy_link/assistant/providers/<type>.py`:

```python
KIND, LABEL, STREAMING = "cli", "My AI", True

def available(cfg):            # -> {"model": ...} when usable now, else None
    ...

def ask(cfg, req):             # call req.delta(chunk) while streaming; return the full text
    # req.text, req.history, req.system, req.lang, req.flat_prompt(), req.transcript()
    # helpers: run_cli(argv, req, on_line), stream_http(url, headers, body, req, on_line)
    ...
```
