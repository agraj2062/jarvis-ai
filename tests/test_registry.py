from jarvis.tools import REGISTRY, load_all


def test_tools_autodiscovered():
    load_all()
    expected = {"list_notifications", "repo_info", "list_open_prs", "ci_status", "create_issue"}
    assert expected <= set(REGISTRY)


def test_write_tools_flagged():
    load_all()
    assert REGISTRY["create_issue"].writes is True
    assert REGISTRY["repo_info"].writes is False


def test_schema_shape():
    load_all()
    s = REGISTRY["repo_info"].schema()
    assert s["type"] == "function" and "repo" in s["function"]["parameters"]["properties"]


def test_system_tools_and_briefing():
    load_all()
    assert {"current_time", "system_status", "open_url", "briefing"} <= set(REGISTRY)
    assert "It is" in REGISTRY["current_time"].func()
    assert REGISTRY["open_url"].func("file:///etc/passwd").startswith("Only http")


def test_persona_uses_address():
    from jarvis.brain import build_system

    assert "'ma'am'" in build_system("ma'am")
