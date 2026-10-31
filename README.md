# Jarvis AI

An open-source, JARVIS-style assistant that talks to your GitHub. Bring your own brain: local models via Ollama or any OpenAI-compatible API.

## Quick start

```bash
git clone https://github.com/<you>/jarvis-ai && cd jarvis-ai
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # add your GITHUB_TOKEN, choose your model
jarvis
```

For a fully local setup: install [Ollama](https://ollama.com), run `ollama pull qwen2.5:7b`, and keep the defaults in `.env`.

## Voice mode (v0.2): "Hey Jarvis"

```bash
pip install -e ".[voice]"
mkdir voices && cd voices
curl -L -O https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx
curl -L -O https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json
cd .. && jarvis --voice
```

Say **"Hey Jarvis"**, wait for "Yes, sir?", then speak. Try "Good morning, brief me" or "Power down" to exit.
Spoken confirmation is required before any action that writes to GitHub.

## What it can do

- List unread notifications
- Repo info, open PRs, CI status
- Create issues (asks for your confirmation first)
- Status briefing (time, machine health, GitHub), system status, open web pages

Try: *"What's the CI status of owner/repo?"* or *"Open an issue in owner/repo about flaky tests."*

## Security

- Use a **fine-grained** GitHub token with the minimum scopes. Start read-only.
- Tools marked `writes=True` always require confirmation.
- Never commit `.env`.

## Roadmap

- [x] v0.1 Text CLI, tool calling, GitHub tools
- [x] v0.2 Voice: openWakeWord + faster-whisper + Piper, British butler persona
- [ ] v0.3 Memory (SQLite), config file, more tools
- [ ] v0.4 Web/desktop UI, calendar/email integrations

## License

MIT
