# 🧠 CODING SPECIFICATION  
**Personio HR Data Export Integration (Dockerized Python ETL)**

---

## 1. Objective

Build a **lightweight, customer-deployable ETL tool** that:
- Extracts HR data and documents from the **Personio API**
- Transforms the data into a **clean, well-structured CSV**
- Generates a **department-level summary**
- Runs **locally or scheduled**
- Is **secure, configurable, and easy to use**
- Is packaged and distributed as a **Docker container**

The solution must follow **senior engineering best practices** and be understandable by non-technical customers.

---

## 2. Technology Stack (MANDATORY)

### Core Stack
- **Language:** Python 3.11+
- **Containerization:** Docker
- **Web server (optional):** Flask (only for health + scheduler)
- **Scheduler:** APScheduler
- **HTTP Client:** \`requests\`
- **CSV handling:** \`csv\` or \`pandas\` (prefer standard \`csv\`)
- **Config parsing:** \`pyyaml\`
- **Environment variables:** \`python-dotenv\`
- **Logging:** Python \`logging\` module

### Explicit Non-Goals
- No database
- No external hosting
- No UI
- No cloud dependency
- No heavy frameworks

---

## 3. High-Level Responsibilities

The system must:

1. Authenticate securely against Personio API
2. Extract:
   - Employee master data
   - Employment details
   - Compensation (base salary)
   - Employee documents (download locally)
3. Transform nested JSON → flat CSV schema
4. Generate:
   - \`personio_employee_export.csv\`
   - \`department_summary.csv\`
5. Support:
   - Manual execution
   - Scheduled execution
6. Log clearly and fail gracefully
7. Be configurable without code changes

---

## 4. Project Structure (REQUIRED)

\`\`\`
personio-hr-export/
│
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── config_loader.py
│   │   └── config_schema.py
│   │
│   ├── api/
│   │   ├── personio_client.py
│   │   └── endpoints.py
│   │
│   ├── etl/
│   │   ├── extractor.py
│   │   ├── transformer.py
│   │   ├── loader.py
│   │   └── post_processor.py
│   │
│   ├── scheduler/
│   │   └── scheduler.py
│   │
│   ├── documents/
│   │   └── document_downloader.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── errors.py
│   │   └── helpers.py
│   │
│   └── web/
│       └── app.py
│
├── output/
│   ├── personio_employee_export.csv
│   ├── department_summary.csv
│   └── documents/
│
├── config.yml
├── .env.example
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
\`\`\`

---

## 5. Configuration Specification

### \`.env\`
\`\`\`
PERSONIO_CLIENT_ID=
PERSONIO_CLIENT_SECRET=
PERSONIO_BASE_URL=https://api.personio.de
\`\`\`

### \`config.yml\`
\`\`\`yaml
export:
  output_path: ./output
  include_documents: true

schedule:
  enabled: true
  cron: "0 2 * * *"

logging:
  level: INFO
\`\`\`

---

## 6. Personio API Integration

### Authentication
- OAuth token retrieval
- Token passed via Authorization header
- Centralized token handling

### Required Endpoints
- Employees
- Employment details
- Compensation
- Documents

### Client Rules
- Pagination support
- Timeout handling
- Retries
- Rate-limit awareness

---

## 7. Data Transformation Rules

### CSV File
**Filename:** \`personio_employee_export.csv\`

**Schema:**
- employeeID
- First name
- Last name
- email
- status
- Hire date
- Termination date
- position
- department
- team
- Supervisor name
- location
- Weekly working hours
- Employment type
- Cost center
- Base Salary
- Last modified

### Formatting
- Dates: YYYY-MM-DD
- Empty values: blank
- UTF-8 encoding

---

## 8. Document Handling

### Behavior
- Enabled via config
- Download documents per employee
- Directory:
\`\`\`
output/documents/{employee_id}/
\`\`\`

---

## 9. Post-Processing

Generate \`department_summary.csv\`

### Columns
- department
- employee_count
- average_base_salary

---

## 10. Scheduling

### Supported Modes
- Built-in APScheduler
- External scheduler (cron, task scheduler)

---

## 11. Logging Standards

\`\`\`
INFO Starting HR export job
INFO Fetched 482 employees
INFO CSV generated successfully
WARNING Document download failed
ERROR API token missing
\`\`\`

---

## 12. Error Handling

### Custom Exceptions
- ConfigError
- AuthenticationError
- APIError
- FileWriteError

---

## 13. Docker Requirements

- Slim Python base image
- Non-root user
- Clean dependency install
- Volume-mounted output

---

## 14. Documentation

README must include:
- Setup
- Configuration
- Running manually
- Scheduling
- Errors
- Security notes

---

## 15. Quality Expectations

- Readable
- Modular
- Maintainable
- No over-engineering

---

## 16. Completion Criteria

- Container runs [x]
- CSV generated [x]
- Logs readable [x]
- Config-driven [x]
- Customer-ready [x]

---

## 🏗️ Implementation Progress

1. **Project Initialization & Structure** ✅
2. **Config & Logging Foundation** ✅
3. **Personio API Client** ✅
4. **ETL Core Implementation** ✅
5. **Document Downloader** ✅
6. **Scheduling & Web Health Check** ✅
7. **Main Entry Point** ✅
8. **Dockerization** ✅
9. **Documentation** ✅
