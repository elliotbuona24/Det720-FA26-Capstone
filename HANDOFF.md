# Handoff guide

For the next exercises officer, or anyone reusing the board for another exercise. Read the README first.

## What the board is

- One web page (`index.html`) served by GitHub Pages. No server code.
- Shared data lives in a Firebase project (Cloud Firestore). Every device writes small "events" (a claim, a report, an order); every screen rebuilds the game from the full list of events.
- The admin page (Game list, Create, Edit, Delete) signs in with a Firebase email and password. Players never sign in; they pick a game, enter the game PIN, then their role PIN.
- `sw.js` keeps a copy of the page, the intel images and the Firebase code on each device so the board opens on weak connections.
- `dev/index.html` is a test copy at `/dev/`. Change and test it there first, then copy the same file to the top folder.

## Accounts to hand over

| What | Where | Hand over by |
| --- | --- | --- |
| GitHub repository | github.com, repository Settings | Add the new officer as a collaborator, or transfer the repository to a detachment GitHub account |
| Firebase project | console.firebase.google.com, Project settings, Users and permissions | Add the new officer as Owner. Keep at least two Owners so the project is never locked out |
| Owner | Firestore rules, `isOwner()` | The owner email in the rules has full control, including managing admins. Change it in the console rules when ownership moves |
| Admins | Board, Admin, Admins list (owner only) | The owner adds, renames, suspends and removes admins on the board. Each admin also needs a Firebase sign-in: tick "Also create their sign-in now" (needs sign-up turned on) or create it in Firebase console, Authentication, Users |
| Billing (Blaze plan) | Firebase console, Usage and billing | Keep a budget alert on whoever pays. A full exercise costs well under a dollar |

If you keep ownership yourself, still add a second Owner on Firebase and GitHub so the board survives a lost password.

## Security setup (one time, and after any account change)

1. **Firestore rules:** paste `firestore.rules` from this repository into Firebase console, Firestore Database, Rules. Replace `OWNER_EMAIL_HERE` with the owner's email (lowercase) in the console only; don't commit real emails here. Publish. Other admins are managed on the board, not in the rules. The first time the owner signs in to Admin after publishing, the board adds the owner to the Admins list.
2. **Sign-up setting:** Firebase console, Authentication, Settings, User actions, "Enable create (sign-up)". Leave it off and create admin sign-ins in the Users tab, or turn it on so the owner can create them from the board. Either way, a sign-in alone gives no access; only the owner's Admins list does.
3. **Plan:** keep the project on the Blaze (pay as you go) plan with a small budget alert. The free Spark plan allows 50,000 document reads a day, and a full exercise with 50+ devices reads far more than that. On Spark the board stops syncing partway through the exercise.
4. **API key (optional):** Google Cloud console, APIs and Services, Credentials, the Browser key: add an HTTP referrer restriction for `https://YOUR-USERNAME.github.io/*`. The key in `index.html` is meant to be public; the rules are what protect the data.
5. **Game PINs:** use 8 or more letters and numbers for real games (the admin page warns on shorter ones). The game list is public, so a short game PIN can be guessed.

## Running a new exercise

1. **Content.** Build or edit in the admin page and the White Force screens: map and sites, code words, role PINs, injects (template library and queue), props catalog, intel packages. Then use White Force **Download backup** to save the whole setup as one JSON file.
2. **Test.** Create a test game from that file with "Allow practice bots" on. Run the bots at fast-forward to drill the timeline. Delete the test game when done.
3. **Real game.** Create it fresh from the final JSON with practice bots off and a strong game PIN. Hand out role PINs in person.
4. **After.** Download the ENDEX backup and run `marala_aar.py` for the AAR (see the README).

Never commit the setup JSON, backups, PINs, code words or rosters. This repository is public.

## Changing the built-in content in the code

Most content lives in the game file, not the code. The parts below are built into `index.html` and need a code change to replace for a different scenario. Search for these names:

| Name | What it holds |
| --- | --- |
| `SIDES`, `SITES`, `BASE_SITE_KEYS` | Force labels, capture sites and their grid squares. Who each force is and the four key site names can be changed per game without code: Admin, Edit game, Names in this game |
| `GEO`, `DEFAULT_POIS` | Area 5 map outline and points of interest |
| `PROBLEMS` | The built-in intel packages, including their answers. Anyone can read these in the page source, so for a new exercise write new packages or start games with the starter content turned off and load custom packages through the game file |
| `CUB_STD`, `CUB_LINES`, `RHYTHM` | Update brief lines and battle rhythm |
| `OC_CALLS`, `INDOOR_DEFAULT` | POC O/C call types and the indoor room plan |
| `LEVELS` | Escalation level names |
| Bot names (search `'Hawk'` and `botName`) | Practice bot fireteam names and default POC names |
| `HELP` | The Help button text for each role. Update it when buttons or procedures change |

Keep `index.html` and `dev/index.html` identical after testing.

## Known limits

- Role PINs and code words are checked on each device, not by a server. A participant who has the game PIN and opens the browser's developer tools could, with effort, read hashed PINs and code words or post events as another role. The White Force log shows every event and who sent it; watch for claims or results that don't match what POCs saw.
- The intel package answers built into the code are public (see `PROBLEMS` above).
- Firestore security depends on the rules in the Firebase console. If the rules are ever reset, anyone could read or change games.

## Before every execution day

- Rules published and admin emails current; sign-up off; Blaze plan with a budget alert.
- Real game created fresh from the final JSON, strong game PIN, practice bots off, test and drill games deleted.
- Last commit at least a day before. Every device opens the board and its map on Wi-Fi the morning of.
- Backups at a few set times during the game and right after ENDEX.
