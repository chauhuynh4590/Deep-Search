# Agentic Deep Researcher

A web-based research assistant that combines a FastAPI backend and a Streamlit frontend, orchestrating multi-agent research workflows to answer complex queries and generate detailed reports.

---

## 🚀 Setup

### Installing `uv` (Python package manager)

This project uses [`uv`](https://github.com/astral-sh/uv) for fast dependency management. If you don't have `uv` installed, follow the steps below:

#### 1. Check if you have `uv` installed:

```bash
uv --version
```
If you see a version number, you already have `uv` installed. If you get a "command not found" error, install it using one of the following methods:

#### 2. Install `uv`

- **Using pipx (recommended):**
  ```bash
  pipx install uv
  ```
- **Using pip:**
  ```bash
  pip install uv
  ```
- **Using Homebrew (macOS):**
  ```bash
  brew install uv
  ```

For more information, see the [official uv installation guide](https://github.com/astral-sh/uv#installation).

### 1. Clone the Repository
```bash
git clone https://github.com/chauhuynh4590/Deep-Search.git
cd Deep-Search
```

### 2. Sync Dependencies with uv
```bash
uv sync
```

### 3. Environment Variables
Copy the example file and fill in your secrets:
```bash
cp .env.example .env
```
Edit `.env` and provide your actual API keys and settings.

### 4. Run the Backend (FastAPI)
```bash
uv run uvicorn api:app --reload --port 8000
```

### 5. Run the Frontend (Streamlit)

---

**Note:** The first time you use features that involve uploading files or images (such as document/image OCR), the process may take longer. This is because the application uses the `docling` library for OCR, which will automatically download the necessary AI models on first use. Subsequent uses will be much faster.

---
```bash
uv run streamlit run app.py
```

---

## 🛠️ Technical Overview and Key Components

- **`api.py`**: FastAPI backend exposing `/query` (main research endpoint) and `/status` (health check).
- **`app.py`**: Streamlit UI for uploading files, entering queries, and viewing/downloadable results.
- **`agents.py`**: Orchestrates multi-agent research crews, using LLMs and web search tools (e.g., LinkUp).
- **File Upload & Extraction**: Supports images, PDFs, and DOCX. Extracted content is included in queries.
- **PDF Generation**: Converts markdown research output to downloadable PDF.

---

## 🏗️ System Architecture

> **Note:** Mermaid diagrams render in GitHub and supported Markdown viewers. If you see a rendering error, view this file on GitHub or a compatible tool.

```mermaid
graph TD
    User("User")
    Streamlit("Streamlit UI<br/>(app.py)")
    FastAPI("FastAPI Backend<br/>(api.py)")
    Crew("Research Crew<br/>(agents.py)")
    APIs("External APIs<br/>(LinkUp, Gemini)")

    User --> Streamlit
    Streamlit --> FastAPI
    FastAPI --> Crew
    Crew -->|Web Search/LLM| APIs
    Crew --> FastAPI
    FastAPI --> Streamlit
    Streamlit -->|Display/Download| User
```

---

## 🔄 Solution Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Streamlit UI
    participant F as FastAPI API
    participant R as Research Crew
    U->>S: Enter query / Upload file
    S->>F: POST /query {input}
    F->>R: run_research(input)
    R->>R: Multi-agent search, analysis, synthesis
    R->>F: Return result
    F->>S: Return result
    S->>U: Display result, download PDF
```

---

## 🧪 Sample Inputs/Outputs

### API Example
**Request:**
```json
POST /query
{
  "input": "What are the latest advances in quantum computing?"
}
```
**Response:**
```json
{
  "result": "1. Executive Summary: ...\n2. Key Findings: ... [1] ... [2] ..."
}
```

### UI Example
- **Input:** User enters a research question and/or uploads a PDF.
- **Output:**
  - Detailed markdown report displayed in the UI
  - Option to download the report as a PDF

---

## 📈 Notes
- The system requires valid API keys for Gemini and LinkUp.
- Supported file types: png, jpg, jpeg, pdf, docx.
- For more details, see comments in `app.py`, `api.py`, and `agents.py`.

---

## 📬 Contact
For questions or support, please open an issue or contact the maintainer.
