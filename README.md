# Det720 FA26 Capstone

Live game board for the Marala Island capstone (BLUFOR vs. REDFOR).

**Board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/

## Files

| File | What it is |
| --- | --- |
| `index.html` | The game board (this is the website) |
| `marala_aar.py` | Turns a game backup into a printable after-action report |
| `sample-backup.json` | Fake game for testing the AAR script |

## Running a game

1. Open the board, choose **White cell**, enter the PIN.
2. **Game** panel → **Set up a new game** → enter the six PINs (white cell, two wings, two fireteam, POC), site code words, start time and length → **Create game**.
3. **Map setup** (white cell): click or type the play area's corners and each site's grid → **Save the map for every screen**.
4. Wings pick their view and enter their PIN. One phone per fireteam picks **BLUFOR fireteam** or **REDFOR fireteam**, enters the fireteam PIN and names the team. **Public screen** needs no PIN. Each POC opens the board on a phone, picks **POC**, enters the POC PIN, types their name and picks the fireteam they are with (or Mayor).
5. Open the map on every device before step-off so the satellite pictures load while the wifi is quiet.
6. Click **Start the game**. Until then you can change the start time and length in the white cell's **Clock** panel (default 0830, 165 minutes). The Capstone field (the 13 Oct points, with the five points of interest on the white cell map only) loads by default; change it under **Map setup**.
7. After ENDEX: **Download backup**.

Lost the white cell PIN? Use **Start a new game** on the main menu with the recovery code (ask the exercise officers).

## After-action report

One-time setup: install Python from python.org (tick **Add to PATH**), then:

```
pip install matplotlib
```

Each game: put `marala_aar.py` and the backup in one folder, open a terminal there, and run:

```
python marala_aar.py marala-board-backup-XXXX.json
```

Open the `AAR - ….html` file it creates → Ctrl+P → **Save as PDF** (headers and footers off).
Add `--charts charts` to also save each chart as an image for slides.

## Updating the board

**Add file → Upload files** → drag in the new `index.html` → **Commit changes**. Live in about a minute (check **Actions** for the green check).

## Do not upload

Real PINs, code words, the recovery code, rosters, or backups from real games. This repository is public.
