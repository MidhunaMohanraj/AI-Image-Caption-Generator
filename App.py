"""
app.py — AI Image Caption Generator
Upload any image → Get captions, alt text, tags, mood & social media posts
Uses BLIP (local, no API key) + optional Gemini for enhanced captions
"""  
     
import streamlit as st
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import google.generativeai as genai
import io
import base64
import json
import re
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Image Caption Generator",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .main { background: #07080d; }

  .hero {
    background: linear-gradient(135deg, #0f0818 0%, #07080d 55%, #001810 100%);
    border: 1px solid #1a1a2e;
    border-radius: 16px;
    padding: 38px 40px;
    text-align: center;
    margin-bottom: 24px;
  }
  .hero h1 { font-size: 42px; font-weight: 700; color: #fff; margin: 0 0 8px; }
  .hero p  { color: #64748b; font-size: 15px; margin: 0; }

  .result-card {
    background: #0c0d16;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
  }
  .result-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  .caption-text {
    font-size: 16px;
    line-height: 1.75;
    color: #e2e8f0;
    font-style: italic;
  }
  .tag-chip {
    display: inline-block;
    background: #12132a;
    border: 1px solid #2a2a50;
    color: #a78bfa;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px;
  }
  .stat-card {
    background: #0c0d16;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
  }
  .stat-val   { font-size: 24px; font-weight: 700; color: #a78bfa; }
  .stat-label { font-size: 10px; color: #475569; text-transform: uppercase;
                letter-spacing: 1.5px; margin-top: 4px; }

  .social-box {
    background: #080910;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 16px 18px;
    font-size: 14px;
    line-height: 1.75;
    color: #cbd5e1;
    margin: 8px 0;
    white-space: pre-wrap;
  }
  .platform-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  div.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 13px 28px;
    font-size: 15px;
    width: 100%;
  }
  div.stButton > button:hover { opacity: 0.85; }
  .stTextInput input, .stTextArea textarea {
    background: #0c0d16 !important;
    border-color: #1a1a2e !important;
    color: #e2e8f0 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Load BLIP model (cached) ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading BLIP vision model (~900MB on first run)...")
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model     = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        torch_dtype=torch.float32,
    )
    model.eval()
    return processor, model

# ── BLIP caption generation ────────────────────────────────────────────────────
def generate_blip_captions(image: Image.Image, processor, model) -> list[str]:
    """Generate multiple captions using BLIP with different prompts."""
    captions = []
    device   = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # 1. Unconditional caption
    inputs = processor(image, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=60, num_beams=5)
    captions.append(processor.decode(out[0], skip_special_tokens=True))

    # 2. Conditional captions with different prompts
    prompts = ["a photo of", "this image shows", "in this picture,"]
    for prompt in prompts:
        inputs = processor(image, prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=60, num_beams=5)
        cap = processor.decode(out[0], skip_special_tokens=True)
        # Remove the prompt prefix if present
        cap = re.sub(rf"^{re.escape(prompt)}\s*", "", cap, flags=re.IGNORECASE).strip()
        if cap and cap not in captions:
            captions.append(cap)

    return [c for c in captions if len(c) > 8]

# ── Gemini enhanced analysis ───────────────────────────────────────────────────
def gemini_analyse(image: Image.Image, blip_caption: str, api_key: str, tone: str) -> dict:
    """Use Gemini Vision to get rich analysis: alt text, tags, mood, social posts."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Convert PIL image to bytes
    buf = io.BytesIO()
    fmt = image.format or "JPEG"
    image.save(buf, format=fmt)
    img_bytes = buf.getvalue()

    prompt = f"""Analyse this image thoroughly and return a JSON object with exactly these keys:

{{
  "enhanced_caption": "A vivid, engaging one-sentence caption ({tone} tone, 15-25 words)",
  "alt_text": "Detailed accessibility alt text description (2-3 sentences, describe everything important)",
  "short_caption": "Ultra-short punchy caption under 10 words",
  "tags": ["list", "of", "12", "relevant", "hashtag", "keywords", "without", "the", "hash", "symbol"],
  "mood": "One word describing the mood/emotion of this image",
  "colors": ["3 to 5 dominant colors as descriptive names"],
  "scene_type": "Type of scene (e.g. portrait, landscape, product, food, architecture, abstract)",
  "instagram_post": "A complete Instagram caption with emojis and 8 relevant hashtags",
  "twitter_post": "A tweet-length caption under 280 chars with 3 hashtags",
  "linkedin_post": "A professional LinkedIn caption 2-3 sentences, no hashtags",
  "seo_title": "An SEO-optimised image title for web use"
}}

The BLIP model already detected: "{blip_caption}"
Build on that but make all outputs richer and more detailed.
Return ONLY valid JSON, no markdown, no explanation."""

    response = model.generate_content([
        {"mime_type": f"image/{fmt.lower()}", "data": base64.b64encode(img_bytes).decode()},
        prompt,
    ])

    raw = response.text.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```json\s*|^```\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# ── Image info ─────────────────────────────────────────────────────────────────
def image_info(image: Image.Image, file_bytes: bytes) -> dict:
    return {
        "size":   f"{image.width} × {image.height} px",
        "mode":   image.mode,
        "format": image.format or "Unknown",
        "kb":     f"{len(file_bytes)/1024:.0f} KB",
        "aspect": f"{image.width/image.height:.2f}",
    }

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🖼️ Caption Generator")
    st.markdown("---")

    st.markdown("### 🔑 Gemini API Key *(optional)*")
    api_key = st.text_input(
        "Free Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get FREE at https://aistudio.google.com"
    )
    if not api_key:
        st.info("Works without a key using BLIP.\nAdd Gemini key for **social posts, SEO titles, alt text & more**.")

    st.markdown("---")
    st.markdown("### 🎭 Caption Tone")
    tone = st.selectbox("Select tone for enhanced captions", [
        "Descriptive & neutral",
        "Warm & friendly",
        "Professional & formal",
        "Creative & poetic",
        "Humorous & playful",
        "Dramatic & cinematic",
    ])

    st.markdown("---")
    st.markdown("### ⚙️ BLIP Settings")
    num_captions = st.slider("Number of BLIP captions", 1, 4, 3)

    st.markdown("---")
    st.markdown("### 📂 Supported Formats")
    st.markdown("`JPG` `PNG` `WEBP` `BMP` `TIFF` `GIF`")

    st.markdown("---")
    st.markdown("### 🔒 Privacy")
    st.markdown("BLIP runs **100% locally**.\nOnly with Gemini key: image is sent to Google.")

# ── Main UI ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🖼️ AI Image Caption Generator</h1>
  <p>Upload any image → Get captions, alt text, SEO titles, tags, mood & social media posts instantly</p>
</div>
""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📂 Upload an image",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"],
    help="Works best with clear, well-lit images"
)

if uploaded:
    file_bytes = uploaded.read()
    image      = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    info       = image_info(image, file_bytes)

    col_img, col_info = st.columns([1, 1])

    with col_img:
        st.image(image, caption=uploaded.name, use_column_width=True)

    with col_info:
        st.markdown("### 📊 Image Info")
        i1, i2 = st.columns(2)
        stats = [
            (info["size"],   "Dimensions"),
            (info["kb"],     "File Size"),
            (info["format"], "Format"),
            (info["mode"],   "Color Mode"),
        ]
        for i, (val, label) in enumerate(stats):
            with (i1 if i % 2 == 0 else i2):
                st.markdown(
                    f'<div class="stat-card"><div class="stat-val" style="font-size:16px;">{val}</div>'
                    f'<div class="stat-label">{label}</div></div><br>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        generate_clicked = st.button("🚀 Generate Captions")

    if generate_clicked:
        # ── BLIP captions ──────────────────────────────────────────────────────
        with st.spinner("🧠 Running BLIP vision model..."):
            try:
                processor, blip_model = load_blip()
                blip_captions = generate_blip_captions(image, processor, blip_model)
                blip_captions = blip_captions[:num_captions]
            except Exception as e:
                st.error(f"BLIP error: {e}")
                blip_captions = ["Could not generate BLIP caption."]

        best_blip = blip_captions[0] if blip_captions else ""

        st.markdown("---")

        # ── Tabs ───────────────────────────────────────────────────────────────
        if api_key:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🖼️ Captions", "🏷️ Tags & Info", "📱 Social Media", "♿ Accessibility", "📋 All Export"
            ])
        else:
            tab1, tab2 = st.tabs(["🖼️ BLIP Captions", "📋 Export"])

        # ── Gemini analysis ────────────────────────────────────────────────────
        gemini_data = None
        if api_key:
            with st.spinner("✨ Running Gemini vision analysis..."):
                try:
                    gemini_data = gemini_analyse(image, best_blip, api_key, tone)
                except Exception as e:
                    st.warning(f"Gemini failed: {e} — showing BLIP results only.")

        # Tab 1 — Captions
        with tab1:
            st.markdown("### 🖼️ Generated Captions")

            if gemini_data:
                # Enhanced caption
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="result-label" style="color:#a78bfa;">✨ Enhanced Caption ({tone})</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="caption-text">"{gemini_data.get("enhanced_caption","")}"</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Short caption
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="result-label" style="color:#06b6d4;">⚡ Short Caption</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="caption-text">"{gemini_data.get("short_caption","")}"</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # BLIP captions
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="result-label" style="color:#4ade80;">🤖 BLIP Captions (Local Model)</div>', unsafe_allow_html=True)
            for i, cap in enumerate(blip_captions, 1):
                st.markdown(f'<div class="caption-text" style="margin-bottom:8px;">{i}. "{cap}"</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Mood & scene
            if gemini_data:
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-val" style="font-size:20px;">{gemini_data.get("mood","—")}</div>'
                        f'<div class="stat-label">Mood</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-val" style="font-size:16px;">{gemini_data.get("scene_type","—")}</div>'
                        f'<div class="stat-label">Scene Type</div></div>', unsafe_allow_html=True)
                with m3:
                    colors = gemini_data.get("colors", [])
                    color_text = " · ".join(colors[:3]) if colors else "—"
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-val" style="font-size:14px;">{color_text}</div>'
                        f'<div class="stat-label">Dominant Colors</div></div>', unsafe_allow_html=True)

        # Tab 2 — Tags (with Gemini) or Export (without)
        if api_key and gemini_data:
            with tab2:
                st.markdown("### 🏷️ Tags & Keywords")
                tags = gemini_data.get("tags", [])
                chips = "".join([f'<span class="tag-chip">#{t}</span>' for t in tags])
                st.markdown(chips, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🔍 SEO Title")
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="caption-text">{gemini_data.get("seo_title","")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Copy-ready tags
                st.text_area("Copy all hashtags:", value=" ".join([f"#{t}" for t in tags]), height=80)

            with tab3:
                st.markdown("### 📱 Social Media Captions")

                platforms = [
                    ("📸 Instagram",  "instagram_post",  "#E1306C"),
                    ("🐦 Twitter/X",  "twitter_post",    "#1DA1F2"),
                    ("💼 LinkedIn",   "linkedin_post",   "#0A66C2"),
                ]
                for platform_label, key, color in platforms:
                    content = gemini_data.get(key, "")
                    if content:
                        st.markdown(f'<div class="platform-label" style="color:{color};">{platform_label}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="social-box">{content}</div>', unsafe_allow_html=True)
                        char_count = len(content)
                        st.caption(f"{char_count} characters")
                        st.markdown("<br>", unsafe_allow_html=True)

            with tab4:
                st.markdown("### ♿ Accessibility Alt Text")
                st.markdown("*For use in HTML `alt` attributes, screen readers, and CMS image fields:*")
                alt_text = gemini_data.get("alt_text", "")
                st.markdown(f'<div class="result-card"><div class="caption-text">{alt_text}</div></div>', unsafe_allow_html=True)
                st.text_area("Copy alt text:", value=alt_text, height=100)

                st.markdown("### 📝 HTML Snippet")
                html_snippet = f'<img src="{uploaded.name}" alt="{alt_text}" />'
                st.code(html_snippet, language="html")

            with tab5:
                st.markdown("### 📋 Export All Results")
                export = {
                    "filename":        uploaded.name,
                    "image_info":      info,
                    "blip_captions":   blip_captions,
                }
                if gemini_data:
                    export.update(gemini_data)

                st.download_button(
                    "⬇️ Download as JSON",
                    data=json.dumps(export, indent=2),
                    file_name=f"{Path(uploaded.name).stem}_captions.json",
                    mime="application/json",
                    use_container_width=True,
                )

                # Plain text summary
                summary_lines = [
                    f"IMAGE: {uploaded.name}",
                    f"SIZE: {info['size']} | FORMAT: {info['format']} | {info['kb']}",
                    "",
                    "── CAPTIONS ──",
                ]
                for i, cap in enumerate(blip_captions, 1):
                    summary_lines.append(f"BLIP {i}: {cap}")
                if gemini_data:
                    summary_lines += [
                        f"ENHANCED: {gemini_data.get('enhanced_caption','')}",
                        f"SHORT: {gemini_data.get('short_caption','')}",
                        f"MOOD: {gemini_data.get('mood','')}",
                        f"SCENE: {gemini_data.get('scene_type','')}",
                        "",
                        "── TAGS ──",
                        " ".join([f"#{t}" for t in gemini_data.get("tags",[])]),
                        "",
                        "── ALT TEXT ──",
                        gemini_data.get("alt_text",""),
                        "",
                        "── SOCIAL ──",
                        f"Instagram: {gemini_data.get('instagram_post','')}",
                        f"Twitter: {gemini_data.get('twitter_post','')}",
                        f"LinkedIn: {gemini_data.get('linkedin_post','')}",
                    ]
                st.download_button(
                    "⬇️ Download as TXT",
                    data="\n".join(summary_lines),
                    file_name=f"{Path(uploaded.name).stem}_captions.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
        else:
            # Without Gemini — simple export tab
            with tab2:
                st.markdown("### 📋 Export")
                st.download_button(
                    "⬇️ Download Captions (.txt)",
                    data="\n".join([f"{i+1}. {c}" for i, c in enumerate(blip_captions)]),
                    file_name=f"{Path(uploaded.name).stem}_captions.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
                st.info("💡 Add a free Gemini API key in the sidebar to unlock social media posts, SEO titles, tags, alt text and more!")

else:
    # Empty state
    st.markdown("""
<div style="text-align:center;padding:60px 20px;">
  <div style="font-size:72px;margin-bottom:16px;">🖼️</div>
  <h3 style="color:#475569;">Upload an image to generate captions</h3>
  <p style="color:#334155;font-size:14px;max-width:540px;margin:0 auto 28px;">
    Works with photos, illustrations, screenshots, product images — any JPG, PNG or WEBP.
    BLIP runs locally (no key needed). Add a free Gemini key for social media posts, SEO titles & accessibility alt text.
  </p>
</div>
""", unsafe_allow_html=True)

    uc = ["📸 Photography", "🛍️ E-commerce products", "📰 News images",
          "🎨 Artwork & illustrations", "🏗️ Architecture", "🍔 Food photography"]
    cols = st.columns(3)
    for i, u in enumerate(uc):
        with cols[i % 3]:
            st.markdown(
                f'<div style="background:#0c0d16;border:1px solid #1a1a2e;border-radius:8px;'
                f'padding:10px 14px;text-align:center;font-size:13px;color:#64748b;margin:4px 0;">'
                f'{u}</div>', unsafe_allow_html=True)
