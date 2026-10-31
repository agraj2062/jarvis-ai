import json
from collections.abc import Callable

from openai import OpenAI

from .config import Config
from .tools import REGISTRY, load_all


def build_system(address: str) -> str:
    return (
        "You are J.A.R.V.I.S., a refined British AI butler and engineering partner. "
        f"Address the user as '{address}'. Your tone is calm, impeccably polite, and dryly witty, "
        "with understatement rather than jokes. Your replies are spoken aloud, so keep them to one "
        "to three short sentences, with no markdown, lists, or emoji. "
        "Use the provided tools for anything about the user's GitHub, machine, or schedule, "
        "and never invent data. If a tool fails, say so plainly. "
        "Offer one proactive suggestion when it is genuinely useful, otherwise don't."
    )



class Brain:
    def __init__(self, cfg: Config | None = None, confirm: Callable[[str], bool] | None = None):
        self.cfg = cfg or Config()
        self.client = OpenAI(base_url=self.cfg.base_url, api_key=self.cfg.api_key)
        self.confirm = confirm or (lambda _: False)  # deny writes by default
        load_all()
        self.messages: list[dict] = [
            {"role": "system", "content": build_system(self.cfg.address)}
        ]

    def _run_tool(self, call) -> str:
        tool = REGISTRY.get(call.function.name)
        if tool is None:
            return f"Unknown tool: {call.function.name}"
        try:
            args = json.loads(call.function.arguments or "{}")
        except json.JSONDecodeError:
            return "Invalid tool arguments."
        if tool.writes and not self.confirm(f"{tool.name}({args})"):
            return "The user declined this action."
        try:
            return str(tool.func(**args))
        except Exception as e:  # surface errors to the model, don't crash
            return f"Tool error: {e}"

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        schemas = [t.schema() for t in REGISTRY.values()]
        for _ in range(8):  # cap tool-call rounds
            resp = self.client.chat.completions.create(
                model=self.cfg.model, messages=self.messages, tools=schemas
            )
            msg = resp.choices[0].message
            self.messages.append(msg.model_dump(exclude_none=True))
            if not msg.tool_calls:
                return msg.content or ""
            for call in msg.tool_calls:
                self.messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": self._run_tool(call)}
                )
        return "I got stuck in a loop of tool calls. Try rephrasing."
