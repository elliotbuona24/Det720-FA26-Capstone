# Det720 FA26 Capstone

Live game board for the Marala Island capstone (BLUFOR vs. REDFOR).

**Board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/
**Dev board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/dev/

## Files

| File | What it is |
| --- | --- |
| `index.html` | The game board (this is the website) |
| `dev/index.html` | Test copy of the board. Upload new versions here first. |
| `marala_aar.py` | Turns a white cell backup into a printable after-action report |

## Updating the board

1. **Add file → Upload files** in the `dev` folder, drag in the new `index.html`, **Commit changes**. Test it on the dev board.
2. When it works, upload the same file to the top folder and commit.
3. Live in about a minute. Check **Actions** for the green check, then hard-refresh (Ctrl+Shift+R).

## After-action report

One-time setup: install Python (tick **Add to PATH**), then run `pip install matplotlib`.

Each game: download the backup from the game's **white cell** (Game panel), put it in a folder with `marala_aar.py`, open a terminal there and run:

```
python marala_aar.py "backup file name.json"
```

Open the `AAR - ….html` file it creates, press Ctrl+P and choose **Save as PDF** (headers and footers off). Add `--charts charts` to also save each chart as an image for slides.

## Do not upload

Real PINs, code words, the real map file, rosters, or backups and game files of any kind. This repository is public.
