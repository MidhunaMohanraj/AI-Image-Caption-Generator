# 🖼️ AI Image Caption Generator

<div align="center">

![Banner](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=14,18,24&height=200&section=header&text=AI%20Image%20Caption%20Generator&fontSize=40&fontColor=fff&animation=twinkling&fontAlignY=35&desc=BLIP%20%2B%20Gemini%20Vision%20%7C%20Captions%2C%20Tags%2C%20Alt%20Text%20%26%20Social%20Posts%20in%20Seconds&descAlignY=55&descSize=14)

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/BLIP-Salesforce-00A3E0?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Gemini%20Vision-Optional%20Free-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Multimodal%20AI-Vision%20%2B%20Language-a855f7?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge"/>
</p>

<p>
  <b>Upload any image → Instantly get captions, accessibility alt text, SEO titles, keyword tags, mood detection, and ready-to-post social media captions for Instagram, Twitter & LinkedIn.</b><br/>
  Powered by Salesforce BLIP (runs locally) + optional Google Gemini Vision (free tier).
</p>

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [How It Works](#-how-it-works) • [Use Cases](#-use-cases) • [FAQ](#-faq)

</div>

---

## 🌟 Why This Project?

Writing image captions manually is slow, inconsistent, and easy to forget. This tool automates everything:

- 🛍️ **E-commerce** — auto-generate product alt text for SEO & accessibility
- 📸 **Photographers** — caption entire shoots in seconds
- 📱 **Social media managers** — get platform-specific posts instantly
- ♿ **Accessibility** — never miss an alt text attribute again
- 🔍 **SEO** — AI-generated image titles and keyword tags
- 📰 **Content creators** — caption news images, blog photos, and more

---

## ✨ Features

| Feature | Requires API Key? | Description |
|---|---|---|
| 🤖 **BLIP Captions** | ❌ No — 100% local | Multiple caption variants from Salesforce BLIP |
| ✨ **Enhanced Caption** | ✅ Free Gemini key | Vivid, tone-adjusted caption (6 tone options) |
| ⚡ **Short Caption** | ✅ Free Gemini key | Ultra-punchy caption under 10 words |
| 🏷️ **12 Keyword Tags** | ✅ Free Gemini key | Hashtag-ready keywords for discoverability |
| 😊 **Mood Detection** | ✅ Free Gemini key | Single-word emotional tone of the image |
| 🎨 **Color Analysis** | ✅ Free Gemini key | Dominant colors described in plain English |
| 🏗️ **Scene Classification** | ✅ Free Gemini key | Portrait / landscape / product / food / etc. |
| 📸 **Instagram Caption** | ✅ Free Gemini key | Full post with emojis and 8 hashtags |
| 🐦 **Twitter/X Caption** | ✅ Free Gemini key | Under 280 chars with 3 hashtags |
| 💼 **LinkedIn Caption** | ✅ Free Gemini key | Professional 2-3 sentence post |
| ♿ **Accessibility Alt Text** | ✅ Free Gemini key | Full WCAG-compliant alt text + HTML snippet |
| 🔍 **SEO Image Title** | ✅ Free Gemini key | Keyword-rich title for web use |
| 📥 **Export JSON / TXT** | ❌ No | Download all results in one file |

---

## 🖥️ Demo

```
╔══════════════════════════════════════════════════════════════════╗
║  🖼️ AI Image Caption Generator                                   ║
║  sunset_beach.jpg  │  2.4 MB  │  3840 × 2160 px                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🖼️ Captions  🏷️ Tags  📱 Social  ♿ Accessibility  📋 Export   ║
║  ──────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  ✨ Enhanced Caption (Cinematic tone)                            ║
║  "Golden light drapes the horizon as waves dissolve into        ║
║   the shore, painting a moment of perfect solitude."            ║
║                                                                  ║
║  ⚡ Short Caption                                                ║
║  "Where the sky meets the sea."                                  ║
║                                                                  ║
║  🤖 BLIP Captions                                                ║
║  1. "a sunset over the ocean with waves"                        ║
║  2. "a beautiful sunset at the beach"                           ║
║                                                                  ║
║  😊 Mood: Peaceful  🏗️ Scene: Landscape  🎨 Gold · Blue · Pink  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 📦 Installation

### Prerequisites
- Python 3.9+ → [Download](https://www.python.org/downloads/)
- Free Gemini API key *(optional)* → [Get here](https://aistudio.google.com)

### Step 1 — Clone
```bash
git clone https://github.com/YOUR_USERNAME/ai-image-caption-generator.git
cd ai-image-caption-generator
```

### Step 2 — Virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **First run:** BLIP model weights (~900MB) are downloaded automatically from HuggingFace. Internet required once — then runs offline.

### Step 4 — Run
```bash
streamlit run app.py
```

Opens at **http://localhost:8501** 🎉

---

## 🧠 How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│  User uploads image (JPG, PNG, WEBP, BMP, TIFF, GIF)            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
             ┌─────────────┴──────────────┐
             ▼                            ▼
┌─────────────────────┐      ┌────────────────────────────────────┐
│  BLIP (Local)       │      │  Gemini Vision (Optional / Free)   │
│                     │      │                                    │
│  Salesforce BLIP    │      │  Image + BLIP caption sent as      │
│  image-captioning   │      │  multimodal prompt to Gemini       │
│  base model         │      │  1.5 Flash                         │
│                     │      │                                    │
│  • Unconditional    │      │  Returns JSON with:                │
│    caption          │      │  • Enhanced caption (toned)        │
│  • 3 conditional    │      │  • Short caption                   │
│    prompt variants  │      │  • 12 keyword tags                 │
│                     │      │  • Mood + scene + colors           │
│  Runs on CPU        │      │  • Instagram/Twitter/LinkedIn      │
│  No API needed      │      │  • Alt text + SEO title            │
└─────────────────────┘      └────────────────────────────────────┘
             │                            │
             └─────────────┬──────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Streamlit UI renders results across 5 tabs                      │
│  + JSON and TXT export download buttons                          │
└──────────────────────────────────────────────────────────────────┘
```

### Why BLIP + Gemini?

| Model | Runs | Cost | Best For |
|---|---|---|---|
| BLIP (base) | Locally | Free forever | Quick factual captions, offline use |
| Gemini 1.5 Flash | Cloud | Free tier | Rich descriptions, social posts, SEO |

Using both gives you the best of both worlds — always-available local captions plus rich AI-enhanced content when a key is available.

---

## 🎨 Caption Tones

| Tone | Example Output |
|---|---|
| Descriptive & neutral | "A golden sunset over calm ocean waters near a sandy beach." |
| Warm & friendly | "Nothing beats ending the day watching the sun melt into the sea! 🌅" |
| Professional & formal | "A high-resolution coastal landscape captured during the golden hour." |
| Creative & poetic | "Where daylight surrenders its reign to the patient, waiting night." |
| Humorous & playful | "The sun is leaving — and honestly, same." |
| Dramatic & cinematic | "As the dying sun scorched the horizon, the world held its breath." |

---

## 💡 Use Cases

| Industry | How to Use |
|---|---|
| 🛍️ **E-commerce** | Auto-generate alt text and product titles for entire image libraries |
| 📰 **News / Media** | Caption breaking news photos instantly |
| 📱 **Social Media** | Get platform-specific posts ready in one click |
| ♿ **Accessibility** | Bulk-generate WCAG-compliant alt text |
| 🔍 **SEO** | Keyword-rich image titles improve Google Image Search ranking |
| 🎓 **Education** | Describe images for visually impaired students |
| 🤖 **ML Datasets** | Generate caption annotations for training data |

---

## 📁 Project Structure

```
ai-image-caption-generator/
│
├── app.py              # 🧠 Main Streamlit app — all logic
├── requirements.txt    # 📦 5 dependencies
├── .gitignore          # 🚫 Excludes model cache, uploaded images
├── LICENSE             # 📄 MIT License
└── README.md           # 📖 You are here
```

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| [Streamlit](https://streamlit.io) | 1.35 | Web UI |
| [Salesforce BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base) | via HuggingFace | Local image captioning |
| [Transformers](https://huggingface.co/docs/transformers) | 4.41 | BLIP model loading & inference |
| [PyTorch](https://pytorch.org) | 2.3 | Deep learning backend |
| [Pillow](https://pillow.readthedocs.io) | 10.3 | Image loading & preprocessing |
| [Google Gemini](https://aistudio.google.com) | 1.5 Flash | Enhanced multimodal analysis |

---

## 🤔 FAQ

**Q: Does it work without the Gemini API key?**
> Yes! BLIP runs fully locally and generates multiple caption variants with zero setup beyond `pip install`.

**Q: What is BLIP?**
> BLIP (Bootstrapping Language-Image Pre-training) is Salesforce's open-source vision-language model, trained on 129 million image-text pairs. It's one of the best free local captioning models available.

**Q: How good is the accuracy?**
> BLIP is excellent for factual descriptions of clear images. Gemini adds creativity, context, and structured outputs. Complex or abstract images may get generic captions.

**Q: Can I batch-process multiple images?**
> Not in the current version — it processes one image at a time. Batch mode is on the roadmap!

**Q: Is my image sent anywhere with just BLIP?**
> No. BLIP runs 100% locally on your CPU. Only if you provide a Gemini key and click Generate does the image get sent to Google's API.

**Q: Can I use a GPU for faster processing?**
> Yes! If you have CUDA installed, PyTorch auto-detects it and BLIP runs significantly faster.

---

## 🗺️ Roadmap

- [ ] 📦 Batch processing — caption a folder of images at once
- [ ] 🌍 Multi-language caption output
- [ ] 🔄 Compare multiple models side-by-side (BLIP, CLIP, LLaVA)
- [ ] 📤 CSV export for bulk e-commerce workflows
- [ ] 🖥️ Drag-and-drop multiple image upload
- [ ] 🤖 LLaVA local model option for fully offline rich captions

---

## 🤝 Contributing

1. Fork this repo
2. Create a branch: `git checkout -b feature/your-idea`
3. Commit: `git commit -m 'feat: your feature'`
4. Push & open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [Salesforce BLIP](https://github.com/salesforce/BLIP) — incredible open-source vision-language model
- [HuggingFace Transformers](https://huggingface.co/transformers) — for making BLIP accessible in 3 lines of code
- [Google Gemini](https://aistudio.google.com) — for the generous free multimodal API tier

---

<div align="center">

**⭐ Found this useful? Star the repo — it helps a lot!**

Made with ❤️ and Python

![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=14,18,24&height=100&section=footer)

</div>
