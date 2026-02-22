# De-Markation MVP (No-Code-Friendly Starter)

This is a small working prototype that:
- pulls course / assignment / student data from Canvas,
- lets you mark by criteria first,
- keeps the total hidden until expanded,
- pushes a numeric grade and feedback comment back into Canvas.
- can run in demo mode first, even without Canvas credentials.
- supports optional one-click model activation (for example CAPRI).
- exports marking data as CSV.

## Important scope note
This is **not yet an LTI app**. It is the fastest MVP path to prove your concept with real Canvas data.

## 1) Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- `CANVAS_BASE_URL` = your Canvas root URL (for example `https://yourschool.instructure.com`)
- `CANVAS_TOKEN` = a Canvas access token with permission to read courses/assignments and edit submissions
- `DEMO_MODE=true` = run with sample data and no Canvas connection
- `DEMO_MODE=false` = use real Canvas data

## 2) Run

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## 3) Use

1. Select a course.
2. Select an assignment.
3. Select a student.
4. Move criterion sliders.
5. Expand "Total" only if needed.
6. Click "Send Grade".
7. Click "Export Marking CSV" if you want a local file copy.

## Fast demo path (no Canvas required)

1. Set `DEMO_MODE=true` in `.env`.
2. Run `python app.py`.
3. Open the app and choose model `CAPRI`.
4. Click `Activate Selected Model`.
5. Mark against CAPRI criteria using sliders.
6. Use `Send Grade` (simulated in demo mode) and/or `Export Marking CSV`.

Or use one command:

```bash
bash scripts/run_capri_demo.sh
```

## Criteria editing

Edit `config/criteria.json` to change criteria, domains, and weights.

## Optional criteria grouping models

This repo now includes an optional folder: `Criteria Grouping Models/`.

- Included model: `Criteria Grouping Models/CAPRI.json`
- CAPRI is optional. No user is required to use it.

To use CAPRI in the app:

```bash
cp 'Criteria Grouping Models/CAPRI.json' config/criteria.json
```

Then restart the app.

## Next technical upgrades

1. Add Canvas OAuth login so you do not need a manual token.
2. Convert to LTI 1.3 launch flow.
3. Persist assessments in a database.
4. Add student self-assessment + overlay comparison.
