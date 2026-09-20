#!/usr/bin/env python3
import json, html, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CFG = json.loads((ROOT / "stats-config.json").read_text(encoding="utf-8"))

def fetch(url, payload=None):
    req = urllib.request.Request(url, data=payload, headers={
        "User-Agent": "Akhil-GitHub-Profile-Stats/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())

def e(x): return html.escape(str(x))

def card(title, rows, accent):
    y = 72
    parts = []
    for label, value in rows:
        parts.append(f'<text x="42" y="{y}" fill="#8FA2AE" font-family="ui-monospace,monospace" font-size="14">{e(label)}</text>')
        parts.append(f'<text x="718" y="{y}" text-anchor="end" fill="#F4F8FA" font-family="ui-monospace,monospace" font-size="17" font-weight="700">{e(value)}</text>')
        y += 42
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="260" viewBox="0 0 760 260">
<rect x="1" y="1" width="758" height="258" rx="18" fill="#071018" stroke="#183342"/>
<text x="42" y="42" fill="{accent}" font-family="ui-monospace,monospace" font-size="18" font-weight="700">{e(title)}</text>
<circle cx="718" cy="37" r="5" fill="{accent}"><animate attributeName="opacity" values=".2;1;.2" dur="2s" repeatCount="indefinite"/></circle>
{''.join(parts)}
</svg>'''

def leetcode(username):
    if username.startswith("PUT_"):
        return [("Username", "configure stats-config.json"), ("Status", "waiting")]
    query = '''query userPublicProfile($username: String!) {
      matchedUser(username: $username) {
        username
        profile { ranking reputation }
        submitStatsGlobal { acSubmissionNum { difficulty count } }
      }
    }'''
    payload = json.dumps({"query": query, "variables": {"username": username}}).encode()
    data = fetch("https://leetcode.com/graphql", payload)
    u = (data.get("data") or {}).get("matchedUser")
    if not u: raise RuntimeError("LeetCode user not found")
    counts = {x["difficulty"]: x["count"] for x in u["submitStatsGlobal"]["acSubmissionNum"]}
    return [
        ("Username", u["username"]),
        ("Problems solved", counts.get("All", sum(counts.values()))),
        ("Easy / Medium / Hard", f'{counts.get("Easy",0)} / {counts.get("Medium",0)} / {counts.get("Hard",0)}'),
        ("Global ranking", u["profile"].get("ranking") or "—"),
        ("Reputation", u["profile"].get("reputation") or "—")
    ]

def codeforces(username):
    if username.startswith("PUT_"):
        return [("Handle", "configure stats-config.json"), ("Status", "waiting")]
    data = fetch("https://codeforces.com/api/user.info?handles=" + urllib.parse.quote(username))
    if data.get("status") != "OK" or not data.get("result"): raise RuntimeError("Codeforces user not found")
    u = data["result"][0]
    return [
        ("Handle", u.get("handle")),
        ("Rating", u.get("rating", "Unrated")),
        ("Max rating", u.get("maxRating", "—")),
        ("Rank", u.get("rank", "Unrated")),
        ("Max rank", u.get("maxRank", "—"))
    ]

def safe(fn, username):
    try: return fn(username)
    except Exception as ex: return [("Status", "temporary API error"), ("Details", str(ex)[:52])]

(ASSETS / "leetcode-stats.svg").write_text(card("LEETCODE // LIVE STATS", safe(leetcode, CFG["leetcode"]), "#58E6C4"), encoding="utf-8")
(ASSETS / "codeforces-stats.svg").write_text(card("CODEFORCES // LIVE STATS", safe(codeforces, CFG["codeforces"]), "#7C7CFF"), encoding="utf-8")
print("Live-stat SVGs refreshed.")
