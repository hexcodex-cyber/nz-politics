# -*- coding: utf-8 -*-
import json, re, os, html, datetime, zoneinfo, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from data import *
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", os.path.dirname(HERE))  # repo root (tools/..)
TZ = zoneinfo.ZoneInfo("Pacific/Auckland")
UPDATED = "Thursday 29 October 2026 (NZDT)"
e = html.escape
MONTHS = "January February March April May June July August September October November December".split()

def fmtdate(d):
    p = d.split("-")
    if len(p) == 3: return f"{int(p[2])} {MONTHS[int(p[1])-1]} {p[0]}"
    if len(p) == 2: return f"{MONTHS[int(p[1])-1]} {p[0]}"
    return d

# ---- quotes
Q = {}
for l in open(os.path.join(HERE, "quotes.jsonl")):
    x = json.loads(l)
    if x["p"] not in P: continue
    m = re.search(r"x\.com/[^/]+/status/(\d+)", x["u"])
    if m:
        ts = ((int(m.group(1)) >> 22) + 1288834974657) / 1000
        x["d"] = datetime.datetime.fromtimestamp(ts, TZ).strftime("%Y-%m-%d")
        x["s"] = "X post"
    x["q"] = x["q"].strip()
    Q.setdefault(x["p"], [])
    if any(y["q"] == x["q"] for y in Q[x["p"]]): continue
    Q[x["p"]].append(x)
for k in Q:
    Q[k].sort(key=lambda x: x["d"], reverse=True)
    if len(Q[k]) > 8:  # keep a spread across the period rather than only the newest
        n = len(Q[k]); idx = sorted(set(round(i*(n-1)/7) for i in range(8)))
        Q[k] = [Q[k][i] for i in idx]

def srcname(u):
    h = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
    return {"rnz.co.nz":"RNZ","1news.co.nz":"1News","x.com":"X","en.wikipedia.org":"Wikipedia","nzherald.co.nz":"NZ Herald",
            "thespinoff.co.nz":"The Spinoff","newsroom.co.nz":"Newsroom","scoop.co.nz":"Scoop","national.org.nz":"National Party",
            "labour.org.nz":"Labour Party","greens.org.nz":"Green Party","teaonews.co.nz":"Te Ao Māori News","govt.nz":"govt.nz",
            "vote.nz":"Vote.nz","farmersweekly.co.nz":"Farmers Weekly","odt.co.nz":"ODT","pmn.co.nz":"Pacific Media Network",
            "interest.co.nz":"interest.co.nz","asiapacificreport.nz":"Asia Pacific Report","community.scoop.co.nz":"Scoop",
            "newzeal.org.nz":"NewZeal","act.org.nz":"ACT Party","silvereye.co.nz":"Silvereye","democracyproject.org.nz":"Democracy Project","times.co.nz":"Times Media","linkedin.com":"LinkedIn","newswire.nz":"newswire.nz"}.get(h, h)

ALLPARTIES = PARTIES + OUTSIDE
PARTY = {p["id"]: p for p in ALLPARTIES}

def page(title, body, depth=0, desc=""):
    r = "../" * depth
    nav = "".join(f'<li><a href="{r}parties/{p["id"]}.html">{e(p["short"])}</a></li>' for p in ALLPARTIES)
    return f"""<!doctype html>
<html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · NZ Politics 2026: What They Actually Said</title>
<meta name="description" content="{e(desc or 'Non-partisan profiles of New Zealand political parties and politicians ahead of the 7 November 2026 election, built on sourced direct quotes.')}">
<link rel="stylesheet" href="{r}assets/style.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap"><a class="brand" href="{r}index.html">NZ Politics 2026 <span>What they actually said</span></a>
<nav aria-label="Main"><ul><li><a href="{r}index.html">Home</a></li>{nav}<li><a href="{r}sources.html">Sources &amp; method</a></li></ul></nav></div></header>
<main id="main" class="wrap">{body}</main>
<footer class="site"><div class="wrap"><p>Last updated {UPDATED}. Independent and non-partisan research compilation. Not affiliated with any party or media outlet.
Quotes are reproduced from the linked sources. Always check the original. <a href="{r}sources.html">Methodology &amp; sources</a> · <a href="{r}data/profiles.json">Data (JSON)</a> · <a href="https://github.com/hexcodex-cyber/nz-politics">Source on GitHub</a></p></div></footer>
</body></html>"""

def link(u, label=None):
    return f'<a href="{e(u)}" rel="noopener" target="_blank">{e(label or srcname(u))}</a>'

def items(lst):
    return "<ul class='facts'>" + "".join(f"<li>{t} <span class='src'>[{link(u)}]</span></li>" for t, u in lst) + "</ul>"

def initials(n):
    return "".join(w[0] for w in n.split()[:2] if w[0].isalpha()).upper()

def pnote(u):
    n = POLL_NOTES.get(u)
    return f' <abbr title="{e(n)}">‡</abbr>' if n else ''

def poll_rows(pid):
    rows = ""
    for name, fw, pub, u, ver, d in POLLS:
        v = d.get(pid)
        if v is None: continue
        rows += f"<tr><td>{link(u, name)}{pnote(u)}{'' if ver else ' <abbr title=\"Figures taken from the Wikipedia polling table, not checked against the pollster release\">†</abbr>'}</td><td>{e(fw)}</td><td class='num'>{v:g}%</td></tr>"
    return rows

def person_card(pid, depth):
    p = P[pid]; r = "../" * depth
    n = len(Q.get(pid, []))
    return f"""<li class="pcard"><a href="{r}people/{pid}.html"><span class="avatar" aria-hidden="true">{initials(p['name'])}</span>
<span><strong>{e(p['name'])}</strong><br><span class="muted">{e(p['role'])}</span><br><span class="tag">{n} sourced quote{'s' if n!=1 else ''}</span></span></a></li>"""

def write(path, s):
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(s)

for d in ("parties", "people", "assets", "data"):
    shutil.rmtree(os.path.join(OUT, d), ignore_errors=True)
os.makedirs(OUT + "/assets"); os.makedirs(OUT + "/data")
shutil.copy(os.path.join(HERE, "style.css"), OUT + "/assets/style.css")

# ---- index
grid = ""
for p in ALLPARTIES:
    lead = " &amp; ".join(e(P[l]["name"]) for l in p["leaders"])
    rows = poll_rows(p["id"])
    poll_bits = []
    seen_firms = set()
    for name, fw, pub, u, ver, d in POLLS:
        v = d.get(p["id"])
        if v is None: continue
        if name in seen_firms: continue
        seen_firms.add(name)
        poll_bits.append(f"{v:g}% ({e(name)})")
        if len(poll_bits) == 2: break
    poll_line = " · ".join(poll_bits) if poll_bits else "—"
    grid += f"""<li class="party" style="--pc:{p['colour']}"><a href="parties/{p['id']}.html"><h3>{e(p['short'])}</h3>
<p class="status">{e(p['status'])}</p><p>Leader{'s' if len(p['leaders'])>1 else ''}: {lead}</p>
<p class="muted">Latest polls: {poll_line}</p></a></li>"""
facts = "".join(f"<li><strong>{e(k)}:</strong> {v} <span class='src'>[{link(u)}]</span></li>" for k, v, u in ELECTION["facts"])
ctx = "".join(f"<p>{c}</p>" for c in CONTEXT)
ptable = "<table><caption>Party vote in recent polls (%)</caption><thead><tr><th scope='col'>Poll</th><th scope='col'>Fieldwork</th>" + \
    "".join(f"<th scope='col' class='num'>{e(p['short'])}</th>" for p in ALLPARTIES) + "</tr></thead><tbody>"
for name, fw, pub, u, ver, d in POLLS:
    ptable += f"<tr><td>{link(u, name)}{pnote(u)}{'' if ver else ' †'}</td><td>{e(fw)}</td>" + "".join(f"<td class='num'>{d[p['id']]:g}</td>" for p in ALLPARTIES) + "</tr>"
ptable += "</tbody></table><p class='muted small'>All polls in the table were checked against the publisher's or pollster's release (Taxpayers' Union–Curia via RNZ's report). † would mark figures taken only from the Wikipedia polling table." + ((" ‡ marks a figure that sources report differently: " + "".join(f"<br>‡ {e(n)}" for n in POLL_NOTES.values())) if POLL_NOTES else "") + "<br>The 5% threshold (or one electorate seat) is needed for list seats. Te Pāti Māori relies on electorate seats.</p>"
body = f"""<section class="hero"><p class="kicker">General election</p><h1>{ELECTION['date']}</h1>
<p class="lede">A plain-language catch-up on New Zealand's parties and their leading figures. It is built on what politicians have <em>actually said</em> in 2025–26, with every quote dated and linked to its source.</p></section>
<section aria-labelledby="k"><h2 id="k">Key dates</h2><ul class="facts">{facts}</ul></section>
<section aria-labelledby="c"><h2 id="c">The story so far</h2>{ctx}</section>
<section aria-labelledby="p"><h2 id="p">Parties</h2><p class="muted">The six parties in Parliament at dissolution, then one notable party outside Parliament (marked).</p>
<ul class="grid">{grid}</ul><p class="note">{OTHER_NOTE} <span class="src">[{link('https://www.1news.co.nz/2026/10/06/poll-opportunity-still-in-kingmaker-seat-as-greens-hold-strong/')}]</span></p></section>
<section aria-labelledby="po"><h2 id="po">Recent polling</h2><div class="tablewrap">{ptable}</div></section>
<section aria-labelledby="m"><h2 id="m">How this was made</h2>
<p>For each party in Parliament we profile the leader(s) plus four other senior figures, mainly the next places on the party's 2026 list (details on each party page). Quotes were collected only from sources we actually retrieved: news reports (RNZ, 1News, Newsroom, The Spinoff, Te Ao Māori News and others), party and ministerial press releases, and politicians' own X posts. If a quote could not be verified, it was left out. Where a person has fewer than four verified quotes, we say so. <a href="sources.html">Full methodology and source list →</a></p>
<p class="muted">Last updated {UPDATED}. Things move fast in the final weeks of a campaign, so check the linked sources for later developments.</p></section>"""
write("index.html", page("Home", body))

# ---- party pages
for p in ALLPARTIES:
    outside = p in OUTSIDE
    ppl = p["leaders"] + p["top"]
    rows = poll_rows(p["id"])
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> › {e(p['short'])}</p>
<header class="phead" style="--pc:{p['colour']}"><h1>{e(p['name'])}</h1><p class="status">{e(p['status'])}</p>
{'<p class="flag">Outside Parliament: shorter profile</p>' if outside else ''}</header>
<div class="cols"><div>
<section><h2>In brief</h2><dl class="kv"><dt>History</dt><dd>{p['history']}</dd><dt>Ideology / positioning</dt><dd>{p['ideology']}</dd><dt>Current role</dt><dd>{p['role']}</dd></dl></section>
<section><h2>Key 2026 election policies</h2>{items(p['policies'])}</section>
<section><h2>Notable 2025–26 events and controversies</h2>{items(p['events'])}</section>
</div><aside>
<section class="box"><h2>Recent polling</h2><table><thead><tr><th scope="col">Poll</th><th scope="col">Fieldwork</th><th scope="col" class="num">Vote</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small muted">Figures checked against the publisher or pollster. † would mark figures taken only from Wikipedia. ‡ marks a figure that sources report differently (hover, or see the home page).</p></section>
<section class="box"><h2>Who's profiled and why</h2><p>{p['selection']}</p></section>
<section class="box"><h2>Background sources</h2><ul>{''.join(f'<li>{link(u, u.split("/wiki/")[-1].replace("_"," ") + " (Wikipedia)")}</li>' for u in p['sources'])}</ul></section>
</aside></div>
<section style="--pc:{p['colour']}"><h2>People</h2><ul class="people">{''.join(person_card(x, 1) for x in ppl)}</ul></section>"""
    write(f"parties/{p['id']}.html", page(p["name"], body, 1))

# ---- people pages
for pid, x in P.items():
    party = PARTY[x["party"]]
    qs = Q.get(pid, [])
    qhtml = "".join(f"""<li class="quote"><blockquote><p>“{e(q['q'])}”</p></blockquote>
<p class="meta"><time datetime="{q['d']}">{fmtdate(q['d'])}</time> · {e(q['c'])} · {link(q['u'], q.get('s') or srcname(q['u']))}</p></li>""" for q in qs)
    gap = "" if len(qs) >= 4 else f"<p class='note'>Gap: only {len(qs)} verified 2025–26 quote{'s' if len(qs)!=1 else ''} could be sourced for this person.</p>"
    rev = items(x["reversals"]) if x["reversals"] else "<p class='muted'>None noted in our sources.</p>"
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> › <a href="../parties/{party['id']}.html">{e(party['short'])}</a> › {e(x['name'])}</p>
<header class="phead" style="--pc:{party['colour']}"><h1>{e(x['name'])}</h1><p class="status">{e(party['short'])}: {e(x['role'])}</p></header>
<div class="cols" style="--pc:{party['colour']}"><div>
<section><h2>What they've actually said</h2><p class="muted small">Direct quotes from 2025–26, newest first. Context lines are ours. Wording is as published in the linked source.</p>
<ol class="quotes">{qhtml}</ol>{gap}</section>
<section><h2>Reversals or contradictions</h2>{rev}</section>
{f"<p class='note'>{e(x['note'])}</p>" if x.get('note') else ''}
</div><aside>
<section class="box"><h2>Profile</h2><dl class="kv"><dt>Role</dt><dd>{e(x['role'])}</dd><dt>Electorate / list</dt><dd>{e(x['seat'])}</dd><dt>Background</dt><dd>{e(x['background'])}</dd></dl>
<p class="small">Background source: {link(x['wiki'], 'Wikipedia')}</p></section>
<section class="box"><h2>Key positions</h2><ul>{''.join(f'<li>{e(k)}</li>' for k in x['positions'])}</ul></section>
</aside></div>"""
    write(f"people/{pid}.html", page(x["name"], body, 1, f"{x['name']} ({party['short']}): role, background, positions and sourced quotes from 2025–26."))

# ---- sources page
allsrc = {}
for p in ALLPARTIES:
    for _, u in p["policies"] + p["events"]: allsrc.setdefault(u, set()).add(p["short"])
    for u in p["sources"]: allsrc.setdefault(u, set()).add(p["short"])
for pid, qs in Q.items():
    for q in qs: allsrc.setdefault(q["u"], set()).add(P[pid]["name"])
for pid, x in P.items():
    for _, u in x["reversals"]: allsrc.setdefault(u, set()).add(x["name"])
    allsrc.setdefault(x["wiki"], set()).add(x["name"])
for k, v, u in ELECTION["facts"]: allsrc.setdefault(u, set()).add("Election facts")
for t in POLLS: allsrc.setdefault(t[3], set()).add("Polling")
srcl = "".join(f"<li>{link(u, u)} <span class='muted small'>({e(', '.join(sorted(v)))})</span></li>" for u, v in sorted(allsrc.items(), key=lambda a: (srcname(a[0]), a[0])))
nq = sum(len(v) for v in Q.values())
body = f"""<h1>Sources &amp; methodology</h1>
<section><h2>Scope</h2><p>Covered: the six parties with MPs when the 54th Parliament dissolved on 1 October 2026 (National, Labour, Greens, ACT, NZ First, Te Pāti Māori), plus the Opportunity Party. Opportunity is outside Parliament but polling around or above the 5% threshold, so it gets a shorter profile that is clearly marked. Te Tai Tokerau Party is noted but not profiled.</p></section>
<section><h2>How the 'top 4' were chosen</h2><p>Leader(s) plus the next four people, in this order of preference:</p>
<ol><li>The next places on the party's published 2026 list (National, Labour, ACT, NZ First, Greens' final list).</li>
<li>Where a list doesn't tell you who matters (Te Pāti Māori's list has only one name), we used the other sitting MPs plus key party officers.</li></ol>
<p>This means some people profiled are <strong>not current MPs</strong>: Paul Henry (ACT, rank 4), Alfred Ngaro (NZ First, rank 5), John Tamihere and Lance Norman (Te Pāti Māori officers), and Opportunity's leaders. The reasoning for each party is on its page.</p></section>
<section><h2>Quote rules</h2><ul>
<li>Every quote comes from a page we actually retrieved during research (8–29 October 2026). Wording is as published by that source, including the source's own transcription.</li>
<li>Where a quote is relayed by a news outlet, we link that outlet. Where a release was republished (for example via Scoop), we say so.</li>
<li>X posts link to the post itself. Dates are converted to NZ time. Some long posts were only partly returned by the X API, so we quote the opening text.</li>
<li>Up to 8 quotes per person, newest first, from 2025–26. If fewer than 4 could be verified, the page says so. We did not pad with weak or uncertain material.</li>
<li>Context lines are our neutral description. We give no commentary on whether claims are true. 'Reversals' lists only cases where a source documents a statement and a later, different statement or action.</li>
<li>Dates are publication or post dates (NZ time). Where an event date was approximate, the context says so.</li></ul></section>
<section><h2>Polling</h2><p>The Post/Freshwater Strategy poll (9–19 October, published 20 October) was first checked against RNZ's live report and the Democracy Project's summary because The Post's article was paywalled; they differed on Labour (29.7% v 28.7%). The Post's own articles of 22 and 23 October, retrieved on 24 October, give Labour 28.7% and National 27.6%, so the ‡ note has been removed. The RNZ–Reid Research poll of 20–26 Oct (published 29 Oct) was checked against RNZ's own report on 29 Oct 2026; every party's change matches the previous Reid poll in our table. The newest 1News–Verian poll (21–25 Oct, published 27 Oct) was checked against 1News' own report (one-decimal figures) and RNZ's on 28 Oct 2026. The 1News–Verian poll of 15–19 Oct (published 20 Oct) was checked against 1News' own report and RNZ's, and matches Wikipedia's polling table (checked 21 Oct 2026). Other polls in the table were checked against the publishers: 1News–Verian (8–12 Oct, published 13 Oct; and 1–5 Oct) and RNZ–Reid Research (24 Sep–1 Oct) against their own articles, Taxpayers' Union–Curia (1–5 Oct) against RNZ's 8 October report, and Roy Morgan (31 Aug–27 Sep) against Roy Morgan's 6 October release (Curia and Roy Morgan checked 13 Oct 2026; latest Verian checked 14 Oct 2026).</p></section>
<section><h2>Known gaps and uncertainties</h2><ul>
<li>People with fewer than 4 verified quotes: {', '.join(P[k]['name']+' ('+str(len(Q.get(k,[])))+')' for k in P if len(Q.get(k,[]))<4)}.</li>
<li>Background facts (careers, years elected) are summarised from Wikipedia and general knowledge of the public record, and each links to its Wikipedia page. Some party-level facts are marked 'secondary source' where only Wikipedia was used.</li>
<li>Portfolios are as listed for the caretaker ministry after Parliament's dissolution (main portfolios only, not every associate role).</li>
<li>Enrolment closing date (midnight Sunday 25 October 2026) was confirmed on 13 Oct 2026 against govt.nz (Electoral Commission key dates). Vote.nz key-dates still blocks automated fetches.</li>
<li>Paywalled NZ Herald and The Post articles were generally not used for quotes because we could not read them in full.</li></ul></section>
<section><h2>All sources ({len(allsrc)} links, {nq} quotes)</h2><ul class="srclist">{srcl}</ul></section>"""
write("sources.html", page("Sources & methodology", body))

# ---- JSON
data = dict(meta=dict(title="NZ Politics 2026: What they actually said", last_updated="2026-10-29", timezone="Pacific/Auckland",
                     election=ELECTION, context=CONTEXT, polls=[dict(poll=a, fieldwork=b, published=c, url=d, verified_against_publisher=v, party_vote=f) for a,b,c,d,v,f in POLLS],
                     other_parties_note=OTHER_NOTE),
            parties=[dict(p, in_parliament=p not in OUTSIDE) for p in ALLPARTIES],
            people=[dict(x, quotes=[dict(text=q["q"], date=q["d"], context=q["c"], source=q.get("s") or srcname(q["u"]), url=q["u"]) for q in Q.get(k, [])]) for k, x in P.items()])
json.dump(data, open(OUT + "/data/profiles.json", "w"), ensure_ascii=False, indent=1)
open(OUT + "/.nojekyll", "w").write("")
print("people", len(P), "quotes", nq, "sources", len(allsrc))
