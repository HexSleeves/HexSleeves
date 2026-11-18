"""The Actions GITHUB_TOKEN gets "Resource not accessible by integration" from the
GraphQL queries github-readme-stats needs, so these cards use the public REST API.
Colors are mid-tones so the cards read on both GitHub themes without a light/dark pair.
"""

import json
import os
import textwrap
import urllib.request
from datetime import date
from pathlib import Path

USER = "HexSleeves"
PINS = {
    "tailscale-mcp": "MCP server that lets AI agents drive Tailscale's CLI and REST API.",
    "inkwell": "Markdown publishing platform in Rust, built end to end by AI agents on Paperclip.",
    "dvr": "jj-powered daemon that records every state of your working copy so agents can rewind it.",
    "skills": "The agent skills I use every day, installable with npx skills.",
}
CAREER_START = 2016
OUT = Path(__file__).resolve().parent.parent / "profile"

TITLE, TEXT, ICON, EDGE = "#8B5CC7", "#7D8F89", "#C9971C", "#7D8F8955"
LANG_COLORS = {"TypeScript": "#3178C6", "Rust": "#DEA584", "Go": "#00ADD8",
               "Python": "#3572A5", "Shell": "#89E051", "JavaScript": "#F1E05A"}
FONT = "font-family: 'Segoe UI', Ubuntu, -apple-system, Helvetica, Arial, sans-serif;"


def get(path):
    req = urllib.request.Request(f"https://api.github.com{path}",
                                 headers={"Accept": "application/vnd.github+json"})
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(width, height, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">'
            f'<style>text {{ {FONT} }}</style>'
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{EDGE}"/>'
            f'{body}</svg>\n')


def pin(repo, blurb):
    lines = textwrap.wrap(blurb, 52, max_lines=2, placeholder="...")
    body = [f'<text x="20" y="34" fill="{TITLE}" font-size="16" font-weight="600">{esc(repo["name"])}</text>']
    body += [f'<text x="20" y="{60 + i * 18}" fill="{TEXT}" font-size="13">{esc(l)}</text>' for i, l in enumerate(lines)]
    x = 20
    if lang := repo["language"]:
        body.append(f'<circle cx="{x + 6}" cy="106" r="6" fill="{LANG_COLORS.get(lang, TEXT)}"/>')
        body.append(f'<text x="{x + 18}" y="111" fill="{TEXT}" font-size="13">{esc(lang)}</text>')
        x += 30 + len(lang) * 8
    body.append(f'<text x="{x}" y="111" fill="{ICON}" font-size="13">★ {repo["stargazers_count"]}</text>')
    return card(400, 130, f'{repo["name"]}: {blurb}', "".join(body))


def stats(user, repos):
    own = [r for r in repos if not r["fork"]]
    rows = [
        ("Stars earned", sum(r["stargazers_count"] for r in own)),
        ("Original repos", len(own)),
        ("Followers", user["followers"]),
        ("Years shipping", date.today().year - CAREER_START),
    ]
    body = [f'<text x="24" y="38" fill="{TITLE}" font-size="18" font-weight="600">Character stats</text>']
    for i, (k, v) in enumerate(rows):
        y = 72 + i * 24
        body.append(f'<text x="24" y="{y}" fill="{TEXT}" font-size="14">{k}</text>')
        body.append(f'<text x="276" y="{y}" fill="{ICON}" font-size="14" font-weight="700" text-anchor="end">{v}</text>')
    return card(300, 165, "GitHub stats for " + USER, "".join(body))


def main():
    user = get(f"/users/{USER}")
    repos, page = [], 1
    while batch := get(f"/users/{USER}/repos?per_page=100&type=owner&page={page}"):
        repos += batch
        page += 1
    by_name = {r["name"]: r for r in repos}
    (OUT / "stats.svg").write_text(stats(user, repos), encoding="utf-8")
    for name, blurb in PINS.items():
        (OUT / f"pin-{name}.svg").write_text(pin(by_name[name], blurb), encoding="utf-8")


if __name__ == "__main__":
    main()
