# Capstone Starter: how to set it up

`app.py` is the Portfolio Project 2 Streamlit starter with three additions: every turn is saved
in **your own Google Sheet** (criterion 3.6), each reply shows **which part answered it**, and a
chatbot that is lost can use **your FAQ passages and a language model** (Element 4, no marks).

## A. Your chatbot online (3.5)

1. In `app.py`, PART 1 and PART 2: your own chatbot, `THRESHOLD`, and `intent_classifier.joblib`
   next to `app.py`. Students who submitted Part 2 on Streamlit copy their own PART 1 and PART 2.
2. In `requirements.txt`: the scikit-learn version of the Colab that trained the classifier.
3. Upload `app.py`, `requirements.txt` and `intent_classifier.joblib` to the `streamlit` folder of
   the Portfolio Project 2 repository. Do NOT upload `apps_script.gs` or any secret.
4. share.streamlit.io, Create app: the repository, branch `main`, main file path
   `streamlit/app.py`. Deploy. (Already deployed: the app restarts by itself after the upload.)

## B. The log in a Google Sheet (3.6), about 10 minutes

1. Google Drive, New, Google Sheets. Name it `chatbot log`. It stays private.
2. In the Sheet: Extensions, Apps Script. Delete what is there, paste `apps_script.gs`, Save.
3. Deploy, New deployment. Type (the gear): **Web app**. Execute as: **Me**. Who has access:
   **Anyone**. Deploy.
4. Authorise access with the same Google account. Google warns that it has not verified the
   app: it is your own script. Advanced, then Go to the project, then Allow.
5. Copy the **Web app URL** (it ends in `/exec`).
6. Streamlit: your app, Manage app, Settings, **Secrets**. Paste, with your own URL:

   ```toml
   LOG_URL = "https://script.google.com/macros/s/.../exec"
   ```
7. Save. Send the chatbot a message: a row appears in the Sheet. Click 👍 or 👎: a second row
   with the feedback appears.

Changed `apps_script.gs`? Deploy, Manage deployments, edit, Version: **New version**. The URL
stays the same.

## C. Optional, no marks: a language model when the chatbot is lost

In PART 4 write your own `FAQ` passages. In the Secrets add the key of Week 10:

```toml
OPENROUTER_API_KEY = "sk-or-..."
```

When the chatbot would say "Sorry, I did not understand", the app first looks for the closest FAQ
passage (Week 9) and lets the model answer from it (RAG); with no close passage, the model answers
from all the passages; if the model fails (no key, the free limit of 50 a day), the chatbot's own
fallback answers. Every one of these is logged as `rag`, `retriever`, `llm` or `fallback`.

## D. The 3.6 loop: from the log to a better chatbot

1. In the Sheet: File, Download, Comma separated values.
2. The rows to read: `answered_by` is `fallback`, `llm` or `rag`; feedback 👎; confidence just
   above `THRESHOLD`.
3. Label the ones in scope. Add them to `intents.csv` with the source `log`.
4. Retrain in the Part 1 notebook. Measure on the **same, unchanged test set**.
5. README: accuracy before and after, and three or four example messages (anonymised).
6. Upload the new `intent_classifier.joblib`. **Never** upload the log itself.

## E. Telegram in Colab: the same Sheet

Put `LOG_URL` in Colab's secrets, then, in the bot's message handler, after the reply:

```python
import requests
from google.colab import userdata
LOG_URL = userdata.get("LOG_URL")
requests.post(LOG_URL, json={"time": str(update.message.date), "user": str(hash(chat_id)),
                             "message": text, "reply": answer}, timeout=10)
```

## If something goes wrong

* A yellow box "rows could not be saved": the URL is wrong, or Who has access is not Anyone.
* Manage app shows the log: `ModuleNotFoundError` means a line is missing in `requirements.txt`.
* The app sleeps when nobody visits; the next visitor wakes it, which takes up to a minute.
