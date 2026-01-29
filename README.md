# AI Credential Auditor

## Project Overview
AI Credential Auditor is an AI-powered recruitment backend designed to automate the vetting process of international doctors and nurses migrating to Canada and the USA. Utilizing Retrieval-Augmented Generation (RAG), the system compares candidate CVs against the 2026 regulatory rulebooks (CPSO, NNAS, FSMB) to ensure compliance and eligibility.

## Technical Stack
*   **Backend**: Django, Django REST Framework (DRF)
*   **Async Tasks**: Celery + Redis
*   **AI/ML**: LangChain, OpenAI GPT-4, ChromaDB (Vector Store)
*   **Database**: PostgreSQL
*   **Integration**: GoHighLevel (GHL) via Webhooks

## System Architecture
The system follows an event-driven architecture triggered by external webhooks:
1.  **GHL Webhook**: A candidate submission triggers a webhook from GoHighLevel to the Django API.
2.  **Django API**: The endpoint validates the request and offloads the processing to a Celery task.
3.  **Celery Task**: An asynchronous worker picks up the task to prevent blocking the API.
4.  **LangChain RAG**: The AI engine retrieves relevant regulatory rules from ChromaDB and uses GPT-4 to audit the CV against these rules.
5.  **GHL Update**: The audit results are sent back to GoHighLevel to update the candidate's profile.

## Features
*   **2026 Rule Engine**: Up-to-date compliance checks against the latest regulatory frameworks.
*   **PDF Ingestion Pipeline**: Automated parsing and vectorization of regulatory handbooks.
*   **Async Audit Processing**: Scalable background processing for handling high volumes of applications.

## Installation

### Prerequisites
*   Python 3.10+
*   PostgreSQL
*   Redis

### Setup Steps
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ai-credential-auditor
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Redis:**
    Ensure Redis is running locally or provide a remote URL in the configuration.
    ```bash
    redis-server
    ```

## Configuration
Create a `.env` file in the project root with the following variables:

```env
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# AI & Vector Store
OPENAI_API_KEY=sk-...
CHROMA_DB_PATH=./chroma_db

# Integrations
GHL_ACCESS_TOKEN=your_ghl_token
```

## Usage

### Ingest Regulatory Handbooks
Before running audits, ingest the PDF rulebooks into the vector store:
```bash
python manage.py ingest_handbooks
```

### Run the Application
1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```

2.  **Start the Celery worker:**
    ```bash
    celery -A config worker --loglevel=info
    ```

## API Documentation

### Webhook Endpoint
Triggers the audit process for a candidate.

*   **URL**: `/api/ghl-webhook/`
*   **Method**: `POST`
*   **Content-Type**: `application/json`

#### Sample Payload
```json
{
  "contact_id": "ghl_contact_12345",
  "cv_text": "Experienced Registered Nurse with 5 years in ICU...",
  "target_region": "Ontario, Canada"
}
```
