# AI Interview Agent

## Overview

AI Interview Agent is a Streamlit-based application that conducts role-based interviews using an LLM (default model `gpt-4o-mini`). It asks technical, behavioral, and situational questions, adapts follow-ups, evaluates each answer, and produces a final report with a recommendation.

## Features

- Role selection (Software Engineer, Data Scientist, DevOps, Product Manager, Frontend)
- Adaptive follow-up questions based on candidate responses
- LLM-powered evaluation on: relevance, technical depth, clarity, structure (STAR)
- Conversation history tracking
- Final interview report with strengths, weaknesses, and recommendation (Hire/Consider/Reject)

## Project Structure

```
ai_interview_agent/
│── app.py            → Streamlit UI  
│── interviewer.py    → Question generator + conversation logic  
│── evaluator.py      → Answer scoring + evaluation  
│── prompts.py        → System prompts + question templates  
│── requirements.txt 
│── README.md
│── architecture.png (Mermaid diagram text)
```

## Setup

1. Clone or copy the project folder.
2. Create a virtual environment and activate it.

Windows PowerShell example:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Set your OpenAI API key in environment variable `OPENAI_API_KEY` or paste it into the app when prompted.

Alternatively add it to the provided `.env` file.

### New features in this upgraded build

- Adaptive interview engine that changes question difficulty by monitoring confidence, length, and missed topics.
- Live scoring dashboard during interviews: progress bars, radar charts, and detailed breakdowns.
- Interviewer personas that modify question tone and evaluation style.
- Voice interview mode: speech-to-text (Whisper) and text-to-speech (pyttsx3).
- Deep evaluation module using embeddings to compare to ideal answers.
- Resume upload and basic parsing to tailor questions.
- PDF report export and an HR dashboard backed by SQLite.


## Running the App

From the project root run:

```powershell
streamlit run app.py
```

The Streamlit UI will open. Select a role, click `Start Interview`, answer questions, and click `End Interview` to get the final report.

## Scoring Methodology

Each answer is evaluated across four categories:
- Relevance (0-25)
- Technical depth (0-25)
- Clarity (0-25)
- Structure using the STAR method (0-25)

The LLM returns a JSON with a numeric score (0-100), a breakdown for each category, strengths, weaknesses, and a recommendation.

Final decision thresholds:
- 75+ : Hire
- 50-74 : Consider
- <50 : Reject

## Architecture

See `architecture.png` (Mermaid diagram) for a high-level view of components and flow.

## Running the new features

Make sure to install the updated requirements and set `OPENAI_API_KEY` and `OPENAI_MODEL` as needed. The app now requires extra packages: `pyttsx3`, `fpdf2`, `plotly`, `PyPDF2`.

If you want voice mode that uses the Whisper API, ensure your OpenAI account supports it and that you have sufficient quota. The TTS uses `pyttsx3` locally (no cloud cost).

## Future Improvements

- Persist conversation history to a database (Postgres, SQLite)
- Add user authentication
- Add multi-round panel interview orchestration
- Add richer rubric customization per role
- Implement streaming responses for lower latency

## Notes

- The app uses the OpenAI API for both follow-up generation and evaluation. Ensure you have sufficient quota.
- If the LLM call fails, the app uses a lightweight heuristic fallback for basic scoring.
