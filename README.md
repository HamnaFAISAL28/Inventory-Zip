# Inventory App

Small Python inventory manager (SQLite + CLI) used as a SonarQube demo project.

## Run
```bash
pip install -r requirements.txt
python main.py add PEN-001 "Blue Pen" 1.5 --quantity 10 --category stationery
python main.py list
python main.py sell PEN-001 3
python main.py report
```

## Test + coverage
```bash
pytest            # prints coverage and writes coverage.xml
```

## SonarCloud
- `sonar-project.properties` – scanner config (reads `coverage.xml`)
- `.github/workflows/sonar.yml` – CI: tests, coverage, scan
- Add repo secret `SONAR_TOKEN` (SonarCloud host is built in)
- Set `sonar.organization` and `sonar.projectKey` to your SonarCloud values

## Planted issues
See `FIXES.md` for the 2 deliberate issues and their fixes.
