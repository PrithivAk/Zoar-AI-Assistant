# Zoar — Multi-Agent Personal AI Assistant

A Streamlit demo combining three specialist agents behind one router:

- **Wellness Agent** — daily mood check-ins, logged to SQLite, shown as a trend chart
- **Shopping Agent** — semantic product search (sentence-transformers + FAISS) over a small demo catalog
- **Interview Agent** — mock interview Q&A with dynamic follow-ups and end-of-session feedback

An **Orchestrator** classifies each message and routes it to the right agent.

```
User → Orchestrator (intent router) → Wellness / Shopping / Interview agent → reply
                                    ↘ shared SQLite memory (mood_logs, chat_history)
```

## 1. Setup

```bash
cd zoar-ai-assistant
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Get a free API key

You need **one** of these (both have generous free tiers):

- **Groq** (recommended — fast & free): https://console.groq.com → create an API key
- **OpenAI**: https://platform.openai.com

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
# then edit .env and paste your key
```

## 3. Run it

```bash
streamlit run app.py
```

This opens a browser tab with three tabs: Chat, Mood Trend, Mock Interview.

## 4. Test individual pieces (no Streamlit needed)

```bash
python3 orchestrator.py          # test intent routing
python3 agents/wellness_agent.py # test mood check-in + scoring
python3 agents/shopping_agent.py # test semantic product search
python3 agents/interview_agent.py# test question + follow-up + feedback
```

## Project structure

```
zoar-ai-assistant/
├── app.py                  # Streamlit UI (chat, mood trend, mock interview tabs)
├── orchestrator.py         # Intent router (LLM call → wellness/shopping/interview/general)
├── llm_client.py           # Swaps between Groq/OpenAI with one env var
├── db.py                   # SQLite: mood_logs + chat_history tables
├── agents/
│   ├── wellness_agent.py
│   ├── shopping_agent.py
│   └── interview_agent.py
├── data/
│   ├── products.csv        # demo product catalog for Shopping Agent
│   └── questions.json      # HR/behavioral/technical question bank
├── requirements.txt
├── .env.example
└── zoar.db                  # created automatically on first run
```

## Next steps (per the original 8-week plan)

1. **Voice pipeline** — add `SpeechRecognition` for mic input and `gTTS` for spoken replies once the text version works end-to-end. Don't debug voice + agents at the same time.
2. **Deploy** — push to GitHub, deploy free on Streamlit Community Cloud (one click from the repo).
3. **Polish for report/demo**:
   - Screenshot/record the three flows (mood check-in, shopping search, mock interview)
   - Add a short "Future Scope" section: more agents, multilingual (Tamil/Hindi) input, encrypting mood logs (nice callback to your Cybersecurity coursework)
   - Optional: add a simple login so mood data isn't shared across users on a shared deployment

## Notes

- The Shopping Agent's embedding model (`all-MiniLM-L6-v2`) runs **locally and free** — no API cost for search itself; only the final "phrase a recommendation" step calls the LLM.
- All agent prompts are intentionally short and editable — tune them in each agent file to change Zoar's tone.
- `zoar.db` is a plain SQLite file; delete it any time to reset all mood/chat history.
