# Contributing

The easiest contribution is a new tool:

1. Create `jarvis/tools/your_tool.py`.
2. Decorate a function with `@tool("description", parameters_schema, writes=False)`.
3. Set `writes=True` for anything that changes external state (it will require user confirmation).
4. Add a test in `tests/` and open a PR.

Run `pip install -e ".[dev]"`, then `ruff check .` and `pytest` before submitting.
