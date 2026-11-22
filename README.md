# FDE Training

Coursework, homework, and mini projects from the FDE training program. The work moves from Python basics to FastAPI services backed by PostgreSQL, then to TypeScript, plain HTML front ends, and React.

## Repository layout

```
FDETraining/
├── fde-react-check/                         # Vite + React starter used to check the toolchain
└── src/
    ├── *.py                                 # Week 1 Python basics (datatypes, conditions, match, dicts, FastAPI intro)
    ├── data/                                # CSV read/filter exercise
    ├── EmployeeAPI/                         # Small FastAPI CRUD example
    ├── HomeworkWeek1/                       # Invoice reading and a JSON-backed invoice API
    ├── HomeworkWeek2/, Week2ClassRoom/      # Filtering and class exercises
    ├── HomeworkWeek2Day1_assignment_paymentsAndInvoices/
    │                                        # Invoices + payments + reconciliation API (routers / services / repository)
    ├── HomeworkWeek2Day2_gpay/              # psycopg basics, then a refactor into layers
    ├── HomeworkWeek2Day2_invoice_postgress/ # The invoice API moved onto PostgreSQL
    ├── Homeworkweek2Day2-Refactor/          # Layered refactor of the JSON-backed API
    ├── week2_miniProject/                   # Diabetes readmission risk API (FastAPI + Postgres)
    ├── week2_miniProject_with_BE/           # Same API with a simple HTML front end
    ├── week3_miniProject_with_HTML/         # Care queue API + search / add / update HTML pages
    ├── Week3_classRoom_basicsOfTypeScript/  # TypeScript basics and fetch examples
    ├── week4_classRoom_fde-patientManagement-react/
    │                                        # React + TypeScript UI for the encounter API
    └── week4_day2_miniProject/              # Week 4 backend (in progress)
```

## Main project: patient risk and care queue

The mini projects build on each other and use the UCI diabetes dataset (`data/diabetic_data.csv`):

1. **Week 2**: load encounters into PostgreSQL, calculate a risk score for each encounter, group scores into `LOW` / `MEDIUM` / `HIGH`, and expose them through FastAPI.
2. **Week 3**: add care interventions and HTML pages to search patients, add encounters, and update intervention status.
3. **Week 4**: a React front end ([week4_classRoom_fde-patientManagement-react](src/week4_classRoom_fde-patientManagement-react/README.md)) that pages through encounters.

Each mini project's own README holds the business summary: the problem, the users, the assumptions, and the next steps.

### Prerequisites

- Python 3.11+
- PostgreSQL running locally
- Node.js 20+ (for the React apps)

### Running the backend (week 3 version)

```bash
cd src/week3_miniProject_with_HTML

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create the database, users and schema (see sql/createUser.sql, sql/schema.sql, sql/seed.sql)
psql -U postgres -f sql/createUser.sql
psql -U postgres -d <your_db> -f sql/schema.sql

# Connection string
echo 'DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<your_db>' > .env

# Load the CSV, calculate risk scores and seed care interventions
python data_loader.py

# Start the API on the port the front ends expect
uvicorn main:app --reload --port 8001
```

Interactive API docs are at http://127.0.0.1:8001/docs once the server is running.

### Key endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/encounters` | All encounters with risk score and level |
| GET | `/encounters/{encounter_id}` | One encounter |
| GET | `/encounters/patient/{patient_nbr}` | Encounters for one patient |
| POST | `/encounters` | Create an encounter |
| GET | `/careQueue` | Prioritized care queue |
| GET | `/careQueue/highRisk` | High-risk patients only |
| PATCH | `/interventions/{encounter_id}` | Update intervention status or owner |
| GET | `/operational_summary` | Aggregate operational metrics |
| GET | `/readmission_analysis` | Readmission breakdown |

### Front ends

- **HTML pages** (week 2 / 3): open `index.html`, `searchPatient.html`, `addEncounter.html` or `updatePatientDetails.html` in a browser. The API base URL is set in `config.js` (`http://127.0.0.1:8001`).
- **React** (week 4): see [its README](src/week4_classRoom_fde-patientManagement-react/README.md).

## Environment and secrets

- `.env` files are gitignored. Each project that needs a database includes an `.env_example` / `.env_ex` template. Copy it to `.env` and fill in your local credentials.
- The SQL scripts contain **local development passwords only**. Do not reuse them anywhere else.
