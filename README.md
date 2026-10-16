# Det720 FA26 Capstone

Live game board for the Marala Island capstone (BLUFOR vs. REDFOR).

**Board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/
**Dev Board:** https://elliotbuona24.github.io/Det720-FA26-Capstone/dev/

## Files (update!)

| File | What it is |
| --- | --- |
| `index.html` | The game board |
| `marala_aar.py` | Turns a game backup into a printable after-action report |
| `sample-backup.json` | Fake game for testing the AAR script |


## After-action report

One-time setup: install something that can run Python  (tick **Add to PATH**), then:

```
pip install matplotlib
```

Each game: put `marala_aar.py` and the backup in one folder, open a terminal there, and run:

```
python marala_aar.py marala-board-backup-XXXX.json
```

Open the `AAR - ….html` file it creates → Ctrl+P → **Save as PDF** (headers and footers off).
Add `--charts charts` to also save each chart as an image for slides.


