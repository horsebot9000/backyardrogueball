"""Extract BB2001 player database (names + gKidData rows) from baller-decompiled scripts."""
import re, json
SRC = '/root/bbsrc/baseball.scu'
SYM = '/root/bb-symbols.ini'
txt = open(SRC).read()
lines = txt.split('\n')

# enum Kid name -> id
kid_id = {}
for l in open(SYM):
    m = re.match(r'enum\.Kid\.(\d+)\s*=\s*(\S+)', l)
    if m: kid_id[m.group(2)] = int(m.group(1))

# ratings rows
rows = {}
for m in re.finditer(r'array-assign-row gKidData (\d+) \[([^\]]*)\]', txt):
    k = int(m.group(1)); vals = [int(v) for v in m.group(2).split()]
    rows.setdefault(k, vals)  # first occurrence = InitOneKidData literal
# clone rule: kids 232..262 copy row kid-201 with appearance+6, gender girl
for k in range(232, 263):
    if k not in rows and (k - 201) in rows:
        r = list(rows[k - 201]); r[11] += 6; r[28] = 1  # GIRL = 1 per symbols
        rows[k] = r

# names from GetKidName
start = txt.index('script GetKidName@229')
end = txt.index('\n}\n', start)
names = {}
cur = None
for l in txt[start:end].split('\n'):
    m = re.match(r'\s*([A-Z0-9][A-Z0-9-]*) \{\s*$', l)
    if m and m.group(1) in kid_id: cur = kid_id[m.group(1)]
    m2 = re.search(r'assign-string gKidName "([^"]*)"', l)
    if m2 and cur is not None and cur not in names: names[cur] = m2.group(1)

COLS = ['pos_pref','stamina','intelligence','coordination','speed','arm','throwing','swing','hitting','eye',
 'attention','appearance','aggression','handedness','heat','slowball','lhook','rhook','corkscrew','zigzag',
 'freeze','fireball','spitball','crazy','slomo','elevator','stance','height','gender','bday_m','bday_d']
POS = ['LF','CF','RF','3B','2B','1B','SS','C','P']
players = []
for k in sorted(r for r in rows if r < 264):
    r = rows[k] + [0] * (len(COLS) - len(rows[k]))
    d = {c: r[i] for i, c in enumerate(COLS)}
    kind = 'kid' if k <= 30 else 'pro' if k <= 61 else 'clanky' if k == 263 else 'custom' if k >= 264 else 'generic'
    d.update(id=k, name=names.get(k, f'Kid {k}'), kind=kind,
             pref=POS[d['pos_pref'] - 1] if d['pos_pref'] else None,
             clone_of=(k - 201) if 232 <= k <= 262 else None)
    players.append(d)
json.dump(players, open('/root/rogue/players.json', 'w'), indent=0)
print(len(players), 'players;', sum(1 for p in players if p['name'].startswith('Kid ')), 'unnamed')
for k in (1, 31, 62, 232, 263):
    p = next(p for p in players if p['id'] == k); print(k, p['name'], p['kind'], p['pref'], p['speed'], p['swing'], p['hitting'], p['arm'], p['height'])
