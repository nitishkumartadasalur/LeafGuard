# 🍃 LeafGuard
AI plant disease detection. Upload a leaf photo, get diagnosis, treatment and prevention tips.

## Run locally
```
pip install -r requirements.txt
export GEMINI_API_KEY=your_key     # Windows PowerShell: $env:GEMINI_API_KEY="your_key"
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push to GitHub. 2. share.streamlit.io -> New app -> pick repo, main file `app.py`.
3. Advanced settings -> Secrets: `GEMINI_API_KEY = "your_key"`

## Deploy on Render
New Web Service -> connect repo.
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Env vars: `GEMINI_API_KEY`, `PYTHON_VERSION=3.12.7`
