import json, os, re
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="LeafGuard", page_icon="🍃", layout="centered")

   MODEL = "gemini-3.8-flash"

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden}
.block-container {padding-top:0 !important; max-width:760px}
.hero {background:linear-gradient(135deg,#1f9d55,#0f6b3a); color:#fff; text-align:center;
       padding:48px 20px 60px; border-radius:0 0 32px 32px; margin:0 -1rem 24px}
.hero h1 {color:#fff; font-size:2.3rem; margin:10px 0 6px; line-height:1.15}
.hero p {opacity:.92; margin:0}
.logo {display:inline-block; background:rgba(255,255,255,.18); padding:6px 16px;
       border-radius:99px; font-weight:800}
.pill {display:inline-block; padding:5px 14px; border-radius:99px; font-weight:700; font-size:.85rem}
.ok {background:#e6f4e9; color:#1f9d55} .mid {background:#fef3c7; color:#b45309} .bad {background:#fee2e2; color:#b91c1c}
.crop {color:#6b7f72; font-weight:700; text-transform:uppercase; letter-spacing:.08em; font-size:.8rem}
.stButton>button {background:linear-gradient(135deg,#1f9d55,#0f6b3a); color:#fff; border:0;
       border-radius:14px; padding:.7rem 1.2rem; font-weight:700; width:100%}
.stButton>button:hover {color:#fff; transform:translateY(-1px)}
</style>
<div class="hero">
  <div class="logo">🍃 LeafGuard</div>
  <h1>Know what's wrong with your plant in seconds</h1>
  <p>Upload a leaf photo and get a diagnosis, treatment and prevention tips.</p>
</div>
""", unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None
if not api_key:
    st.error("Missing GEMINI_API_KEY. Add it in your host's secrets / environment variables.")
    st.stop()
client = genai.Client(api_key=api_key)

PROMPT = """You are LeafGuard, an expert plant pathologist. Look at the attached plant leaf photo.
Reply with ONLY a JSON object, no markdown, in this exact shape:
{"isLeaf":true,"crop":"string","condition":"disease name or Healthy","healthy":false,"confidence":0,
"severity":"None|Mild|Moderate|Severe","summary":"2 short sentences","symptoms":["3-4 short signs"],
"treatment":["3-5 practical steps, organic and chemical options"],"prevention":["3-4 short tips"]}
If the image is not a plant leaf: isLeaf false, crop "Unknown", condition "No leaf detected",
healthy false, confidence 0, severity "None", and ask for a clearer photo in summary. Be honest about uncertainty."""


def diagnose(file) -> dict:
    img = Image.open(file).convert("RGB")
    img.thumbnail((1024, 1024))
    resp = client.models.generate_content(
        model=MODEL,
        contents=[img, PROMPT],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(re.search(r"\{.*\}", resp.text, re.S).group(0))


tab1, tab2 = st.tabs(["📁 Upload photo", "📷 Use camera"])
with tab1:
    photo = st.file_uploader("Leaf photo", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
with tab2:
    cam = st.camera_input("Take a photo", label_visibility="collapsed")
file = photo or cam

if file:
    st.image(file, use_container_width=True)
    if st.button("Diagnose leaf"):
        with st.spinner("Examining your leaf..."):
            try:
                st.session_state["result"] = diagnose(file)
            except Exception as e:
                st.session_state["result"] = None
                st.error(f"Something went wrong: {e}")

d = st.session_state.get("result")
if d and file:
    sev = "✓ Healthy" if d["healthy"] else f'{d["severity"]} severity'
    cls = "ok" if d["healthy"] else ("bad" if d["severity"] == "Severe" else "mid")
    st.markdown(f'<div class="crop">{d["crop"]}</div><h2 style="margin:0">{d["condition"]}</h2>'
                f'<span class="pill {cls}">{sev}</span>', unsafe_allow_html=True)
    st.progress(min(max(int(d["confidence"]), 0), 100) / 100, text=f'Confidence {int(d["confidence"])}%')
    st.write(d["summary"])
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("**🔍 What to look for**")
            for s in d["symptoms"]: st.markdown(f"- {s}")
    with c2:
        with st.container(border=True):
            st.markdown("**💊 Treatment**")
            for s in d["treatment"]: st.markdown(f"- {s}")
    with st.container(border=True):
        st.markdown("**🛡️ Prevention**")
        for s in d["prevention"]: st.markdown(f"- {s}")

st.caption("LeafGuard gives a first opinion, not a professional diagnosis.")
