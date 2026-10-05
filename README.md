# Backyard Rogueball (BB2001 roguelite)

Run `play.bat` (needs Python), or host this folder on GitHub Pages. First launch asks for your
Backyard Baseball 2001 folder; the patch in `patches/` is applied in the browser to your own files.
The patch only fits the BSO-patched copy it was made from. After an update the page asks for the
game folder again (the stored patched copy is versioned).

## Loop
Draft 9 from market-rank buckets that get weaker each round (top 24 of the market held out; open
C / P / SS / 1B / OF spots are guaranteed to show up late) > case-opening reel picks park + innings
(3 to 6, every park, plus a tee-ball bonus slot) > clubhouse: drag faces between positions, a
5-player bench and the batting order; trade block (sign to bench or swap) > play > payout:
$3 win + $1 per run of differential + interest; mercy rule at a 20-run lead > 1 of 3 augments.
One loss ends the run. CPU difficulty: easy games 1-3, medium 4-8, hard after.

## Values and position rules
Market value, market rank and ADP come from the BBOL S8 mock draft tool data (source/market_raw.json).
Position rules match that tool: C 90+ arm (87-89 low end), SS 65+ arm and speed tier 5+,
OF speed tier 6+, 1B height 3+, P = pitcher or workhorse flag (or two non-heat pitches 65+).

## Sound
Page volume defaults to 25% and the engine is muted whenever the menus are up. Game music,
commentary, crowd and player chatter default off (Sound settings). The boot intro is skipped.

## Tuning
`CONFIG` and `AUGMENTS` at the top of source/index.src.html (or directly in index.html).
Console: `__G.run` is the live run, `__G.CONFIG` can be changed on the fly.

## Game-side changes (source/rogue-scripts.diff)
Lobby polls rogue_in.ini, applies rosters / stat deltas / innings / park / difficulty / audio
flags, starts a quick game; result + box score written to rogue_out.ini. Mercy rule checked
between plays. During a run the in-game quit prompts are blocked, and if the lobby is ever
reached mid-game the same game restarts. Good/bad days (hot/cold) are off.
Engine change (fresh reads for rogue_* files): source/scummvm-rogue.diff.

## Shop, cards, power-ups (v4)
- Cards (3 slots, 3 offered per round, no rerolls, sell for half): rarity colors common grey, rare blue, epic purple, legendary gold. Prices in CONFIG.cardPrice.
- Power-ups are bought, never earned in game. Counts carry over; up to 9 of each batting type (10 More Juice) go into each game, unused ones come back.
- Augment rerolls and reel respins cost money, rising with each use, reset each round. Freerolls cards give free augment rerolls.
- Stats run 0 to 125 (height 1 to 5). Team name and adjective from the game's own lists.
