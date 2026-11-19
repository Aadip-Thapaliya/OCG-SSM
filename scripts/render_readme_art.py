"""Draw the SVG figures used by README.md into assets/readme/.

Every number here is copied from the README's results tables (which in turn
come from the stage summaries in results/roadmap/). Nothing is computed from
model runs, so this script needs only the Python standard library:

    python -m scripts.render_readme_art
"""

from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "readme"

C = {
    "bg": "#0e1a2f", "bg2": "#15243e", "line": "#2a3d61", "grid": "#1f3050",
    "cream": "#f3e9d2", "muted": "#a9b8cf", "dim": "#6b7f9e",
    "orange": "#f0803c", "amber": "#e3a24f", "teal": "#5fb3a6", "red": "#e5684f", "gray": "#8796ad",
}
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
CSS = f"""
.s{{font-family:{SANS}}} .m{{font-family:{MONO}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes flow{{to{{stroke-dashoffset:-40}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.fade{{animation:fade .8s ease-out both}} .rise{{animation:rise .7s ease-out both}}
.flow{{stroke-dasharray:8 6;animation:flow 1.6s linear infinite}}
"""
VERDICT = {"S": ("Supported", C["teal"]), "P": ("Partly supported", C["amber"]), "N": ("Not supported", C["red"])}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def svg(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><style>{CSS}</style>'
            f'<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg2"]}"/>'
            f'<stop offset="1" stop-color="{C["bg"]}"/></linearGradient>'
            f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["muted"]}"/></marker>'
            f'<marker id="ao" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["orange"]}"/></marker></defs>'
            f'<rect x="4" y="4" width="{w - 8}" height="{h - 8}" rx="16" fill="url(#pg)" stroke="{C["line"]}"/>'
            f"{body}</svg>\n")


def t(x, y, s, size=16, fill=None, cls="s", anchor="start", weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill or C["cream"]}" '
            f'text-anchor="{anchor}"{w} {extra}>{esc(s)}</text>')


def box(x, y, w, h, title, sub=None, stroke=None, delay=0.0):
    out = (f'<g class="rise" style="animation-delay:{delay:.2f}s">'
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["bg"]}" stroke="{stroke or C["line"]}" stroke-width="1.6"/>'
           + t(x + w / 2, y + (h / 2 + 6 if not sub else h / 2 - 4), title, 17, anchor="middle", weight=700))
    if sub:
        lines = sub if isinstance(sub, list) else [sub]
        for i, line in enumerate(lines):
            out += t(x + w / 2, y + h / 2 + 18 + i * 18, line, 13.5, C["muted"], "m", "middle")
    return out + "</g>"


# ---------------------------------------------------------------- hero ----

def hero() -> str:
    W, H = 1200, 440
    # lag graph: columns t-2, t-1, t ; 4 variables
    cols = {"t-2": 760, "t-1": 900, "t": 1080}
    ys = [130, 200, 270, 340]
    edges = [("t-2", 0, 1), ("t-1", 0, 0), ("t-1", 1, 2), ("t-2", 2, 3), ("t-1", 3, 3), ("t-1", 2, 1), ("t-2", 1, 0)]
    out = []
    for i, (c, j, k) in enumerate(edges):
        x1, y1, x2, y2 = cols[c] + 18, ys[j], cols["t"] - 20, ys[k]
        col = C["orange"] if i % 3 == 0 else C["teal"]
        out.append(f'<path d="M{x1},{y1} C{(x1 + x2) / 2},{y1} {(x1 + x2) / 2},{y2} {x2},{y2}" fill="none" '
                   f'stroke="{col}" stroke-width="2.4" opacity=".85" class="flow" marker-end="url(#ao)" '
                   f'style="animation-delay:{i * .2:.1f}s"/>')
    for name, x in cols.items():
        out.append(t(x, 96, f"x({name})" if name != "t" else "x(t)", 16, C["muted"], "m", "middle"))
        for j, y in enumerate(ys):
            live = name == "t"
            out.append(f'<circle cx="{x}" cy="{y}" r="17" fill="{C["bg"]}" stroke="{C["teal"] if live else C["dim"]}" stroke-width="2.4"/>')
            out.append(t(x, y + 5, f"x{j + 1}", 13, C["cream"], "m", "middle"))
    out.append(f'<circle cx="{cols["t"]}" cy="{ys[0]}" r="25" fill="none" stroke="{C["orange"]}" stroke-width="2">'
               f'<animate attributeName="r" values="18;30" dur="1.8s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>')
    out.append(t(920, 396, "edges only point forward in time: acyclic by construction", 14, C["dim"], "m", "middle"))

    chips = ["bachelor's thesis", "pure PyTorch", "pre-registered gates", "96 tests"]
    x, ch = 50, []
    for i, c in enumerate(chips):
        w = len(c) * 16 * 0.61 + 28
        ch.append(f'<g class="rise" style="animation-delay:{.6 + i * .1:.1f}s"><rect x="{x:.0f}" y="300" width="{w:.0f}" height="34" rx="17" '
                  f'fill="{C["bg"]}" stroke="{C["line"]}"/>' + t(x + w / 2, 322, c, 16, C["cream"], "m", "middle") + "</g>")
        x += w + 10
    body = (t(50, 84, "// bachelor's thesis · University of Europe for Applied Sciences · 2026", 16, C["orange"], "m")
            + t(50, 168, "OCG-SSM", 84, weight=800, cls="s fade")
            + t(50, 214, "Online Causal-Graph-Conditioned", 28, C["cream"])
            + t(50, 250, "State-Space Forecasting", 28, C["cream"])
            + "".join(ch)
            + t(50, 380, "Learn a sparse lagged graph. Let it decide which variables", 17, C["muted"])
            + t(50, 404, "may talk inside a state-space model. Keep learning online.", 17, C["muted"])
            + "".join(out))
    return svg(W, H, body, "OCG-SSM: Online Causal-Graph-Conditioned State-Space Forecasting")


# ------------------------------------------------------------ verdicts ----

CLAIMS = [
    ("Stationary synthetic data", [("S", "Recovers the true lagged graph"), ("S", "Beats dense, random, identity"),
                                   ("S", "Benefit grows with less data"), ("P", "Within 5% of oracle"),
                                   ("N", "Matches a direct VAR")]),
    ("After a graph switch (online)", [("S", "Online beats a frozen model"), ("N", "Online learned beats online dense"),
                                       ("N", "Tracks the new graph"), ("N", "Detector: no false alarms")]),
    ("Real data (ETTh1, ETTh2)", [("S", "Beats dense at H24"), ("P", "Beats dense at H96"),
                                  ("N", "Competitive with DLinear")]),
]


def icon(kind: str, cx: float, cy: float) -> str:
    col = VERDICT[kind][1]
    g = f'<circle cx="{cx}" cy="{cy}" r="12" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-width="2"/>'
    if kind == "S":
        g += f'<path d="M{cx - 5},{cy} l4,4 l7,-8" fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    elif kind == "P":
        g += f'<path d="M{cx},{cy - 8} A8,8 0 0 1 {cx},{cy + 8} Z" fill="{col}"/>'
    else:
        g += f'<path d="M{cx - 5},{cy - 5} l10,10 M{cx + 5},{cy - 5} l-10,10" stroke="{col}" stroke-width="2.6" stroke-linecap="round"/>'
    return g


def verdicts() -> str:
    W, H = 1200, 450
    counts = {"S": 0, "P": 0, "N": 0}
    for _, rows in CLAIMS:
        for k, _ in rows:
            counts[k] += 1
    total = sum(counts.values())
    out = [t(40, 56, "12 claims tested", 30, weight=800),
           t(310, 56, "supported = frozen gate passed or 95% CI excludes no effect", 15, C["muted"], "m")]
    x0, bw, x = 40, 1120, 40
    for i, k in enumerate("SPN"):
        w = bw * counts[k] / total
        label, col = VERDICT[k]
        out.append(f'<rect x="{x:.1f}" y="80" width="{w - 4:.1f}" height="44" rx="10" fill="{col}" fill-opacity=".9" '
                   f'style="transform-box:fill-box;transform-origin:left;animation:grow .8s ease-out {i * .2:.1f}s both"/>')
        short = {"S": "supported", "P": "partly", "N": "not supported"}[k]
        out.append(t(x + 18, 109, f"{counts[k]}  {short}", 19, C["bg"], weight=800, extra=f'style="animation:fade .5s {.6 + i * .2:.1f}s both"'))
        x += w
    cw = (1120 - 2 * 20) / 3
    for ci, (group, rows) in enumerate(CLAIMS):
        gx = 40 + ci * (cw + 20)
        out.append(f'<rect x="{gx:.0f}" y="150" width="{cw:.0f}" height="290" rx="12" fill="{C["bg"]}" stroke="{C["line"]}"/>')
        out.append(t(gx + 20, 184, group, 17, C["orange"], weight=700))
        for ri, (k, claim) in enumerate(rows):
            y = 226 + ri * 46
            out.append(f'<g class="rise" style="animation-delay:{.4 + ci * .15 + ri * .07:.2f}s">'
                       + icon(k, gx + 32, y - 6) + t(gx + 56, y, claim, 16.5) + "</g>")
    return svg(W, H, "".join(out), "12 claims tested: 5 supported, 2 partly supported, 5 not supported")


# -------------------------------------------------------- architecture ----

def architecture() -> str:
    W, H = 1200, 560
    o = []
    # main row
    my, mh = 236, 92
    boxes = [(40, 180, "Input window", ["(L, D)"]), (250, 150, "RevIN", ["normalise"]),
             (430, 300, "Graph-conditioned SSM", ["h_t[i] per variable", "scan: O(D²N) per step"]),
             (760, 170, "Lag + forecast", ["heads"]), (960, 200, "Forecast", ["(H, D), de-normalised"])]
    for i, (x, w, ti, sub) in enumerate(boxes):
        o.append(box(x, my, w, mh, ti, sub, C["teal"] if i == 2 else None, .1 * i))
    for (x, w, *_), (nx, *_rest) in zip(boxes, boxes[1:]):
        o.append(f'<line x1="{x + w + 4}" y1="{my + mh / 2}" x2="{nx - 6}" y2="{my + mh / 2}" stroke="{C["muted"]}" stroke-width="2" class="flow" marker-end="url(#ar)"/>')
    # graph learner above
    o.append(box(380, 60, 400, 100, "GraphLearner", ["logits Lg (K, D, D)", "A = sigmoid(Lg / τ)  →  EMA"], C["orange"], .3))
    o.append(f'<line x1="580" y1="164" x2="580" y2="{my - 6}" stroke="{C["orange"]}" stroke-width="2.4" class="flow" marker-end="url(#ao)"/>')
    o.append(t(592, 204, "adjacency mask A  (only edges couple states)", 14, C["orange"], "m"))
    # structural loop below
    o.append(box(250, 404, 330, 100, "Structural score S(G)", ["masked linear VAR", "+ λ · sparsity"], None, .5))
    o.append(box(640, 404, 300, 100, "RegimeDetector", ["median / MAD z-score", "k consecutive steps"], None, .6))
    o.append(f'<line x1="584" y1="454" x2="634" y2="454" stroke="{C["muted"]}" stroke-width="2" class="flow" marker-end="url(#ar)"/>')
    o.append(f'<path d="M944,454 H1110 V110 H786" fill="none" stroke="{C["orange"]}" stroke-width="2.2" class="flow" marker-end="url(#ao)"/>')
    o.append(t(1100, 200, "on detection:", 14, C["orange"], "m", "end"))
    o.append(t(1100, 220, "graph lr × boost", 14, C["orange"], "m", "end"))
    o.append(t(1100, 240, "S5b: EMA reset", 14, C["orange"], "m", "end"))
    o.append(t(1100, 260, "+ replay refit", 14, C["orange"], "m", "end"))
    o.append(f'<path d="M130,{my + mh + 4} V454 H244" fill="none" stroke="{C["muted"]}" stroke-width="2" class="flow" marker-end="url(#ar)"/>')
    o.append(t(40, 44, "graph and forecaster train with separate optimizers", 14, C["dim"], "m"))
    o.append(t(40, 536, "prequential: every window is forecast first; its targets are used for training only once observed",
               14.5, C["muted"], "m"))
    return svg(W, H, "".join(o), "OCG-SSM architecture: graph learner, graph-conditioned SSM, regime detector loop")


# -------------------------------------------------------------- stages ----

STAGES = [
    ("Development", [("S1", "PASS", "oracle / DirectVAR 1.029"), ("S1b", "none", "no gain"),
                     ("S3", "PASS", "graph converged"), ("S2", "PASS", "learned ≈ oracle"),
                     ("S2d", "info", "gain grows as data shrinks")]),
    ("Held-out synthetic", [("S4", "FAIL", "0 of 4 · switch in test slice"), ("S4b", "PASS", "4 of 4 · stationary"),
                            ("S4b-hard", "PASS", "4 of 4 · D20, 600 steps")]),
    ("Online, after a switch", [("S5", "FAIL", "vs dense online"), ("S5b", "FAIL", "EMA reset + replay")]),
    ("Real data", [("S6", "mixed", "beats dense 3/4 · DLinear 3/4"), ("S6b", "skip", "not run")]),
]
STATUS = {"PASS": C["teal"], "FAIL": C["red"], "none": C["gray"], "info": C["amber"], "mixed": C["amber"], "skip": C["dim"]}


def stages() -> str:
    W, H = 1200, 440
    o = []
    cw, gap = 268, 16
    for gi, (phase, items) in enumerate(STAGES):
        gx = 40 + gi * (cw + gap)
        o.append(t(gx, 54, f"{gi + 1:02d}", 15, C["dim"], "m"))
        o.append(t(gx + 34, 54, phase, 18, C["orange"], weight=700))
        o.append(f'<line x1="{gx}" y1="68" x2="{gx + cw}" y2="68" stroke="{C["line"]}"/>')
        for si, (name, status, note) in enumerate(items):
            y = 84 + si * 66
            col = STATUS[status]
            dash = ' stroke-dasharray="5 5"' if status == "skip" else ""
            label = {"none": "NO GAIN", "info": "TREND", "mixed": "MIXED", "skip": "NOT RUN"}.get(status, status)
            o.append(f'<g class="rise" style="animation-delay:{gi * .15 + si * .08:.2f}s">'
                     f'<rect x="{gx}" y="{y}" width="{cw}" height="56" rx="10" fill="{C["bg"]}" stroke="{col}" stroke-opacity=".7"{dash}/>'
                     f'<rect x="{gx}" y="{y}" width="6" height="56" rx="3" fill="{col}"/>'
                     + t(gx + 20, y + 24, name, 18, weight=800, cls="m")
                     + t(gx + cw - 14, y + 24, label, 13, col, "m", "end", 700)
                     + t(gx + 20, y + 45, note, 14, C["muted"]) + "</g>")
    o.append(t(40, 418, "every held-out stage ran under a gates.yaml committed before its data was built; outcomes reported as they came out",
               14, C["dim"], "m"))
    return svg(W, H, "".join(o), "Stage map: S1 to S6b with pass and fail outcomes")


# -------------------------------------------------------------- forest ----

def forest(title: str, rows: list, panels: list, label_w: int = 380, note: str = "") -> str:
    """rows: list of (label, kind) where kind is 'group' or 'row'.
    panels: dicts with title, lo, hi, ref, ticks, fmt, vals (one (est, lo, hi) per 'row')."""
    W = 1200
    rh, top = 36, 118
    H = top + rh * len(rows) + 70
    o = [t(40, 50, title, 22, weight=800)]
    if note:
        o.append(t(40, 76, note, 14, C["muted"], "m"))
    px0 = 40 + label_w
    pw_total = W - 40 - px0
    gap = 30
    pw = (pw_total - gap * (len(panels) - 1)) / len(panels)
    y = top
    for label, kind in rows:
        if kind == "group":
            o.append(t(40, y + 24, label, 15, C["orange"], "m", weight=700))
        else:
            o.append(t(56, y + 24, label, 15.5, C["cream"]))
        y += rh
    for pi, p in enumerate(panels):
        x0 = px0 + pi * (pw + gap)

        def sx(v, x0=x0, p=p):
            return x0 + (v - p["lo"]) / (p["hi"] - p["lo"]) * pw
        o.append(t(x0 + pw / 2, top - 14, p["title"], 15, C["muted"], "m", "middle", 700))
        o.append(f'<rect x="{x0}" y="{top}" width="{pw:.0f}" height="{rh * len(rows)}" fill="{C["bg"]}" opacity=".55" rx="6"/>')
        for tk in p["ticks"]:
            o.append(f'<line x1="{sx(tk):.1f}" y1="{top}" x2="{sx(tk):.1f}" y2="{top + rh * len(rows)}" stroke="{C["grid"]}"/>')
            o.append(t(sx(tk), top + rh * len(rows) + 22, p["fmt"](tk), 13, C["dim"], "m", "middle"))
        rx = sx(p["ref"])
        o.append(f'<line x1="{rx:.1f}" y1="{top - 4}" x2="{rx:.1f}" y2="{top + rh * len(rows) + 4}" stroke="{C["cream"]}" stroke-opacity=".6" stroke-dasharray="4 4"/>')
        y, vi = top, 0
        for label, kind in rows:
            if kind == "row":
                v = p["vals"][vi]
                vi += 1
                if v is not None:
                    est, lo, hi = v
                    col = C["teal"] if hi < p["ref"] else (C["red"] if lo > p["ref"] else C["gray"])
                    cy = y + rh / 2
                    clip = lambda z: min(max(z, p["lo"]), p["hi"])
                    o.append(f'<g>'
                             f'<line x1="{sx(clip(lo)):.1f}" y1="{cy}" x2="{sx(clip(hi)):.1f}" y2="{cy}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'
                             f'<path d="M{sx(est):.1f},{cy - 8} l7,8 l-7,8 l-7,-8 z" fill="{col}"/></g>')
            y += rh
    ly = H - 26
    lx = 40
    for lab, col in (("CI below reference: A better", C["teal"]),
                     ("CI includes reference: no supported difference", C["gray"]),
                     ("CI above reference: A worse", C["red"])):
        o.append(f'<path d="M{lx + 7},{ly - 13} l6,6 l-6,6 l-6,-6 z" fill="{col}"/>')
        o.append(t(lx + 20, ly - 2, lab, 13, C["muted"], "m"))
        lx += len(lab) * 13 * .61 + 50
    return svg(W, H, "".join(o), title)


def r3(v):
    return f"{v:.2f}"


def forest_synthetic() -> str:
    data = [
        ("Development (S1, S2, S2d)", None),
        ("S1  oracle / DirectVAR", (1.0288, 1.0198, 1.0380)),
        ("S2  learned / oracle", (1.0059, 1.0036, 1.0083)),
        ("S2  learned / dense", (0.9839, 0.9811, 0.9868)),
        ("S2  learned / random", (0.8360, 0.8232, 0.8497)),
        ("S2  learned / identity", (0.8243, 0.8107, 0.8384)),
        ("S2  learned / DirectVAR", (1.0349, 1.0269, 1.0428)),
        ("S2d learned / dense  (D20, 600 steps)", (0.9712, 0.9680, 0.9743)),
        ("Held-out, stationary (S4b)", None),
        ("S4b learned / dense", (0.9857, 0.9841, 0.9874)),
        ("S4b learned / random", (0.8295, 0.8227, 0.8363)),
        ("S4b learned / identity", (0.8093, 0.8021, 0.8166)),
        ("Held-out, data-scarce (S4b-hard)", None),
        ("S4b-hard learned / dense", (0.9735, 0.9715, 0.9754)),
        ("S4b-hard learned / random", (0.8534, 0.8471, 0.8601)),
        ("S4b-hard learned / identity", (0.8518, 0.8453, 0.8588)),
        ("Held-out, switch inside test slice (S4)", None),
        ("S4  learned / dense", (0.9999, 0.9974, 1.0024)),
    ]
    rows = [(l, "group" if v is None else "row") for l, v in data]
    panel = {"title": "H1 MSE ratio, 95% CI", "lo": 0.78, "hi": 1.06, "ref": 1.0,
             "ticks": [0.8, 0.85, 0.9, 0.95, 1.0, 1.05], "fmt": r3, "vals": [v for _, v in data if v is not None]}
    return forest("Synthetic data: ratio A / B at horizon 1 (below 1 = A better)", rows, [panel], 420,
                  "paired circular block-bootstrap 95% intervals, 2000 resamples")


def forest_real() -> str:
    cases = ["ETTh1, H24", "ETTh1, H96", "ETTh2, H24", "ETTh2, H96"]
    dense = [(0.9731, 0.9622, 0.9834), (0.9967, 0.9898, 1.0034), (0.9907, 0.9839, 0.9973), (0.9824, 0.9726, 0.9922)]
    ident = [(0.9479, 0.9305, 0.9668), (0.9753, 0.9667, 0.9845), (0.9828, 0.9761, 0.9893), (1.0250, 1.0159, 1.0333)]
    dlin = [(1.733, 1.624, 1.856), (1.553, 1.453, 1.652), (1.153, 1.114, 1.197), (0.9836, 0.9418, 1.0293)]
    rows = [(c, "row") for c in cases]
    small = {"lo": 0.92, "hi": 1.04, "ref": 1.0, "ticks": [0.94, 0.97, 1.0, 1.03], "fmt": r3}
    panels = [dict(small, title="learned / dense", vals=dense), dict(small, title="learned / identity", vals=ident),
              {"title": "learned / DLinear", "lo": 0.9, "hi": 1.9, "ref": 1.0, "ticks": [1.0, 1.25, 1.5, 1.75],
               "fmt": r3, "vals": dlin}]
    return forest("Real data: MSE ratios with 95% CI (below 1 = learned better)", rows, panels, 200,
                  "chronological splits · block of 96 windows · learned / DLinear on its own wider scale")


def forest_switch() -> str:
    data = [
        ("S5, first 200 windows after the switch", None),
        ("learned + detector  −  frozen learned", (-1.661, -1.831, -1.502)),
        ("learned + detector  −  dense online", (0.117, 0.026, 0.211)),
        ("S5b, EMA reset + replay", None),
        ("learned_fast  −  dense online", (1.084, 0.846, 1.334)),
        ("Pooled S5 + S5b, 10 seeds (post hoc, descriptive)", None),
        ("before the switch", (-0.573, -0.646, -0.507)),
        ("first 200 windows after", (0.496, 0.369, 0.633)),
        ("windows 200-495 after", (1.391, 1.205, 1.574)),
    ]
    rows = [(l, "group" if v is None else "row") for l, v in data]
    panel = {"title": "mean-MSE difference A − B  (× 10⁻³)", "lo": -2.0, "hi": 2.0, "ref": 0.0,
             "ticks": [-2, -1, 0, 1, 2], "fmt": lambda v: f"{v:+.0f}" if v else "0", "vals": [v for _, v in data if v is not None]}
    return forest("After an abrupt graph switch: differences with 95% CI (below 0 = A better)", rows, [panel], 470,
                  "online, prequential evaluation · 5 held-out seeds per stage")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    figs = {"hero.svg": hero(), "claims.svg": verdicts(), "architecture.svg": architecture(),
            "stages.svg": stages(), "forest-synthetic.svg": forest_synthetic(),
            "forest-real.svg": forest_real(), "forest-switch.svg": forest_switch()}
    for name, s in figs.items():
        (OUT / name).write_text(s, encoding="utf-8")
        print(f"wrote assets/readme/{name} ({len(s) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
