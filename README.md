# NZ Politics 2026: What they actually said

**Live site:** https://hexcodex-cyber.github.io/nz-politics/
**Last updated:** 13 October 2026 (NZ time, NZDT)

A static, non-partisan website profiling New Zealand's political parties and their leading figures ahead of the **7 November 2026 general election**. It focuses on what politicians have *actually said* in 2025–26. Every quote is dated, has a short neutral context line, and links to the source it was taken from.

The site is plain HTML and CSS with no JavaScript and no build step needed to view it. It works opened from disk or on any static host.

---

## What's covered

Parties with MPs when the 54th Parliament dissolved on 1 October 2026, plus one notable party outside Parliament:

| Party | Leader(s) | Top 4 others |
|---|---|---|
| National | Christopher Luxon | Nicola Willis, Chris Bishop, Simeon Brown, Erica Stanford |
| Labour | Chris Hipkins | Carmel Sepuloni, Barbara Edmonds, Willie Jackson, Megan Woods |
| Greens | Marama Davidson, Chlöe Swarbrick (co-leaders) | Teanau Tuiono, Tamatha Paul, Julie Anne Genter, Lan Pham |
| ACT | David Seymour | Nicole McKee, Andrew Hoggard, Paul Henry*, Karen Chhour |
| NZ First | Winston Peters | Shane Jones, Casey Costello, Mark Patterson, Alfred Ngaro* |
| Te Pāti Māori | Rawiri Waititi, Debbie Ngarewa-Packer (co-leaders) | Hana-Rāwhiti Maipi-Clarke, Oriini Kaipara, John Tamihere*, Lance Norman* |
| Opportunity (outside Parliament) | Qiulae Wong | Daniel Eb* (deputy) |

\* Not a current MP.

Te Tai Tokerau Party (Mariameno Kapa-Kingi) gets a note but is not profiled.

### How the "top 4" were chosen

1. Leader(s), then **list places 2–5 on each party's published 2026 party list**. For the Greens this is the final members-ranked list of 22 April 2026.
2. Te Pāti Māori's list has only one name (Lance Norman) because of its candidate-vote-only strategy. For TPM we used its two other sitting MPs plus its president and general secretary.
3. Opportunity gets a shorter profile with its leader and deputy.

Each party page explains its own selection.

## Methodology and sourcing rules

- **Quotes come only from sources actually fetched during research (8–11 Oct 2026).** These are news reports (RNZ, 1News, Newsroom, The Spinoff, Te Ao Māori News and others), party and ministerial releases (directly or via Scoop), and politicians' own X posts. Nothing is quoted from memory, and unverifiable quotes were left out.
- Wording is exactly as published by the linked source. Context lines are neutral descriptions written by us, with no fact-check verdicts or commentary.
- Up to 8 quotes per person. Where there are more, a spread across the period is kept, shown newest first. If fewer than 4 could be verified, the page shows a **"Gap"** note rather than padding.
- **X posts:** dates are converted to NZ time from the post ID. Some long posts were truncated by the API, so only the opening text is quoted.
- **Reversals or contradictions** are listed only where a source documents a statement and a later, different statement or action. Examples: Hipkins on capital gains tax (2023 vs 2025), Peters on the Regulatory Standards Act, and National dropping bank and bed tax ideas.
- **Flags used on the site:**
  - **†** marks poll figures taken from the Wikipedia polling table that were not checked against the pollster's own release. 1News–Verian and RNZ–Reid figures were checked against the publishers.
  - **"secondary source"** marks a party-level fact supported only by Wikipedia.
  - **"Uncertain"** marks a fact we could not confirm from a primary source.
  - **"Gap"** marks a person with fewer than 4 verified quotes.
- Background facts (careers, years elected) are summarised from Wikipedia and linked on each person's page.
- Portfolios are those of the caretaker ministry after dissolution (main portfolios only).

## Known gaps

- Fewer than 4 verified 2025–26 quotes: Tamatha Paul, Julie Anne Genter, Paul Henry, Mark Patterson (3 each), Lance Norman (2 short fragments), Daniel Eb (1). Edmonds now has 4.
- Taxpayers' Union–Curia and Roy Morgan were previously † Wikipedia-only; both were checked against publisher releases on 13 Oct 2026.
- Paywalled NZ Herald and The Post articles were generally not used for quotes.
- Some event dates are approximate, and this is stated in the context line (for example Peters' remark to Lawrence Xu-Nan, around 28 July 2026).
- The site is a living snapshot (last rebuilt 13 Oct 2026). Campaign events after that date may not be included yet.

## File and folder structure

```
.
├── index.html            Home: election date, key dates, context, parties grid, polls, method summary
├── sources.html          Full methodology, gaps and every source link
├── parties/<id>.html     One page per party (national, labour, greens, act, nzfirst, tpm, opportunity)
├── people/<id>.html      One page per person (e.g. people/luxon.html)
├── assets/style.css      All styling (generated copy of tools/style.css)
├── data/profiles.json    All underlying data (generated)
├── tools/
│   ├── data.py           Hand-written content: election facts, context, polls, parties, people
│   ├── quotes.jsonl      All quotes, one JSON object per line
│   ├── build.py          Generates every HTML page plus data/profiles.json
│   └── style.css         Stylesheet source
├── docs/CHANGELOG.md
├── .nojekyll             Tells GitHub Pages to serve files as-is
└── README.md
```

The HTML, `assets/` and `data/` are **generated**. Edit `tools/` and rebuild instead of editing them directly.

## `data/profiles.json` schema

```jsonc
{
  "meta": {
    "title": "string",
    "last_updated": "YYYY-MM-DD",
    "timezone": "Pacific/Auckland",
    "election": { "date": "string", "facts": [["label", "html text", "source url"], ...] },
    "context": ["html paragraph", ...],
    "polls": [{
      "poll": "1News–Verian", "fieldwork": "1–5 Oct 2026", "published": "6 Oct 2026",
      "url": "https://...", "verified_against_publisher": true,
      "party_vote": { "<party id>": 29.0, ... }
    }],
    "other_parties_note": "html"
  },
  "parties": [{
    "id": "national", "name": "string", "short": "string", "colour": "#hex",
    "status": "string", "in_parliament": true,
    "leaders": ["<person id>"], "top": ["<person id>", ...],
    "selection": "html: how the top 4 were chosen",
    "history": "html", "ideology": "html", "role": "html",
    "policies": [["html text", "source url"], ...],
    "events":   [["html text", "source url"], ...],
    "sources":  ["background url", ...]
  }],
  "people": [{
    "id": "luxon", "name": "string", "party": "<party id>",
    "role": "string", "seat": "electorate / list", "background": "string",
    "positions": ["string", ...],
    "wiki": "background source url",
    "reversals": [["text", "source url"], ...],
    "note": "string or null",
    "quotes": [{ "text": "verbatim quote", "date": "YYYY-MM-DD (NZ)", "context": "string",
                 "source": "outlet name", "url": "https://..." }]
  }]
}
```

## Preview locally

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000/
```

## Updating: add a quote or politician, then redeploy

Requires Python 3.9+ and only the standard library.

**Add a quote:** append one line to `tools/quotes.jsonl`:

```json
{"p": "luxon", "q": "Exact words as published.", "d": "2026-10-12", "c": "Neutral context", "s": "RNZ", "u": "https://www.rnz.co.nz/..."}
```

`p` is the person id, `q` the verbatim quote, `d` the NZ date, `c` the context, `s` the source name and `u` the URL. Only add quotes from a page you have actually opened, and copy the wording exactly. For X posts the date is recomputed automatically from the post ID.

**Add a politician:** in `tools/data.py`, add a `person("id", "Name", "<party id>", role, seat, background, [positions], "Wikipedia_Title", reversals=[(text, url)], note=None)` call. Then add the id to that party's `leaders` or `top` list.

**Edit party content or polls:** edit `PARTIES`, `OUTSIDE`, `POLLS`, `ELECTION` or `CONTEXT` in `tools/data.py`. Update `UPDATED` in `tools/build.py`.

**Rebuild and redeploy:**

```bash
python3 tools/build.py          # regenerates HTML, assets/ and data/profiles.json
git add -A && git commit -m "Update: <what changed>"
git push origin main            # GitHub Pages redeploys automatically (about 1 minute)
```

Add an entry to `docs/CHANGELOG.md` for each update.

## Disclaimer

This is an independent research compilation, not affiliated with any party or media outlet. Quotes are reproduced from the linked sources for reference. Always check the original.
