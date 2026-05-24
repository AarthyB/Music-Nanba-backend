<div align="center">

# 🎵 Music Nanba

**An emotion-aware Android music recommender — your mood builds the playlist**

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)
[![Android](https://img.shields.io/badge/Android-3DDC84?style=flat&logo=android&logoColor=white)](https://developer.android.com)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Spotify](https://img.shields.io/badge/Spotify_API-1DB954?style=flat&logo=spotify&logoColor=white)](https://developer.spotify.com)
[![Render](https://img.shields.io/badge/Backend_on-Render-46E3B7?style=flat&logo=render&logoColor=white)](https://render.com)

</div>

---

## 📖 About

Current music platforms are great at analysing your *listening history* — but they ignore how you feel *right now*. Music Nanba fixes that.

Type a few words or a full journal entry about your mood, and GPT-4o-mini analyses your emotional state to instantly generate a playlist that matches or gently elevates it. No more manually hunting for the right vibe.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Emotion Detection** | GPT-4o-mini analyses free-text input — from a single word to a full journal entry |
| 🎶 **Smart Playlist Curation** | Generates mood-aware song queues via Spotify API & YouTube Music API |
| 📓 **Mood Journaling** | Log and revisit mood entries as a personal wellness tool |
| 📊 **Mood Analytics Dashboard** | Pie chart, weekly trends, most frequent mood, and average mood score |
| 🔐 **Auth** | Secure account creation and login via Firebase Authentication |
| ⚙️ **Settings** | Language and music platform preferences |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│       Android App (Java)            │
│  Welcome → Mood Input → Playlist    │
│  Dashboard · Journal · Settings     │
└──────────────┬──────────────────────┘
               │ HTTP REST
┌──────────────▼──────────────────────┐
│       Python / Flask Backend        │  ← hosted on Render
│                                     │
│  ┌─────────────────────────────┐    │
│  │  GPT-4o-mini (OpenAI API)   │    │
│  │  Emotion Detection Engine   │    │
│  └──────────┬──────────────────┘    │
│             │                       │
│  ┌──────────▼──────────────────┐    │
│  │  Spotify API + YT Music API │    │
│  │  Song Fetching & Playlists  │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
         │
┌────────▼────────┐
│    Firebase     │
│  (Auth / JWT)   │
└─────────────────┘
```

---

## 📱 Try It — Download the APK

The backend is live and ready. Just install the app and go.

**[⬇️ Download APK](https://github.com/AarthyB/Music-Nanba-backend/releases)**

> Enable "Install from unknown sources" in your Android settings before installing.

---

## 🛠️ Tech Stack

**Mobile:** Android (Java) · Android Studio  
**Backend:** Python · Flask  
**AI:** OpenAI GPT-4o-mini  
**Music APIs:** Spotify API · YouTube Music API (unofficial)  
**Auth:** Firebase Authentication  
**Deployment:** Render (backend)

---

## 📁 Repository Structure

```
MusicNanba/
├── app.py                  # Flask server — main entry point
├── requirements.txt
├── render.yaml             # Render deployment config
└── ...                     # Backend modules and API handlers
```

> The Android project source is not included in this repo. The compiled APK is available in [Releases](https://github.com/AarthyB/MusicNanba-backend/releases).

---

## 🔮 Future Work

- **On-device emotion detection** via TensorFlow Lite (vocal tone + facial expression analysis) for enhanced privacy and offline support
- Replace unofficial YouTube Music API with a stable alternative
- Expand multi-modal mood input (voice, camera)

---

<div align="center">
  <i>Because your mood deserves a better soundtrack 🎧</i>
</div>
