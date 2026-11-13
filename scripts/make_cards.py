"""make_cards.py — draws the static cards on my profile (about-me code card, project cards, divider).

Run it after editing the text below:  python scripts/make_cards.py
Only the standard library is used.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'Fira Code', Consolas, 'Courier New', monospace"
C = dict(bg1="#050816", bg2="#0b1533", gold="#22d3ee", mint="#a78bfa", sub="#c7d2fe",
         muted="#94a3b8", line="#7dd3fc", red="#ff7b72", white="#ffffff")

PANEL = (f'<linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg1"]}"/>'
         f'<stop offset="1" stop-color="{C["bg2"]}"/></linearGradient>'
         f'<linearGradient id="gb" x1="0" x2="1"><stop offset="0" stop-color="{C["mint"]}"/>'
         f'<stop offset="1" stop-color="{C["gold"]}"/></linearGradient>')


# ── 1. About me, written as a Python class ───────────────────────────────────
# Each line is a list of (colour, text) pieces. K = keyword, N = name, S = string, P = punctuation.
K, N, S, P, M, F = C["gold"], C["white"], C["mint"], C["sub"], C["muted"], "#79c0ff"
CODE = [
    [(K, "class "), (F, "Kwadwo"), (P, "("), (N, "Student"), (P, ", "), (N, "Developer"), (P, "):")],
    [(M, '    """CS student who learns by building real things."""')],
    [(N, "    based_in   "), (P, "= "), (S, '"Kumasi, Ghana"')],
    [(N, "    studying   "), (P, "= "), (S, '"BSc Computer Science @ KTU"')],
    [(N, "    building   "), (P, "= ["), (S, '"online stores"'), (P, ", "), (S, '"study apps"'), (P, ", "), (S, '"CampusMart"'), (P, "]")],
    [(N, "    learning   "), (P, "= ["), (S, '"Python"'), (P, ", "), (S, '"maths for ML"'), (P, ", "), (S, '"C++"'), (P, ", "), (S, '"algorithms"'), (P, "]")],
    [(N, "    goal       "), (P, "= "), (S, '"MSc Machine Learning & Robotics"')],
    [(N, "    off_screen "), (P, "= ["), (S, '"keyboard"'), (P, ", "), (S, '"chess"'), (P, "]")],
    [],
    [(K, "    def "), (F, "motto"), (P, "("), (N, "self"), (P, "):")],
    [(K, "        return "), (S, '"Build real things. Understand every line."')],
]


def about_card():
    W, LH, top = 840, 25, 70
    H = top + LH * len(CODE) + 8
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" role="img" '
         f'aria-label="About me, written as a Python class">',
         f'<defs>{PANEL}<style>.cur {{ animation: c 1s steps(1) infinite }} @keyframes c {{ 50% {{ opacity: 0 }} }}</style></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="url(#pg)" stroke="{C["gold"]}" stroke-opacity=".35"/>',
         f'<path d="M1 44H{W-1}" stroke="{C["line"]}" stroke-opacity=".15"/>',
         '<circle cx="26" cy="23" r="6" fill="#ff5f57"/><circle cx="46" cy="23" r="6" fill="#febc2e"/><circle cx="66" cy="23" r="6" fill="#28c840"/>',
         f'<text x="{W/2}" y="28" font-size="13" fill="{C["muted"]}" text-anchor="middle">about_me.py</text>',
         f'<text x="{W-24}" y="28" font-size="12" fill="{C["gold"]}" text-anchor="end">Python 3</text>']
    for i, parts in enumerate(CODE):
        y = top + i * LH
        o.append(f'<text x="34" y="{y}" font-size="13" fill="{C["muted"]}" fill-opacity=".55" text-anchor="end">{i+1}</text>')
        if parts:
            spans = "".join(f'<tspan fill="{col}">{escape(t)}</tspan>' for col, t in parts)
            o.append(f'<text x="52" y="{y}" font-size="15" xml:space="preserve">{spans}</text>')
    last = top + (len(CODE) - 1) * LH
    o.append(f'<rect class="cur" x="{52 + 9.05 * 59:.0f}" y="{last-14}" width="9" height="18" fill="{C["gold"]}"/>')
    o.append("</svg>")
    return "\n".join(o)


# ── 2. Project cards ─────────────────────────────────────────────────────────
ICONS = {
    "bag":   '<path d="M-11 -6h22l-2 17h-18z" fill="none" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/><path d="M-5 -6v-3a5 5 0 0 1 10 0v3" fill="none" stroke="{c}" stroke-width="2.2"/>',
    "cap":   '<path d="M-14 -2l14-7 14 7-14 7z" fill="none" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/><path d="M-8 1v6c4 4 12 4 16 0v-6M14 -2v8" fill="none" stroke="{c}" stroke-width="2.2"/>',
    "users": '<circle cx="-5" cy="-5" r="4.5" fill="none" stroke="{c}" stroke-width="2.2"/><circle cx="7" cy="-3" r="3.5" fill="none" stroke="{c}" stroke-width="2.2"/><path d="M-13 10c1-7 15-7 16 0M3 9c1-5 10-5 11 0" fill="none" stroke="{c}" stroke-width="2.2"/>',
    "compass": '<circle r="12" fill="none" stroke="{c}" stroke-width="2.2"/><path d="M5 -5l-3 8-8 3 3-8z" fill="{c}"/>',
    "code":  '<path d="M-6 -8l-8 8 8 8M6 -8l8 8-8 8M3 -11l-6 22" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
    "tiles": '<rect x="-12" y="-12" width="10" height="10" rx="2" fill="none" stroke="{c}" stroke-width="2.2"/><rect x="2" y="-12" width="10" height="10" rx="2" fill="{c}"/><rect x="-12" y="2" width="10" height="10" rx="2" fill="{c}"/><rect x="2" y="2" width="10" height="10" rx="2" fill="none" stroke="{c}" stroke-width="2.2"/>',
}
STATUS = {"live": ("LIVE", C["mint"]), "inuse": ("IN USE", C["mint"]), "building": ("BUILDING", C["gold"]),
          "growing": ("GROWS WEEKLY", C["gold"]), "client": ("CLIENT WORK", C["mint"])}

PROJECTS = [
    ("kd-wisdom", "bag", "KD Wisdom Enterprise", "live",
     ["Online store for a menswear shop at Kejetia:", "live MoMo + card checkout, AI product autofill."],
     ["Supabase", "Paystack", "Gemini API", "Netlify"]),
    ("campusmart", "cap", "CampusMart", "building",
     ["Marketplace for students across Ghana's", "universities, with escrow payments."],
     ["Full-stack", "Paystack", "Escrow"]),
    ("study-squad", "users", "Study Squad", "inuse",
     ["Study app for my peer group: 3 learning", "tracks, shared progress, a Stuck board."],
     ["TypeScript", "Supabase", "GitHub login"]),
    ("ml-journey-app", "compass", "ML Journey app", "inuse",
     ["My tracker for a 2-year ML + Robotics plan:", "weekly resources, tasks, streaks."],
     ["TypeScript", "Supabase", "Private"]),
    ("ml-journey", "code", "ml-journey", "growing",
     ["My practice code, one folder per week,", "pushed every study day."],
     ["Python", "Maths for ML", "Open source"]),
    ("client-sites", "tiles", "More client work", "client",
     ["Gyawus tile shop website and an", "ordering app for my church's Pathfinder club."],
     ["HTML", "CSS", "JavaScript"]),
]


def project_card(icon, title, status, desc, tags):
    W, H = 412, 176
    label, col = STATUS[status]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="{escape(title)}: {escape(" ".join(desc))}">',
         f'<defs>{PANEL}<style>.p {{ animation: p 1.8s ease-in-out infinite }} @keyframes p {{ 0%,100% {{ opacity: .3 }} 50% {{ opacity: 1 }} }}</style></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="url(#pg)" stroke="{C["gold"]}" stroke-opacity=".35"/>',
         f'<rect x="16" y="0" width="{W-32}" height="3" rx="1.5" fill="url(#gb)" opacity=".85"/>',
         f'<circle cx="44" cy="46" r="24" fill="{C["white"]}" fill-opacity=".06" stroke="{C["gold"]}" stroke-opacity=".3"/>',
         f'<g transform="translate(44 46)">{ICONS[icon].format(c=C["gold"])}</g>',
         f'<text x="82" y="42" font-size="18" font-weight="700" fill="{C["white"]}">{escape(title)}</text>']
    pw = len(label) * 7.8 + 30
    o.append(f'<rect x="82" y="51" width="{pw:.0f}" height="20" rx="10" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".5"/>')
    o.append(f'<circle class="p" cx="94" cy="61" r="3.5" fill="{col}"/>')
    o.append(f'<text x="103" y="65" font-size="10.5" font-weight="700" letter-spacing="1" fill="{col}">{label}</text>')
    for i, line in enumerate(desc):
        o.append(f'<text x="24" y="{98 + i*19}" font-size="13.5" fill="{C["sub"]}">{escape(line)}</text>')
    x = 24
    for t in tags:
        w = len(t) * 6.6 + 18
        o.append(f'<rect x="{x:.0f}" y="138" width="{w:.0f}" height="22" rx="6" fill="{C["white"]}" fill-opacity=".06" stroke="{C["line"]}" stroke-opacity=".25"/>')
        o.append(f'<text x="{x + w/2:.0f}" y="153" font-size="11.5" fill="{C["mint"]}" text-anchor="middle">{escape(t)}</text>')
        x += w + 8
    o.append("</svg>")
    return "\n".join(o)


# ── 3. Divider: a small animated neural network between the gradient lines ──
def divider():
    W, H, cy = 840, 84, 42
    layers = [[cy], [cy - 24, cy + 24], [cy - 32, cy, cy + 32], [cy - 24, cy + 24], [cy]]
    xs = [290, 350, 420, 490, 550]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="divider">',
         f'<defs><linearGradient id="dl" gradientUnits="userSpaceOnUse" x1="0" x2="{xs[0]-14}"><stop offset="0" stop-color="{C["mint"]}" stop-opacity="0"/>'
         f'<stop offset="1" stop-color="{C["gold"]}"/></linearGradient>'
         f'<linearGradient id="dr" gradientUnits="userSpaceOnUse" x1="{xs[-1]+14}" x2="{W}"><stop offset="0" stop-color="{C["gold"]}"/>'
         f'<stop offset="1" stop-color="{C["mint"]}" stop-opacity="0"/></linearGradient>'
         '<style>.n { animation: n 2.4s ease-in-out infinite } @keyframes n { 0%,100% { opacity: .55 } 50% { opacity: 1 } }</style></defs>',
         f'<path d="M0 {cy}H{xs[0]-14}" stroke="url(#dl)" stroke-width="2"/>',
         f'<path d="M{xs[-1]+14} {cy}H{W}" stroke="url(#dr)" stroke-width="2"/>']
    edges = []
    for i in range(len(layers) - 1):
        for y1 in layers[i]:
            for y2 in layers[i + 1]:
                edges.append(f"M{xs[i]} {y1}L{xs[i+1]} {y2}")
    o.append(f'<path d="{"".join(edges)}" stroke="{C["line"]}" stroke-opacity=".45" stroke-width="1.4" fill="none"/>')
    for path, dur, col in [(f"M{xs[0]} {cy}L{xs[1]} {cy-24}L{xs[2]} {cy+32}L{xs[3]} {cy-24}L{xs[4]} {cy}", 2.6, C["gold"]),
                           (f"M{xs[0]} {cy}L{xs[1]} {cy+24}L{xs[2]} {cy-32}L{xs[3]} {cy+24}L{xs[4]} {cy}", 3.2, C["mint"])]:
        o.append(f'<circle r="3.5" fill="{col}"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/></circle>')
    k = 0
    for x, ys in zip(xs, layers):
        for y in ys:
            mid = x == xs[2] and y == cy
            col = C["gold"] if (mid or x in (xs[0], xs[-1])) else C["mint"]
            o.append(f'<circle class="n" style="animation-delay:{k*.25:.2f}s" cx="{x}" cy="{y}" r="{8 if mid else 6}" '
                     f'fill="{C["bg1"]}" stroke="{col}" stroke-width="3"/>')
            k += 1
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    (ROOT / "assets" / "projects").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "about.svg").write_text(about_card(), encoding="utf-8")
    (ROOT / "assets" / "divider.svg").write_text(divider(), encoding="utf-8")
    for slug, *rest in PROJECTS:
        (ROOT / "assets" / "projects" / f"{slug}.svg").write_text(project_card(*rest), encoding="utf-8")
    print("Cards written to assets/")
