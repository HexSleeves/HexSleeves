"""Run `python3 scripts/hero.py` from the repo root to rewrite assets/hero-{dark,light}.svg.

Every glyph is its own <text> so the grid stays aligned whatever monospace font
the viewer has. The resting state is the finished map, so prefers-reduced-motion
viewers (animations off) still see everything.
"""

from pathlib import Path

CW, CH = 10, 20
PAD_X, MAP_TOP = 30, 116
COLS, ROWS = 84, 8
CYCLE = 18.0
WALK_START, WALK_END = 1.2, 11.0

THEMES = {
    "dark": dict(bg="#12262A", edge="#24423F", wall="#6FA287", floor="#3C5C58",
                 hall="#5A7A6F", text="#E9E2D0", dim="#8FA59E", gold="#F2C14E",
                 purple="#B48BE0", coq="#F08A6C"),
    "light": dict(bg="#EEF2EC", edge="#C9D6CE", wall="#2F6B4F", floor="#A9BDB3",
                  hall="#7E978B", text="#1F2A2A", dim="#5B6E68", gold="#A6740B",
                  purple="#6B3FA0", coq="#C2452D"),
}

ROOMS = [
    dict(name="Bayer", x=1, y=1, w=20, h=6, items={(6, 3): "$", (14, 5): "!", (9, 2): "="}),
    dict(name="Liatrio", x=31, y=0, w=20, h=6, items={(36, 2): "?", (46, 2): "["}),
    dict(name="Adobe", x=61, y=2, w=22, h=6, items={(70, 4): "&", (79, 6): ">"}),
]
DOORS = [(20, 3), (31, 3), (50, 4), (61, 4)]
HALLS = [(c, 3) for c in range(21, 31)] + [(c, 4) for c in range(51, 61)]


def walk_path():
    cells = [(c, 4) for c in range(4, 20)]
    cells += [(20, 3)] + [(c, 3) for c in range(21, 32)]
    cells += [(c, 3) for c in range(32, 41)] + [(c, 4) for c in range(41, 62)]
    cells += [(c, 4) for c in range(62, 70)] + [(c, 5) for c in range(70, 79)]
    return cells


def grid():
    g = {}
    for r in ROOMS:
        x0, y0, x1, y1 = r["x"], r["y"], r["x"] + r["w"] - 1, r["y"] + r["h"] - 1
        for c in range(x0, x1 + 1):
            g[(c, y0)] = g[(c, y1)] = ("-", "wall", r["name"])
        for y in range(y0 + 1, y1):
            g[(x0, y)] = g[(x1, y)] = ("|", "wall", r["name"])
            for c in range(x0 + 1, x1):
                g[(c, y)] = (".", "floor", r["name"])
        for pos, ch in r["items"].items():
            g[pos] = (ch, "gold" if ch in "$>" else "purple", r["name"])
    for d in DOORS:
        g[d] = ("+", "gold", None)
    for h in HALLS:
        g[h] = ("#", "hall", None)
    return g


def t_pct(t):
    return f"{t / CYCLE * 100:.2f}%"


def step_keyframes(name, cells, offset_steps=0):
    span = WALK_END - WALK_START
    n = len(cells)
    frames = [f"0% {{ transform: {xy(cells[0])}; }}"]
    for i in range(n):
        j = max(0, i - offset_steps)
        frames.append(f"{t_pct(WALK_START + span * i / (n - 1))} {{ transform: {xy(cells[j])}; }}")
    frames.append(f"100% {{ transform: {xy(cells[max(0, n - 1 - offset_steps)])}; }}")
    return f"@keyframes {name} {{ {' '.join(frames)} }}"


def xy(cell):
    return f"translate({cell[0] * CW}px, {cell[1] * CH}px)"


def arrival_time(room_name):
    cells = walk_path()
    room = next(r for r in ROOMS if r["name"] == room_name)
    i = next(k for k, (c, _) in enumerate(cells) if c >= room["x"])
    return WALK_START + (WALK_END - WALK_START) * i / (len(cells) - 1)


def reveal(name, at):
    a, b = t_pct(at), t_pct(min(at + 0.4, CYCLE - 0.5))
    return f"@keyframes {name} {{ 0%, {a} {{ opacity: 0; }} {b}, 97% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(theme):
    p = THEMES[theme]
    width = PAD_X * 2 + COLS * CW
    log_top = MAP_TOP + ROWS * CH + 28
    t_liatrio, t_adobe = arrival_time("Liatrio"), arrival_time("Adobe")
    path = walk_path()

    css = [
        f"text {{ font-family: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-size: 16px; fill: {p['text']}; white-space: pre; }}",
        f".wall {{ fill: {p['wall']}; }} .floor {{ fill: {p['floor']}; }} .hall {{ fill: {p['hall']}; }}",
        f".gold {{ fill: {p['gold']}; }} .purple {{ fill: {p['purple']}; }} .dim {{ fill: {p['dim']}; }}",
        f".label {{ fill: {p['purple']}; font-weight: 700; font-size: 14px; }}",
        f".hero {{ fill: {p['gold']}; font-weight: 700; }} .coq {{ fill: {p['coq']}; font-weight: 700; }}",
        ".anim { animation-duration: %ss; animation-iteration-count: infinite; animation-fill-mode: both; }" % CYCLE,
        ".walker { animation-timing-function: step-end; }",
        step_keyframes("walk", path),
        step_keyframes("follow", path, offset_steps=1),
        reveal("revealLiatrio", t_liatrio - 0.6),
        reveal("revealAdobe", t_adobe - 0.6),
        reveal("log1", 0.4),
        reveal("log2", t_liatrio),
        reveal("log3", t_adobe + 0.4),
        reveal("log4", WALK_END + 0.8),
        "#at { animation-name: walk; } #coq { animation-name: follow; }",
        "#room-Liatrio { animation-name: revealLiatrio; } #room-Adobe { animation-name: revealAdobe; }",
        "#log1 { animation-name: log1; } #log2 { animation-name: log2; } #log3 { animation-name: log3; } #log4 { animation-name: log4; }",
        "@keyframes blink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }",
        ".cursor { animation: blink 1.1s step-end infinite; }",
        "@media (prefers-reduced-motion: reduce) { .anim, .cursor { animation: none; } "
        f"#at {{ transform: {xy(path[-1])}; }} #coq {{ transform: {xy(path[-2])}; }} }}",
    ]

    groups = {r["name"]: [] for r in ROOMS}
    groups[None] = []
    for (c, y), (ch, cls, room) in sorted(grid().items()):
        x = PAD_X + c * CW + CW / 2
        groups[room].append(f'<text x="{x}" y="{MAP_TOP + y * CH}" class="{cls}" text-anchor="middle">{esc(ch)}</text>')
    for r in ROOMS:
        groups[r["name"]].append(
            f'<text x="{PAD_X + r["x"] * CW}" y="{MAP_TOP + (r["y"] - 1) * CH + 6}" class="label">{r["name"]}</text>')

    body = []
    for name in ("Bayer", None):
        body += groups[name]
    for name in ("Liatrio", "Adobe"):
        body.append(f'<g id="room-{name}" class="anim">{"".join(groups[name])}</g>')

    body.append(f'<g id="coq" class="anim walker"><text x="{PAD_X + CW / 2}" y="{MAP_TOP}" class="coq" text-anchor="middle">c</text></g>')
    body.append(f'<g id="at" class="anim walker"><text x="{PAD_X + CW / 2}" y="{MAP_TOP}" class="hero" text-anchor="middle">@</text></g>')

    log = [
        ("log1", "Welcome, Jacob. You start at Bayer with a 22-app Nx monorepo and a Terraform map."),
        ("log2", "You enter Liatrio and build an AI software factory. The PRs start fixing themselves."),
        ("log3", "You arrive at Adobe. The agents here are friendly."),
        ("log4", "Your pet rooster crows: cocorico!"),
    ]
    for i, (lid, msg) in enumerate(log):
        body.append(f'<text id="{lid}" class="anim" x="{PAD_X}" y="{log_top + i * 22}">{esc(msg)}</text>')

    status_y = log_top + 4 * 22 + 18
    body.append(f'<line x1="{PAD_X}" x2="{width - PAD_X}" y1="{status_y - 22}" y2="{status_y - 22}" stroke="{p["edge"]}"/>')
    body.append(f'<text x="{PAD_X}" y="{status_y}" class="dim">Jacob the Engineer   St:Go  Dx:TypeScript  In:Rust  Wis:agents</text>')
    body.append(f'<text x="{PAD_X}" y="{status_y + 22}" class="dim">Dlvl:3 Adobe   Pet:rooster   HP:caffeinated   T:2016   Lafayette, LA</text>')

    height = status_y + 22 + 30
    head = [
        f'<text x="{PAD_X}" y="46" style="font-size:28px;font-weight:700">Jacob LeCoq</text>',
        f'<text x="{PAD_X}" y="70" class="dim" style="font-size:14px">software engineer, AI agents, roguelikes</text>',
        f'<text x="{width - PAD_X}" y="46" class="dim" text-anchor="end" style="font-size:14px">~/HexSleeves $ play<tspan class="cursor gold">█</tspan></text>',
    ]

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Jacob LeCoq. A roguelike map: @ walks from Bayer through Liatrio to Adobe, followed by a pet rooster.">'
        f'<style>{" ".join(css)}</style>'
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="{p["bg"]}" stroke="{p["edge"]}" stroke-width="2"/>'
        + "".join(head) + "".join(body) + "</svg>\n"
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    for theme in THEMES:
        (out / f"hero-{theme}.svg").write_text(render(theme))
