# IMS - Institute Management System
### SGGS Nanded · Academic Year 2024–25

Live dashboard connected to Google Sheets. Data auto-refreshes every 30 seconds.

## Deploy on Streamlit Community Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — live in ~2 minutes ✅

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py` — main Streamlit app
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — theme & server config

## How dynamic updates work
The app fetches data directly from your public Google Sheet every 30 seconds (configurable).
Any edits you make to the Google Sheet appear automatically — no redeployment needed.
