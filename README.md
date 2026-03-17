# Autonomous Job Hunter

A self-hosted job hunting assistant that scrapes remote job boards, ranks openings, and delivers personalized digests via email, Telegram, or WhatsApp.

## 🚀 Features

- **Job Scraping**: Aggregates listings from multiple sources (RemoteOK, Remote.co, WeWorkRemotely, LinkedIn, etc.).
- **Ranking & Deduplication**: Filters and ranks jobs based on relevance and avoids duplicates.
- **Delivery Options**: Sends job digests via email, Telegram, or WhatsApp.
- **Agent Modules**: Includes tools to analyze job descriptions, tailor resumes, and generate cover letters.
- **Dashboard**: Provides a local Streamlit dashboard for monitoring and interaction.

## 🧩 Repository Structure

- `scrapers/` – Job board scrapers and runner logic.
- `core/` – Core scheduling, pipeline, ranking, and deduplication logic.
- `delivery/` – Email, Telegram, and WhatsApp delivery integrations.
- `agents/` – AI-powered modules for cover letters, resume tailoring, and interview prep.
- `dashboard/` – Streamlit app for local monitoring.

## ⚙️ Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the `.env` template and add your secrets:
   ```bash
   cp .env.example .env
   ```

4. Run the dashboard (optional):
   ```bash
   streamlit run dashboard/app.py
   ```

## ▶️ Running the job pipeline

```bash
python scheduler.py
```

## 🗂️ Notes

- **Do not commit** `.env` or other secret files. This repo includes a `.gitignore` to help keep secrets out of source control.
- If GitHub flags a secret in your history, rotate the secret and remove it from the repo history.

---

*Built with automation in mind — customize scrapers, delivery channels, and agents to match your workflow.*
