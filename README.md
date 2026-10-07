# Bulk Certificate Generator API

A FastAPI-based backend for generating certificates in bulk from a predefined certificate template.

The system accepts a single bulk request containing event information and a list of recipients. It creates a generation job, processes certificates independently, tracks job progress, stores certificate status in a relational database, and provides individual PDF and bulk ZIP downloads.

## Features

- Bulk certificate generation
- REST API using FastAPI
- Pydantic request validation
- SQLite relational database
- SQLAlchemy ORM
- Background certificate processing
- Individual certificate success/failure tracking
- Job progress tracking
- PDF certificate generation using ReportLab
- Individual PDF download
- Bulk ZIP download
- Automated Pytest test suite
- Swagger/OpenAPI documentation
- Docker support

## Architecture

```text
Client
   |
   v
FastAPI
   |
   +---- Pydantic Validation
   |
   v
Generation Job
   |
   v
Background Processing
   |
   +---- Certificate 1 --> PDF
   |
   +---- Certificate 2 --> PDF
   |
   +---- Certificate 3 --> PDF
   |
   v
SQLite Database
   |
   +---- Job Status
   +---- Certificate Status
   +---- Progress
   Project Structure
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── certificates.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── certificate_generator.py
│       └── job_processor.py
│
├── tests/
│   ├── test_jobs.py
│   ├── test_validation.py
│   ├── test_certificate_generation.py
│   └── test_retrieval.py
│
├── templates/
├── generated_certificates/
├── generated_archives/
│
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md

API Endpoints
Health Check
GET /health

Returns:
{
  "status": "healthy"
}

Create Generation Job
POST /api/jobs

Example request:
{
  "event_name": "Python Workshop 2026",
  "organization": "ZHCET AMU",
  "date": "2026-10-20",
  "recipients": [
    {
      "name": "Anant Gupta",
      "email": "anant@example.com",
      "certificate_type": "Participation"
    },
    {
      "name": "Rahul Sharma",
      "email": "rahul@example.com",
      "certificate_type": "Completion"
    }
  ]
}

Example response:
{
  "id": 1,
  "event_name": "Python Workshop 2026",
  "organization": "ZHCET AMU",
  "event_date": "2026-10-20",
  "status": "PENDING",
  "total_certificates": 2,
  "successful_certificates": 0,
  "failed_certificates": 0,
  "progress_percentage": 0.0
}

Get Job Status
GET /api/jobs/{job_id}

Example:
{
  "id": 1,
  "event_name": "Python Workshop 2026",
  "organization": "ZHCET AMU",
  "event_date": "2026-10-20",
  "status": "COMPLETED",
  "total_certificates": 2,
  "successful_certificates": 2,
  "failed_certificates": 0,
  "progress_percentage": 100.0
}

Get Certificates for a Job
GET /api/jobs/{job_id}/certificates

Returns the individual certificate records and their status.
Download Individual Certificate
GET /api/certificates/{certificate_id}/download

Returns the generated PDF.
Download All Certificates
GET /api/jobs/{job_id}/download

Returns a ZIP archive containing all successfully generated certificates for the job.
Certificate Processing
Each recipient is processed independently.
For example:
Recipient 1 -> SUCCESS
Recipient 2 -> SUCCESS
Recipient 3 -> FAILED
Recipient 4 -> SUCCESS

A failure for one recipient does not stop the remaining certificates from being generated.
Possible job states include:
PENDING
PROCESSING
COMPLETED
COMPLETED_WITH_ERRORS

Validation
The API validates:
- Recipient name
- Recipient email
- Certificate type
- Event name
- Organization
- Event date
- At least one recipient
Invalid requests return HTTP 422.
Database
The application uses SQLite with SQLAlchemy.
Two main tables are used:
generation_jobs
Stores:
- Event information
- Job status
- Total certificates
- Successful certificates
- Failed certificates
- Creation time
certificates
Stores:
- Recipient information
- Certificate type
- Individual status
- Generated file path
- Error information
- Job relationship
Background Processing
Certificate generation is performed using FastAPI background tasks.
This allows the API to return the generation job quickly while certificate files are generated in the background.
The client can then query:
GET /api/jobs/{job_id}

to check progress.
Running Locally
Clone the repository
git clone https://github.com/anantgupta19/bulk-certificate-generator.git
cd bulk-certificate-generator

Create virtual environment
Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1

Install dependencies
pip install -r requirements.txt

Run the application
uvicorn app.main:app --reload

API:
http://127.0.0.1:8000

Swagger documentation:
http://127.0.0.1:8000/docs

Running Tests
pytest -v
The current test suite covers:
- Job creation
- Input validation
- Certificate generation
- Job status and progress
- Individual certificate failure handling
- Certificate retrieval
- PDF download
- Bulk ZIP download
Docker
The application can also be run using Docker.
docker compose up --build

Swagger documentation:
http://localhost:8000/docs

Technology Stack
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- ReportLab
- Pytest
- Docker

Save it.

---

# 3. Create the Dockerfile

Open:

```text
D:\bulk-certificate-generator\Dockerfile

Paste:
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p generated_certificates generated_archives

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

Save.
I'm using Python 3.13 inside Docker rather than your local 3.14 environment to keep the container on a broadly supported Python version.