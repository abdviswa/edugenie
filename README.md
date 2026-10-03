# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a FastAPI + HTML/CSS/JavaScript educational assistant based on the supplied project document. It provides:

- Question answering (`/qa`)
- Beginner-friendly concept explanation (`/explain`)
- Three-question MCQ generation with four options each (`/quiz`)
- Educational passage summarization (`/summarize`)
- Beginner-to-advanced learning paths (`/learn/recommendations`)

## Architecture

```text
Browser
  │
  ├── HTML/CSS/JS
  │
  ▼
FastAPI
  ├── qna.py
  ├── explanation_module.py
  ├── quiz_module.py
  ├── summary_module.py
  └── learning_path.py
        │
        ▼
 services/gemini_service.py
        │
        ▼
 Google Gemini API
```

The document specified Gemini 1.5 Pro and LaMini-Flan-T5-783M. The code keeps the LaMini option for local explanation, but defaults to Gemini because the current Google SDK/model catalog changes over time. Configure `GEMINI_MODEL` in `.env` if needed.

## Windows VS Code setup

1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the commands from Command Prompt instead:

```cmd
.venv\Scripts\activate
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Create `.env` from `.env.example` and put your Gemini API key in:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
LOCAL_EXPLANATION_ENABLED=false
```

Never commit `.env` or expose the API key in frontend JavaScript.

## Run

```powershell
uvicorn main:app --reload
```

Open http://127.0.0.1:8000

Health check: http://127.0.0.1:8000/health

## Test

Run automated tests:

```powershell
pytest -q
```

Manual feature checks:

1. Ask: `Which is the largest ocean?`
2. Explain: `Pythagoras theorem`
3. Quiz: paste a paragraph and verify exactly 3 questions and 4 options each.
4. Summary: paste a long study paragraph.
5. Learning path: `SQL`, level `beginner`.

## Local LaMini explanation (optional)

The supplied document specifies LaMini-Flan-T5-783M for explanations. To use it, set:

```env
LOCAL_EXPLANATION_ENABLED=true
LOCAL_EXPLANATION_MODEL=MBZUAI/LaMini-Flan-T5-783M
```

The first use downloads the model from Hugging Face and requires additional disk/RAM. If the local model cannot load, EduGenie safely falls back to Gemini.

## API examples

```powershell
curl -X POST http://127.0.0.1:8000/qa `
  -H "Content-Type: application/json" `
  -d '{"text":"What is normalization in DBMS?"}'
```

```powershell
curl -X POST http://127.0.0.1:8000/learn/recommendations `
  -H "Content-Type: application/json" `
  -d '{"topic":"SQL","level":"beginner"}'
```
