# Personio HR Data Export Integration

A lightweight, containerized ETL tool to extract HR data and documents from Personio and transform them into clean CSV files.

## 🚀 Features

- **Automated Extraction**: Fetches employee master data, employment details, and compensation.
- **Document Backup**: Automatically downloads employee documents and organizes them by employee ID.
- **Data Transformation**: Flattens nested JSON data into a clean, well-structured CSV.
- **Reporting**: Generates a department-level summary with employee counts and average salaries.
- **Flexible Scheduling**: Built-in scheduler for daily/weekly exports.
- **Docker Ready**: Easy deployment as a lightweight container.

## 🛠️ Tech Stack

- **Python 3.11+**
- **Requests** (HTTP Client)
- **APScheduler** (Job Scheduling)
- **Flask** (Health Check Server)
- **PyYAML** & **python-dotenv** (Configuration)
- **Docker** (Containerization)

## 📁 Project Structure

```text
personio-hr-export/
├── app/                  # Application source code
│   ├── api/              # Personio API client
│   ├── config/           # Configuration handling
│   ├── etl/              # ETL logic (Extract, Transform, Load)
│   ├── documents/        # Document downloader
│   ├── scheduler/        # Job scheduler
│   ├── utils/            # Shared utilities (logging, errors)
│   └── web/              # Web health check server
├── output/               # Exported files (CSV and documents)
├── Dockerfile            # Container definition
├── config.yml            # Main configuration
└── .env.example          # Environment variables template
```

## ⚙️ Configuration

### 1. Environment Variables (`.env`)

Create a `.env` file from `.env.example`:

```bash
PERSONIO_CLIENT_ID=your_client_id
PERSONIO_CLIENT_SECRET=your_client_secret
PERSONIO_BASE_URL=https://api.personio.de
```

### 2. Application Config (`config.yml`)

```yaml
export:
  output_path: ./output
  include_documents: true

schedule:
  enabled: true
  cron: "0 2 * * *"  # Runs daily at 2:00 AM

logging:
  level: INFO
```

## 🏃 Getting Started

### Using Docker (Recommended)

1. Build the image:
   ```bash
   docker build -t personio-etl .
   ```

2. Run the container:
   ```bash
   docker run -d --name personio-etl --env-file .env --mount type=bind,source="$(pwd)/output",target=/app/output personio-etl
   ```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app/main.py
   ```

## 📊 Outputs

- `output/personio_employee_export.csv`: Main employee data.
- `output/department_summary.csv`: Department-level statistics.
- `output/documents/{employee_id}/`: Employee document backups.

## 🩺 Health Check

When running with the scheduler enabled, a health check server is available at `http://localhost:5000/health`.

## 🔒 Security Notes

- API credentials should only be stored in `.env` or passed as environment variables.
- The `output` directory should be secured and ideally mounted to a protected volume.
- The Docker container runs as a non-root user for enhanced security.
