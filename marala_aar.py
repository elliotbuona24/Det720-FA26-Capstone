import argparse
import base64
import html
import io
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

BLUE = "#1d3f8a"
RED = "#9e1b1b"
INK = "#000000"
MUTED = "#3a3a3a"
GRID = "#d4d4d4"
NAMES = {"B": "BLUFOR", "R": "REDFOR"}
COLORS = {"B": BLUE, "R": RED}
LEVEL_BANDS = [
    (0, 25, "Competition", "#f7f7f7"),
    (25, 50, "Tension", "#ececec"),
    (50, 75, "Crisis", "#e0e0e0"),
    (75, 100, "Brink", "#d3d3d3"),
]
KEY_TYPES = {
    "claim", "act_drone", "act_show", "act_jam", "act_strike", "act_aid", "act_statement",
    "firstfire", "returnfire", "sabotage", "provocation", "detonation", "cache", "civaid",
    "resolve", "conduct", "ied", "site_set", "site_contested",
}

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Liberation Serif", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 12.5,
    "axes.edgecolor": "#000000",
    "axes.linewidth": 0.8,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.titlelocation": "left",
})


def hhmm(g):
    m = 360 + int(g)
    return f"{m // 60:02d}{m % 60:02d}"


def g_from_hhmm(text):
    t = "".join(ch for ch in str(text or "") if ch.isdigit())
    if len(t) != 4:
        return None
    return int(t[:2]) * 60 + int(t[2:]) - 360


def level_name(esc):
    if esc >= 100:
        return "War"
    for lo, hi, name, _ in LEVEL_BANDS:
        if lo <= esc < hi:
            return name
    return "War"


def time_axis(ax, start, end):
    ax.set_xlim(start, end)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: hhmm(v)))
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def fig_to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    aar = data.get("aar")
    if not aar or not aar.get("steps"):
        sys.exit(
            "This backup has no game timeline in it. Download a new backup from the white cell's "
            "Game panel on the updated board, then run this again."
        )
    return data, aar


def series(steps, pick):
    xs, ys = [], []
    for s in steps:
        xs.append(s["g"])
        ys.append(pick(s))
    return xs, ys


def log_by_id(aar):
    return {e["id"]: e for e in aar["log"] if e.get("id")}


def escalation_jumps(aar):
    logs = log_by_id(aar)
    jumps = []
    prev = None
    for s in aar["steps"]:
        if prev is not None:
            for side in ("B", "R"):
                d = s["escBy"][side] - prev["escBy"][side]
                if d > 0:
                    entry = logs.get(s["ev"].get("id"), {})
                    jumps.append({"g": s["g"], "side": side, "delta": d, "text": entry.get("text", s["ev"]["type"])})
            d_total = s["esc"] - prev["esc"]
            if d_total < 0 and s["ev"]["type"] != "tick":
                entry = logs.get(s["ev"].get("id"), {})
                jumps.append({"g": s["g"], "side": s["ev"].get("side"), "delta": d_total, "text": entry.get("text", s["ev"]["type"])})
        prev = s
    return jumps


def chart_escalation(aar):
    steps = aar["steps"]
    start, end = aar["startG"], aar["endG"]
    fig, ax = plt.subplots(figsize=(8, 3.99))
    for lo, hi, name, color in LEVEL_BANDS:
        ax.axhspan(lo, hi, color=color, zorder=0)
        ax.text(start + 0.6, lo + 1.5, name, ha="left", va="bottom", fontsize=10.5, color=MUTED)
    ax.axhline(100, color=RED, linewidth=1, linestyle="--")
    ax.text(start + 0.6, 101, "War at 100", ha="left", va="bottom", fontsize=10.5, color=RED)
    xs, ys = series(steps, lambda s: s["esc"])
    xs.append(end)
    ys.append(ys[-1])
    ax.step(xs, ys, where="post", color=INK, linewidth=2.2, zorder=3)
    big = [j for j in escalation_jumps(aar) if j["delta"] >= 10]
    after = {}
    for s in steps:
        after[s["g"]] = s["esc"]
    for i, j in enumerate(big):
        y = after.get(j["g"], 0)
        ax.scatter([j["g"]], [y], color=COLORS.get(j["side"], INK), s=40, zorder=4)
        label = f"{hhmm(j['g'])} {NAMES.get(j['side'], '')} +{j['delta']}"
        ax.annotate(label, (j["g"], y), xytext=(-8, 8 + (i % 2) * 14), textcoords="offset points", ha="right",
                    fontsize=10.5, color=COLORS.get(j["side"], INK), fontweight="bold", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    time_axis(ax, start, end)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Escalation (0–100)")
    return fig_to_png(fig)


def chart_lines(aar, pick, title, ylabel, ylim=None):
    steps = aar["steps"]
    fig, ax = plt.subplots(figsize=(8, 3.23))
    for side in ("B", "R"):
        xs, ys = series(steps, lambda s, side=side: pick(s, side))
        xs.append(aar["endG"])
        ys.append(ys[-1])
        ax.step(xs, ys, where="post", color=COLORS[side], linewidth=2.2, label=NAMES[side])
        ax.annotate(f"{ys[-1]:g}", (xs[-1], ys[-1]), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=10.5, color=COLORS[side], fontweight="bold")
    time_axis(ax, aar["startG"], aar["endG"] + 2)
    if ylim:
        ax.set_ylim(*ylim)
    ax.axhline(0, color="#9aa0a6", linewidth=0.8)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    return fig_to_png(fig)


def site_segments(aar, key):
    segs = []
    cur = None
    for s in aar["steps"]:
        st = s["sites"].get(key) if key != "town" else None
        if key == "town":
            holder = "both" if s["office"]["B"] and s["office"]["R"] else "B" if s["office"]["B"] else "R" if s["office"]["R"] else None
            state = (holder, False)
        else:
            state = (st["holder"], st["contested"])
        if cur is None or state != cur[0]:
            if cur is not None:
                segs.append((cur[1], s["g"], cur[0]))
            cur = (state, s["g"])
    if cur is not None:
        segs.append((cur[1], aar["endG"], cur[0]))
    return segs


def chart_sites(aar):
    keys = list(aar["sites"].keys()) + ["town"]
    labels = [f"{aar['sites'][k]['name']} ({aar['sites'][k]['grid']})" for k in aar["sites"]] + ["Town office"]
    fig, ax = plt.subplots(figsize=(8, 3.13))
    for row, key in enumerate(keys):
        for g0, g1, (holder, contested) in site_segments(aar, key):
            if not holder or g1 <= g0:
                continue
            y = len(keys) - 1 - row
            if holder == "both":
                ax.broken_barh([(g0, g1 - g0)], (y - 0.32, 0.3), facecolors=BLUE)
                ax.broken_barh([(g0, g1 - g0)], (y + 0.02, 0.3), facecolors=RED)
            else:
                ax.broken_barh([(g0, g1 - g0)], (y - 0.32, 0.64), facecolors=COLORS[holder],
                               hatch="////" if contested else None, edgecolor="white" if contested else None,
                               alpha=0.55 if contested else 1)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels(list(reversed(labels)))
    time_axis(ax, aar["startG"], aar["endG"])
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=BLUE, label="BLUFOR"), Patch(color=RED, label="REDFOR"),
                       Patch(facecolor="#9aa0a6", hatch="////", edgecolor="white", label="Contested (scores nothing)")],
              frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3)
    return fig_to_png(fig)


def intel_stats(aar):
    out = {}
    for side in ("B", "R"):
        mine = [c for c in aar["contacts"] if c["side"] == side]
        verdicts = [c.get("verdict") for c in mine]
        delays = []
        for c in mine:
            seen = g_from_hhmm(c.get("seen"))
            if seen is not None and c.get("g") is not None:
                d = c["g"] - seen
                if -1 <= d <= 60:
                    delays.append(max(0.0, d))
        graded = sum(1 for v in verdicts if v in ("confirm", "false", "duplicate"))
        out[side] = {
            "filed": len(mine),
            "confirm": verdicts.count("confirm"),
            "false": verdicts.count("false"),
            "duplicate": verdicts.count("duplicate"),
            "ungraded": sum(1 for v in verdicts if not v),
            "accuracy": (verdicts.count("confirm") / graded * 100) if graded else None,
            "delay": statistics.median(delays) if delays else None,
            "delay_max": max(delays) if delays else None,
        }
    return out


def chart_intel(stats):
    fig, ax = plt.subplots(figsize=(8, 2.09))
    cats = [("confirm", "Confirmed", "#2f5d3a"), ("duplicate", "Duplicate", "#8c8c8c"),
            ("false", "False", "#b0651f"), ("ungraded", "Not graded", "#d9d9d9")]
    for row, side in enumerate(("R", "B")):
        left = 0
        for key, label, color in cats:
            v = stats[side][key]
            if v:
                ax.barh(row, v, left=left, color=color, height=0.55, label=label if row == 0 else None)
                ax.text(left + v / 2, row, str(v), ha="center", va="center", color="white" if key != "ungraded" else INK,
                        fontsize=10.5, fontweight="bold")
                left += v
    ax.set_yticks([0, 1])
    ax.set_yticklabels([NAMES["R"], NAMES["B"]])
    ax.set_xlabel("Reports sent to the board")
    ax.xaxis.set_major_locator(MultipleLocator(1))
    handles = [Patch(color=c, label=l) for _, l, c in cats]
    ax.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=4)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return fig_to_png(fig)


def statements(aar):
    rows = []
    incidents = {i["id"]: i for i in aar["incidents"]}
    for key, blame in aar["statements"].items():
        side, inc_id = key.split(":", 1)
        inc = incidents.get(inc_id)
        if not inc:
            continue
        truth = inc["truth"]
        correct = (blame == "militia" and truth == "militia") or (blame == "other" and truth == ("R" if side == "B" else "B"))
        said = "The militia did it" if blame == "militia" else f"{NAMES['R' if side == 'B' else 'B']} did it"
        real = "the militia" if truth == "militia" else NAMES[truth]
        rows.append({"side": side, "grid": inc["grid"], "g": inc["g"], "said": said, "truth": real, "correct": correct})
    return rows


def questions(aar, stats, jumps, stmts):
    final = aar["final"]
    qs = {"B": [], "R": []}
    for side in ("B", "R"):
        other = "R" if side == "B" else "B"
        mine = sorted([j for j in jumps if j["side"] == side and j["delta"] > 0], key=lambda j: -j["delta"])
        if mine:
            top = mine[0]
            qs[side].append(
                f"Your biggest escalation was at {hhmm(top['g'])}: {top['text']}. What did the Wing Commander know at that "
                f"moment, who made the call, and was it in your decision table?")
        total_esc = final[side]["esc"]
        if total_esc:
            qs[side].append(f"Escalation cost your wing {-total_esc} points in total. Which of those raises bought you something worth it?")
        else:
            qs[side].append("Your wing caused no escalation at all. What did that restraint cost or gain you on the ground?")
        st = stats[side]
        if st["false"]:
            qs[side].append(
                f"{st['false']} of your {st['filed']} reports were judged false. Where did each one start, and how could Intel have checked it before it went to the board?")
        if st["delay"] is not None and st["delay"] >= 4:
            qs[side].append(
                f"Reports took a median of {st['delay']:.0f} minutes from sighting to the board (longest {st['delay_max']:.0f}). Where did the time go between the team and Intel?")
        elif st["delay"] is not None:
            qs[side].append(f"Reports reached the board in a median of {st['delay']:.0f} minutes. What made the reporting chain fast, and does it hold up under jamming?")
        for s in stmts:
            if s["side"] != side:
                continue
            if s["correct"]:
                qs[side].append(f"You correctly said the {s['grid']} explosion was caused by {s['truth']}. What evidence convinced you?")
            else:
                qs[side].append(
                    f"You said \"{s['said']}\" about the {s['grid']} explosion, but it was {s['truth']}. What was that based on, and who checked it?")
        hn = final["hn"][side]
        if hn < 40:
            qs[side].append(f"The mayor's support ended at {hn}. Which moments lost it, and what could have kept the town on your side?")
        held = sum(1 for k, v in aar["steps"][-1]["sites"].items() if v["holder"] == side and not v["contested"])
        lost = sum(1 for c in aar["claims"] if c["side"] == side and c["status"] == "held")
        if lost:
            qs[side].append(f"Your teams reached {lost} site(s) that {NAMES[other]} already held. How did your plan decide which sites to go for first?")
        qs[side].append(f"You finished holding {held} of {len(aar['sites'])} sites. Which branch of your plan actually got used, and which never came up?")
    return qs


def esc_table(jumps):
    rows = []
    for j in jumps:
        if j["delta"] == 0:
            continue
        who = NAMES.get(j["side"], "Both")
        sign = f"+{j['delta']}" if j["delta"] > 0 else str(j["delta"])
        rows.append((hhmm(j["g"]), who, sign, j["text"], j["side"]))
    return rows


def esc(s):
    return html.escape(str(s))


def img(png, alt):
    return f'<img alt="{esc(alt)}" src="data:image/png;base64,{base64.b64encode(png).decode()}">'


def side_cell(side, text):
    cls = {"B": "b", "R": "r"}.get(side, "")
    return f'<td class="{cls}">{esc(text)}</td>'


def build_html(data, aar, charts):
    final = aar["final"]
    b, r = final["B"], final["R"]
    stats = intel_stats(aar)
    jumps = escalation_jumps(aar)
    stmts = statements(aar)
    qs = questions(aar, stats, jumps, stmts)
    if b["total"] > r["total"]:
        winner = f"BLUFOR wins on points, {b['total']} to {r['total']}."
    elif r["total"] > b["total"]:
        winner = f"REDFOR wins on points, {r['total']} to {b['total']}."
    else:
        winner = f"A tie at {b['total']} points each."
    war = "War broke out" + (f" at {hhmm(final['warAt'])}" if final.get("warAt") is not None else "") + ", so both scores were cut in half." if final["war"] else \
        f"No war. Escalation finished at {final['esc']} ({level_name(final['esc'])})."
    score_rows = [
        ("Sites held at the end (10 each)", "sites"), ("Town office open", "town"), ("Confirmed intel reports", "reports"),
        ("IEDs handled", "ied"), ("Militia cache", "cache"), ("Host nation (1 per 10)", "hn"),
        ("Escalation caused (−1 each)", "esc"), ("White cell adjustments", "adj"), ("War penalty", "war"),
    ]
    rows_html = "".join(
        f"<tr><td>{esc(label)}</td><td class='num'>{b[k]:+d}</td><td class='num'>{r[k]:+d}</td></tr>" if k in ("esc", "war", "adj") else
        f"<tr><td>{esc(label)}</td><td class='num'>{b[k]}</td><td class='num'>{r[k]}</td></tr>"
        for label, k in score_rows if b[k] or r[k] or k in ("sites", "esc")
    )
    rows_html += f"<tr class='total'><td>Total</td><td class='num'>{b['total']}</td><td class='num'>{r['total']}</td></tr>"
    intel_rows = ""
    for side in ("B", "R"):
        s = stats[side]
        acc = f"{s['accuracy']:.0f}%" if s["accuracy"] is not None else "–"
        dl = f"{s['delay']:.0f} min" if s["delay"] is not None else "–"
        intel_rows += f"<tr>{side_cell(side, NAMES[side])}<td class='num'>{s['filed']}</td><td class='num'>{s['confirm']}</td><td class='num'>{s['false']}</td><td class='num'>{s['duplicate']}</td><td class='num'>{acc}</td><td class='num'>{dl}</td></tr>"
    stmt_rows = "".join(
        f"<tr><td>{hhmm(s['g'])}</td>{side_cell(s['side'], NAMES[s['side']])}<td>{esc(s['grid'])}</td><td>{esc(s['said'])}</td><td>{esc(s['truth'])}</td><td>{'Correct' if s['correct'] else 'Wrong'}</td></tr>"
        for s in sorted(stmts, key=lambda x: x["g"])
    ) or "<tr><td colspan='6' class='muted'>No public statements were made.</td></tr>"
    esc_rows = "".join(f"<tr><td>{t}</td>{side_cell(sd, who)}<td class='num'>{d}</td><td>{esc(txt)}</td></tr>" for t, who, d, txt, sd in esc_table(jumps)) \
        or "<tr><td colspan='4' class='muted'>Escalation never changed.</td></tr>"
    key_log = [e for e in aar["log"] if e.get("type") in KEY_TYPES]
    key_rows = "".join(
        f"<tr class='{'rej' if e.get('status') == 'rejected' else ''}'><td>{hhmm(e['g'])}</td>{side_cell(e.get('side'), NAMES.get(e.get('side'), '–'))}<td>{esc(e['text'])}</td></tr>"
        for e in key_log
    )
    full_rows = "".join(
        f"<tr class='{'rej' if e.get('status') == 'rejected' else ''}'><td>{hhmm(e['g'])}</td>{side_cell(e.get('side'), NAMES.get(e.get('side'), '–'))}<td>{esc(e['text'])}</td></tr>"
        for e in aar["log"]
    )
    q_html = "".join(
        f"<div class='{side.lower()}'><h3>{NAMES[side]} Wing Commander</h3><ol>{''.join(f'<li>{esc(q)}</li>' for q in qs[side])}</ol></div>"
        for side in ("B", "R")
    )
    built_dt = datetime.fromtimestamp(aar["built"] / 1000) if aar.get("built") else datetime.now()
    built = built_dt.strftime("%d %b %Y").upper()
    outcome = "WAR" if final["war"] else level_name(final["esc"]).upper()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AAR · {esc(aar['name'])}</title>
<style>
@page{{size:letter;margin:0.75in 0.8in 0.8in}}
:root{{--ink:#000;--muted:#3a3a3a;--rule:#000;--light:#bdbdbd;--shade:#efefef;--blue:{BLUE};--red:{RED}}}
*{{box-sizing:border-box}}
html{{background:#d9d9d9}}
body{{margin:0;color:var(--ink);font:12pt/1.4 "Times New Roman",Times,"Liberation Serif",serif}}
main{{max-width:8.5in;margin:24px auto;background:#fff;padding:0.75in 0.8in 0.9in;box-shadow:0 1px 6px rgba(0,0,0,.25)}}
.banner{{text-align:center;font-weight:bold;letter-spacing:.12em;font-size:10pt;border-top:1.5px solid var(--rule);border-bottom:1.5px solid var(--rule);padding:3px 0;margin:0 0 18px}}
.unit{{text-align:center;margin:0 0 14px;line-height:1.25}}
.unit b{{display:block;font-size:13pt;letter-spacing:.04em}}
.unit span{{font-size:11pt}}
h1{{text-align:center;font-size:16pt;letter-spacing:.08em;margin:6px 0 16px}}
.memo{{width:100%;border-collapse:collapse;margin:0 0 16px;font-size:11.5pt}}
.memo td{{padding:2px 0;border:0;vertical-align:top}}
.memo td:first-child{{width:1.6in;font-weight:bold;letter-spacing:.03em}}
h2{{font-size:12pt;text-transform:uppercase;letter-spacing:.06em;margin:22px 0 8px;padding-bottom:2px;border-bottom:1px solid var(--rule)}}
h3{{font-size:12pt;font-style:italic;font-weight:normal;margin:14px 0 6px}}
p{{margin:0 0 8px;text-align:justify}}
.bluf{{border:1px solid var(--rule);padding:8px 12px;margin:0 0 6px}}
.bluf b{{letter-spacing:.04em}}
table.data{{width:100%;border-collapse:collapse;font-size:11pt;margin:6px 0 4px;border-top:1.5px solid var(--rule);border-bottom:1.5px solid var(--rule)}}
table.data th{{text-align:left;font-weight:bold;padding:4px 6px;border-bottom:1px solid var(--rule);font-size:10.5pt}}
table.data td{{padding:3px 6px;border-bottom:.5px solid var(--light);vertical-align:top}}
table.data tr:last-child td{{border-bottom:0}}
.num{{text-align:right!important;font-variant-numeric:tabular-nums}}
td.b{{color:var(--blue);font-weight:bold}} td.r{{color:var(--red);font-weight:bold}}
tr.total td{{font-weight:bold;border-top:1px solid var(--rule)}}
tr.rej td{{color:#777;text-decoration:line-through}}
.stats{{width:100%;border-collapse:collapse;margin:10px 0 4px;text-align:center}}
.stats td{{border:1px solid var(--rule);padding:6px 4px;width:25%}}
.stats b{{display:block;font-size:18pt;line-height:1.15}}
.stats span{{font-size:10pt;text-transform:uppercase;letter-spacing:.05em}}
.stats .b b{{color:var(--blue)}} .stats .r b{{color:var(--red)}}
figure{{margin:8px 0 10px;break-inside:avoid}}
figure img{{width:94%;height:auto;display:block;margin:0 auto}}
figcaption{{font-size:10.5pt;font-style:italic;text-align:center;margin-top:3px}}
.note{{font-size:10.5pt;font-style:italic;color:var(--muted);margin:2px 0 8px}}
.qs h3{{font-style:normal;font-weight:bold;margin:12px 0 4px}}
.qs ol{{margin:0 0 6px;padding-left:24px}} .qs li{{margin:0 0 5px;text-align:justify}}
.qs .b h3{{color:var(--blue)}} .qs .r h3{{color:var(--red)}}
.sig{{margin-top:28px;width:3.2in;margin-left:auto;break-inside:avoid}}
.sig .line{{border-top:1px solid var(--rule);margin-top:40px;padding-top:2px;font-size:11pt}}
.foot{{margin-top:28px;font-size:9.5pt;text-align:center;color:var(--muted)}}
table.log{{font-size:10pt}}
@media print{{html{{background:#fff}} main{{margin:0;padding:0;max-width:none;box-shadow:none}} h2{{break-after:avoid}} table.data tr,.stats,.bluf{{break-inside:avoid}} .pb{{break-before:page}}}}
@media (max-width:700px){{main{{padding:24px 18px;margin:0}}}}
</style></head><body><main>
<div class="banner">* EXERCISE * EXERCISE * EXERCISE * EXERCISE *</div>
<div class="unit"><b>AFROTC DETACHMENT 720</b><span>Capstone</span></div>
<h1>AFTER-ACTION REPORT</h1>
<table class="memo">
<tr><td>EXERCISE:</td><td>{esc(aar['name'])} (Marala Island, BLUFOR vs. REDFOR)</td></tr>
<tr><td>DATE:</td><td>{esc(built)}</td></tr>
<tr><td>GAME WINDOW:</td><td>{hhmm(aar['startG'])}–{hhmm(aar['endG'])} board time</td></tr>
<tr><td>PREPARED BY:</td><td>White Cell</td></tr>
<tr><td>SUBJECT:</td><td>Results, key decisions and discussion points for both Wing Commanders</td></tr>
</table>

<h2>1. Bottom Line Up Front</h2>
<div class="bluf"><b>{esc(winner)}</b> {esc(war)}</div>
<table class="stats"><tr>
<td class="b"><b>{b['total']}</b><span>BLUFOR points</span></td>
<td class="r"><b>{r['total']}</b><span>REDFOR points</span></td>
<td><b>{final['esc']}</b><span>Final escalation · {esc(outcome)}</span></td>
<td><b>{final['hn']['B']} / {final['hn']['R']}</b><span>Host nation B / R</span></td>
</tr></table>

<h2>2. Final Score</h2>
<table class="data"><thead><tr><th>Category</th><th class="num">BLUFOR</th><th class="num">REDFOR</th></tr></thead><tbody>{rows_html}</tbody></table>

<h2>3. Escalation</h2>
<figure>{img(charts['escalation'], 'Escalation over the game')}<figcaption>Figure 1. Shared escalation meter over the game. Marked points are single moves worth 10 or more.</figcaption></figure>
<table class="data"><thead><tr><th>Time</th><th>Wing</th><th class="num">Change</th><th>Event</th></tr></thead><tbody>{esc_rows}</tbody></table>
<p class="note">With no new escalation, the meter drops 3 at each 10-minute board update; those drops are not listed.</p>

<h2>4. Points and Host-Nation Support</h2>
<figure>{img(charts['score'], 'Points over time')}<figcaption>Figure 2. Each wing's points over the game.</figcaption></figure>
<figure>{img(charts['hn'], 'Host-nation meter over time')}<figcaption>Figure 3. The mayor's support (host-nation meter). Below 20, the mayor closes that wing's town office.</figcaption></figure>

<h2>5. Site Control</h2>
<figure>{img(charts['sites'], 'Who held each site')}<figcaption>Figure 4. Control of each site over the game. Hatched bars were contested and scored nothing.</figcaption></figure>

<h2>6. Managing Intelligence</h2>
<figure>{img(charts['intel'], 'Intel reports by verdict')}<figcaption>Figure 5. Reports sent to the board and how the white cell judged them.</figcaption></figure>
<table class="data"><thead><tr><th>Wing</th><th class="num">Reports</th><th class="num">Confirmed</th><th class="num">False</th><th class="num">Duplicate</th><th class="num">Accuracy</th><th class="num">Median delay</th></tr></thead><tbody>{intel_rows}</tbody></table>
<p class="note">Delay is the time from a team's sighting to the report reaching the board. Accuracy counts only reports the white cell judged.</p>
<h3>Attribution of explosions</h3>
<table class="data"><thead><tr><th>Time</th><th>Wing</th><th>Where</th><th>Public statement</th><th>Actual cause</th><th>Result</th></tr></thead><tbody>{stmt_rows}</tbody></table>

<h2>7. Discussion Points</h2>
<div class="qs">{q_html}</div>

<div class="sig"><div class="line">White Cell Lead<br>Capstone, Det 720</div></div>

<h2 class="pb">Annex A. Chronology of Key Events</h2>
<table class="data"><thead><tr><th style="width:0.7in">Time</th><th style="width:1in">Wing</th><th>Event</th></tr></thead><tbody>{key_rows}</tbody></table>
<p class="note">Struck-through entries were refused by the board.</p>

<h2 class="pb">Annex B. Full Board Log ({len(aar['log'])} entries)</h2>
<table class="data log"><thead><tr><th style="width:0.7in">Time</th><th style="width:1in">Wing</th><th>Entry</th></tr></thead><tbody>{full_rows}</tbody></table>
<div class="foot">Generated from the Marala Island board backup. Points and meters are computed by the board's rules.</div>
</main></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Turn a Marala Island board backup into an after-action report.")
    ap.add_argument("backup", help="the .json file from the white cell's Download backup button")
    ap.add_argument("-o", "--out", help="report file to write (default: next to the backup)")
    ap.add_argument("--charts", help="also save each chart as a PNG in this folder, for slides")
    args = ap.parse_args()

    data, aar = load(args.backup)
    stats = intel_stats(aar)
    charts = {
        "escalation": chart_escalation(aar),
        "score": chart_lines(aar, lambda s, side: s["score"][side], "Points over time", "Points"),
        "hn": chart_lines(aar, lambda s, side: s["hn"][side], "The mayor's support (host-nation meter)", "Support (0–100)", (0, 105)),
        "sites": chart_sites(aar),
        "intel": chart_intel(stats),
    }
    src = Path(args.backup)
    out = Path(args.out) if args.out else src.with_name(f"AAR - {aar['name']}.html")
    out.write_text(build_html(data, aar, charts), encoding="utf-8")
    print(f"Report written to {out}")
    if args.charts:
        folder = Path(args.charts)
        folder.mkdir(parents=True, exist_ok=True)
        for name, png in charts.items():
            (folder / f"{name}.png").write_bytes(png)
        print(f"Charts saved in {folder}")


if __name__ == "__main__":
    main()
