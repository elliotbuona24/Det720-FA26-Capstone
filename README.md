# Det720 FA26 Capstone Guide

Live game board for the Marala Island capstone (BLUFOR vs. REDFOR).

**Board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/
**Dev board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/dev/

READ ALL SUPPORTING DOCUMENTS PROVIDED BY EXERCISES PRIOR TO USE

## Files

| File | What it is |
| --- | --- |
| `index.html` | The game board (this is the website) |
| `dev/index.html` | Test copy of the board. Upload new versions here first. |
| `marala_aar.py` | Turns a white force backup into a printable after-action report |
| `firestore.rules` | Database security rules to paste into the Firebase console |
| `HANDOFF.md` | How the board works, who owns what, and how to run a new exercise |
| `Capstone injects - AOC.json` | The 31 injects used on 19 Nov (load on White Force, Intel and inject creation) |
| `Capstone injects - extra field.json` | 15 more field injects that use only props already on hand |
| `Capstone props catalog.json` | The props catalog and where each prop is used |
| `Capstone offline board.zip` | Offline copy of the board for the White Force laptop if the internet fails |
| `sw.js` | Lets phones reopen the board with a weak signal |

## Updating the board

1. **Add file → Upload files** in the `dev` folder, drag in the new `index.html`, **Commit changes**. Test it on the dev board.
2. When it works, upload the same file to the main top folder and commit. 
3. Live in about a minute. Check **Actions** for the green check, then hard-refresh (Ctrl+Shift+R).

## After-action report (generates automatically at ENDEX and can open PDF at the end)

One-time setup: install Python (tick **Add to PATH**), then run `pip install matplotlib`.

Each game: download the backup from the game's **White Force** screen (Clock and setup tab), put it in a folder with `marala_aar.py`, open a terminal there and run:

```
python marala_aar.py "backup file name.json"
```

Open the `AAR - ….html` file it creates, press Ctrl+P and choose **Save as PDF** (headers and footers off). Add `--charts charts` to also save each chart as an image for slides.

## Do not upload

Real PINs, code words, the real map file, rosters, or backups and game files of any kind. This repository is public.
