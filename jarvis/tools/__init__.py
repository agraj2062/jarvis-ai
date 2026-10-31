"""Tool registry. Drop a new .py file in this folder and decorate functions
with @tool(...) -- they are auto-discovered and offered to the LLM."""
import importlib
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass

EMPTY_PARAMS = {"type": "object", "properties": {}}


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    func: Callable
    writes: bool = False  # write tools require user confirmation

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


REGISTRY: dict[str, Tool] = {}


def tool(description: str, parameters: dict | None = None, writes: bool = False):
    def deco(fn: Callable) -> Callable:
        REGISTRY[fn.__name__] = Tool(
            fn.__name__, description, parameters or EMPTY_PARAMS, fn, writes
        )
        return fn

    return deco


def load_all() -> dict[str, Tool]:
    for mod in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{mod.name}")
    return REGISTRY
