# Shiksha Copilot — working starter website

A Python Flask student learning website based on the supplied Mermaid flow:
student onboarding → quiz → performance analysis → learner profile → dashboard → weak-concept learning → feedback → profile update.

## Requirements
- Python 3.10+
- VS Code (recommended)

## Run on Windows
Open this folder in VS Code, then open Terminal.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

If PowerShell blocks environment activation, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

## Included in this starter
- Student onboarding and learning goal capture.
- Initial assessment and daily quiz using sample Python questions.
- Topic-level score tracking.
- Dashboard generated from saved quiz attempts.
- Weak-topic recommendations.
- What / Why / How lesson cards.
- Student teach-back text submission for review.
- Local JSON persistence for quick demo.

## Important limitations
This is a functional starter prototype, not the full AI marketplace. The questions are sample questions, not generated from uploaded PDFs yet. The teach-back feature currently saves a text explanation; it does not claim to verify mastery with AI. Authentication, PDF ingestion, LLM integration, video upload/transcription, creator rewards, and real payments are planned next phases.

For a demo only. Before public deployment, use a production secret, real authentication, secure database, upload validation, CSRF protection, and a proper deployment configuration.
