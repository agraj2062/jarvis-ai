import requests

from ..config import Config
from . import tool

API = "https://api.github.com"
TIMEOUT = 15


def _headers() -> dict:
    token = Config().github_token
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set. See .env.example.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get(path: str, **params):
    r = requests.get(f"{API}{path}", headers=_headers(), params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


REPO = {
    "type": "object",
    "properties": {"repo": {"type": "string", "description": "owner/name, e.g. torvalds/linux"}},
    "required": ["repo"],
}


@tool("List the user's unread GitHub notifications.")
def list_notifications() -> str:
    items = _get("/notifications", per_page=15)
    if not items:
        return "No unread notifications."
    return "\n".join(
        f"- [{n['repository']['full_name']}] {n['subject']['type']}: {n['subject']['title']}"
        for n in items
    )


@tool("Get basic info about a GitHub repository.", REPO)
def repo_info(repo: str) -> str:
    d = _get(f"/repos/{repo}")
    return (
        f"{d['full_name']}: {d['description']}\n"
        f"Stars: {d['stargazers_count']}, open issues: {d['open_issues_count']}, "
        f"language: {d['language']}, default branch: {d['default_branch']}"
    )


@tool("List open pull requests in a repository.", REPO)
def list_open_prs(repo: str) -> str:
    prs = _get(f"/repos/{repo}/pulls", state="open", per_page=15)
    if not prs:
        return "No open pull requests."
    return "\n".join(f"- #{p['number']} {p['title']} (by {p['user']['login']})" for p in prs)


@tool(
    "Show the CI status of the latest commit on the default branch.",
    REPO,
)
def ci_status(repo: str) -> str:
    branch = _get(f"/repos/{repo}")["default_branch"]
    s = _get(f"/repos/{repo}/commits/{branch}/status")
    return f"Combined status on {branch}: {s['state']} ({s['total_count']} checks)"


@tool(
    "Create a new issue in a repository. Changes GitHub, so it needs user approval.",
    {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "owner/name"},
            "title": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["repo", "title"],
    },
    writes=True,
)
def create_issue(repo: str, title: str, body: str = "") -> str:
    r = requests.post(
        f"{API}/repos/{repo}/issues",
        headers=_headers(),
        json={"title": title, "body": body},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return f"Created issue #{r.json()['number']}: {r.json()['html_url']}"
