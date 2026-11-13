"""
update_profile.py — redraws the progress card and the Learning Log on my profile.

How it works (run by .github/workflows/update-profile.yml every day and on every push):
  1. Read my numbers from progress.toml (the file I edit by hand).
  2. Ask the GitHub API about my practice repo: which weekNN folders exist,
     how many commits it has, and what the latest commits say.
  3. Draw two SVG pictures of the progress card (dark + light theme).
  4. Rewrite the Learning Log section of README.md between two marker comments.

Uses only the Python standard library, so there is nothing to install.
If the API can't be reached (e.g. running on my laptop), it just uses progress.toml.
"""

import json
import os
import re
import sys
import tomllib                     # reads .toml files (built into Python 3.11+)
import urllib.request
from datetime import datetime, timezone
from html import escape             # makes text safe to put inside SVG/HTML
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # the repo folder
USER = os.environ.get("GH_USER", "0001appiagyeisn")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


# ── 1. GitHub API helper ──────────────────────────────────────────────────────
def api(path):
    """GET https://api.github.com/<path>. Returns (data, headers) or (None, {})."""
    req = urllib.request.Request("https://api.github.com/" + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-progress-script")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp), dict(resp.headers)
    except Exception as err:                      # no internet / rate limit / 404
        print(f"  (API skipped for {path}: {err})")
        return None, {}


def practice_repo_facts(repo):
    """Latest week folder, total commit count and recent commits of the practice repo."""
    facts = {"latest_week": None, "commits": None, "recent": []}

    contents, _ = api(f"repos/{USER}/{repo}/contents")
    if isinstance(contents, list):
        weeks = [int(m.group(1)) for item in contents if item.get("type") == "dir"
                 for m in [re.fullmatch(r"week0*(\d+)", item["name"], re.I)] if m]
        if weeks:
            facts["latest_week"] = max(weeks)

    # per_page=1 trick: the "last" page number in the Link header = number of commits
    one, headers = api(f"repos/{USER}/{repo}/commits?per_page=1")
    if one is not None:
        link = headers.get("Link") or headers.get("link") or ""
        last = re.search(r"[?&]page=(\d+)>; rel=\"last\"", link)
        facts["commits"] = int(last.group(1)) if last else len(one)

    recent, _ = api(f"repos/{USER}/{repo}/commits?per_page=10")
    if isinstance(recent, list):
        for c in recent:
            facts["recent"].append({
                "date": c["commit"]["author"]["date"][:10],
                "msg": c["commit"]["message"].splitlines()[0],
                "url": c["html_url"],
                "repo": repo,
            })
    return facts


# ── 2. Drawing the card ──────────────────────────────────────────────────────
# One look for both GitHub themes: the card brings its own dark green panel (matches the banner).
GHANA = dict(bg="url(#pbg)", border="#f2b70559", text="#ffffff", muted="#8fb3a3",
             track="#17352b", green="#7ee2a8", gold="#f2b705", tile="#ffffff0d")
THEMES = {"dark": GHANA, "light": GHANA}
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
W = 840


def card_svg(cfg, facts, theme):
    t = THEMES[theme]
    j = cfg["journey"]
    stages, skills = cfg.get("stages", []), cfg.get("skills", [])

    week = max(j.get("current_week", 1), facts["latest_week"] or 0)
    done = j.get("weeks_completed", 0)
    total = j.get("plan_weeks", 104)
    commits = facts["commits"] if facts["commits"] is not None else "—"
    pct = done / total if total else 0
    updated = datetime.now(timezone.utc).strftime("%d %b %Y")

    out = []
    add = out.append

    skill_rows = (len(skills) + 1) // 2
    H = 372 + skill_rows * 30 + 28
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" role="img" aria-label="{escape(j["title"])}: week {week} of {total}">')
    add(f"""<style>
  .pulse {{ animation: pulse 1.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .35; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.35); }} }}
</style>""")
    add('<defs><linearGradient id="pbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#041f17"/>'
        '<stop offset="1" stop-color="#0d1b2a"/></linearGradient></defs>')
    add(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>')

    # Header
    add(f'<text x="28" y="44" font-size="22" font-weight="700" fill="{t["text"]}">{escape(j["title"])}</text>')
    add(f'<text x="28" y="68" font-size="14" fill="{t["muted"]}">Now: {escape(j.get("focus", ""))}</text>')
    add(f'<text x="{W-28}" y="44" font-size="22" font-weight="700" fill="{t["gold"]}" text-anchor="end">Week {week}</text>')
    add(f'<text x="{W-28}" y="68" font-size="14" fill="{t["muted"]}" text-anchor="end">of {total} · started {escape(j.get("started", ""))}</text>')

    # Stat tiles
    tiles = [(str(done), "weeks completed"), (f'{j.get("streak_days", 0)} days', "study streak"),
             (str(commits), "commits to ml-journey"), (str(sum(1 for s in stages if s.get("status") in ("done", "now"))) + f"/{len(stages)}", "roadmap stages started")]
    tw, gap, y0 = (W - 56 - 3 * 14) / 4, 14, 88
    for i, (val, label) in enumerate(tiles):
        x = 28 + i * (tw + gap)
        add(f'<rect x="{x:.1f}" y="{y0}" width="{tw:.1f}" height="70" rx="8" fill="{t["tile"]}" stroke="{t["border"]}"/>')
        add(f'<text x="{x+16:.1f}" y="{y0+36}" font-size="26" font-weight="700" fill="{t["text"]}">{escape(val)}</text>')
        add(f'<text x="{x+16:.1f}" y="{y0+56}" font-size="12.5" fill="{t["muted"]}">{escape(label)}</text>')

    # Overall bar
    by = 186
    add(f'<text x="28" y="{by}" font-size="13" fill="{t["muted"]}">Overall plan</text>')
    add(f'<text x="{W-28}" y="{by}" font-size="13" fill="{t["muted"]}" text-anchor="end">{pct*100:.0f}% · {total-done} weeks to go</text>')
    add(f'<rect x="28" y="{by+10}" width="{W-56}" height="10" rx="5" fill="{t["track"]}"/>')
    add(f'<rect x="28" y="{by+10}" width="{max(10, (W-56)*pct):.1f}" height="10" rx="5" fill="{t["green"]}"/>')

    # Roadmap timeline
    ty = 262
    add(f'<text x="28" y="{ty-24}" font-size="13" font-weight="600" fill="{t["text"]}">Roadmap</text>')
    n = max(len(stages), 1)
    step = (W - 56 - 80) / max(n - 1, 1)
    xs = [68 + i * step for i in range(n)]
    if n > 1:
        add(f'<line x1="{xs[0]}" y1="{ty}" x2="{xs[-1]}" y2="{ty}" stroke="{t["track"]}" stroke-width="4" stroke-linecap="round"/>')
    for x, s in zip(xs, stages):
        st = s.get("status", "later")
        if st == "done":
            add(f'<circle cx="{x:.1f}" cy="{ty}" r="10" fill="{t["green"]}"/>')
            add(f'<path d="M{x-4:.1f} {ty} l3 3 l6 -6" stroke="{t["bg"]}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
        elif st == "now":
            add(f'<circle class="pulse" cx="{x:.1f}" cy="{ty}" r="13" fill="{t["gold"]}" opacity=".35"/>')
            add(f'<circle cx="{x:.1f}" cy="{ty}" r="8" fill="{t["gold"]}"/>')
        elif st == "next":
            add(f'<circle cx="{x:.1f}" cy="{ty}" r="8" fill="{t["bg"]}" stroke="{t["gold"]}" stroke-width="2.5"/>')
        else:
            add(f'<circle cx="{x:.1f}" cy="{ty}" r="7" fill="{t["bg"]}" stroke="{t["muted"]}" stroke-width="2"/>')
        color = t["text"] if st in ("done", "now") else t["muted"]
        add(f'<text x="{x:.1f}" y="{ty+32}" font-size="12.5" fill="{color}" text-anchor="middle">{escape(s["name"])}</text>')
        tag = {"done": "done", "now": "in progress", "next": "next up", "later": ""}[st]
        if tag:
            add(f'<text x="{x:.1f}" y="{ty+48}" font-size="11" fill="{t["gold"] if st != "done" else t["green"]}" text-anchor="middle">{tag}</text>')

    # Skills (two columns of 5-segment meters)
    sy = 372
    add(f'<text x="28" y="{sy-14}" font-size="13" font-weight="600" fill="{t["text"]}">Skill levels</text>')
    add(f'<text x="{W-28}" y="{sy-14}" font-size="12" fill="{t["muted"]}" text-anchor="end">self-rated 1–5 · goes up as I learn</text>')
    colw = (W - 56 - 40) / 2
    for i, s in enumerate(skills):
        col, row = i % 2, i // 2
        x, y = 28 + col * (colw + 40), sy + row * 30
        add(f'<text x="{x:.1f}" y="{y+13}" font-size="13.5" fill="{t["text"]}">{escape(s["name"])}</text>')
        lvl = max(0, min(5, int(s.get("level", 0))))
        for k in range(5):
            segx = x + colw - 5 * 36 + k * 36
            fill = t["green"] if k < lvl else t["track"]
            add(f'<rect x="{segx:.1f}" y="{y+3}" width="30" height="10" rx="3" fill="{fill}"/>')

    add(f'<text x="{W-28}" y="{H-14}" font-size="11" fill="{t["muted"]}" text-anchor="end">'
        f'auto-updated {updated} · edit progress.toml to change</text>')
    add("</svg>")
    return "\n".join(out)


# ── 3. Learning Log in README ────────────────────────────────────────────────
def learning_log(facts, max_items):
    items = facts["recent"][:max_items]
    if not items:
        return "_The log fills in automatically once the Action runs._"
    lines = []
    for c in items:
        msg = c["msg"] if len(c["msg"]) <= 72 else c["msg"][:69] + "..."
        msg = msg.replace("|", "/").replace("<", "&lt;")
        lines.append(f'- `{c["date"]}` · [{escape(msg)}]({c["url"]}) <sub>in {c["repo"]}</sub>')
    return "\n".join(lines)


def achievements_svg(cfg):
    """Game-style card: unlocked achievements glow gold, locked ones show a lock and a progress bar."""
    items = cfg.get("achievements", [])
    j = cfg["journey"]
    W, ROWH, top = 840, 62, 104
    rows = (len(items) + 1) // 2
    H = top + rows * ROWH + 14
    done = sum(1 for a in items if a.get("done"))
    gold, mint, sub, muted = "#f2b705", "#7ee2a8", "#cfe9dc", "#8fb3a3"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Achievements: {done} of {len(items)} unlocked">',
         '<defs><linearGradient id="ag" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#041f17"/><stop offset="1" stop-color="#0d1b2a"/></linearGradient>'
         f'<linearGradient id="ab" x1="0" x2="1"><stop offset="0" stop-color="{mint}"/><stop offset="1" stop-color="{gold}"/></linearGradient>'
         '<style>.sh { animation: sh 2.6s ease-in-out infinite } @keyframes sh { 0%,100% { opacity: .25 } 50% { opacity: .7 } }</style></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="url(#ag)" stroke="{gold}" stroke-opacity=".35"/>',
         f'<text x="28" y="44" font-size="20" font-weight="800" fill="#ffffff">Achievements</text>',
         f'<text x="{W-28}" y="44" font-size="15" font-weight="700" fill="{gold}" text-anchor="end">{done} / {len(items)} unlocked</text>',
         f'<rect x="28" y="62" width="{W-56}" height="8" rx="4" fill="#17352b"/>',
         f'<rect x="28" y="62" width="{max(8, (W-56) * done / max(1, len(items))):.1f}" height="8" rx="4" fill="url(#ab)"/>']
    colw = (W - 56 - 24) / 2
    for i, a in enumerate(items):
        x, y = 28 + (i % 2) * (colw + 24), top + (i // 2) * ROWH
        cx, cy = x + 22, y + 20
        if a.get("done"):
            o.append(f'<circle class="sh" cx="{cx:.0f}" cy="{cy}" r="21" fill="{gold}"/>')
            o.append(f'<circle cx="{cx:.0f}" cy="{cy}" r="17" fill="{gold}"/>')
            o.append(f'<g transform="translate({cx:.0f} {cy})" fill="#041f17"><path d="M-7 -8h14v5a7 7 0 0 1-14 0z"/>'
                     '<path d="M-7 -6h-3a3 3 0 0 0 3 6M7 -6h3a3 3 0 0 1-3 6" fill="none" stroke="#041f17" stroke-width="1.8"/>'
                     '<rect x="-1.5" y="3" width="3" height="4"/><rect x="-5" y="7" width="10" height="2.5" rx="1"/></g>')
            name_col, sub_col = "#ffffff", sub
        else:
            o.append(f'<circle cx="{cx:.0f}" cy="{cy}" r="17" fill="#ffffff" fill-opacity=".05" stroke="{muted}" stroke-opacity=".4"/>')
            o.append(f'<g transform="translate({cx:.0f} {cy})"><rect x="-6" y="-2" width="12" height="9" rx="2" fill="{muted}"/>'
                     f'<path d="M-3.5 -2v-3a3.5 3.5 0 0 1 7 0v3" fill="none" stroke="{muted}" stroke-width="2"/></g>')
            name_col, sub_col = sub, muted
        o.append(f'<text x="{x+52:.0f}" y="{y+16}" font-size="14.5" font-weight="700" fill="{name_col}">{escape(a["name"])}</text>')
        target = a.get("target")
        if target and not a.get("done"):
            cur = j.get("streak_days", 0) if a.get("current") == "streak" else a.get("current", 0)
            bw = colw - 52 - 64
            o.append(f'<rect x="{x+52:.0f}" y="{y+26}" width="{bw:.0f}" height="6" rx="3" fill="#17352b"/>')
            o.append(f'<rect x="{x+52:.0f}" y="{y+26}" width="{max(6, bw * min(1, cur / target)):.1f}" height="6" rx="3" fill="{gold}"/>')
            o.append(f'<text x="{x+52+bw+10:.0f}" y="{y+33}" font-size="12" font-weight="700" fill="{gold}">{cur}/{target}</text>')
        else:
            o.append(f'<text x="{x+52:.0f}" y="{y+35}" font-size="12.5" fill="{sub_col}">{escape(a.get("sub", ""))}</text>')
    o.append("</svg>")
    return "\n".join(o)


def replace_between(text, start, end, new):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pattern.sub(start + "\n" + new + "\n" + end, text)


def ask_numbers():
    """When I run this on my laptop, ask for today's streak and weeks done, and save them in progress.toml.
    Press Enter to keep a number as it is. (Skipped automatically when GitHub Actions runs it.)"""
    if not sys.stdin.isatty():
        return
    path = ROOT / "progress.toml"
    text = path.read_text(encoding="utf-8")
    for key, question in [("streak_days", "Study streak today (days)"), ("weeks_completed", "Weeks completed")]:
        current = re.search(rf"^{key} = (\d+)", text, re.M).group(1)
        answer = input(f"{question} [{current}]: ").strip()
        if answer.isdigit():
            text = re.sub(rf"^{key} = \d+", f"{key} = {answer}", text, count=1, flags=re.M)
    path.write_text(text, encoding="utf-8")


def main():
    ask_numbers()
    cfg = tomllib.loads((ROOT / "progress.toml").read_text(encoding="utf-8"))
    repo = cfg["journey"].get("practice_repo", "ml-journey")
    print(f"Reading {USER}/{repo} ...")
    facts = practice_repo_facts(repo)
    print("  facts:", {k: v for k, v in facts.items() if k != "recent"}, f"recent={len(facts['recent'])}")

    (ROOT / "assets").mkdir(exist_ok=True)
    for theme in THEMES:
        (ROOT / "assets" / f"progress-{theme}.svg").write_text(card_svg(cfg, facts, theme), encoding="utf-8")
    (ROOT / "assets" / "achievements.svg").write_text(achievements_svg(cfg), encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    log = learning_log(facts, cfg.get("log", {}).get("max_items", 6))
    text = replace_between(text, "<!--LOG:START-->", "<!--LOG:END-->", log)
    readme.write_text(text, encoding="utf-8")
    print("Done: assets/progress-*.svg and README Learning Log updated.")


if __name__ == "__main__":
    main()
