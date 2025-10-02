# 🌧️🎶 Zelda Storm Autoplay  

A fun Python script that plays **Zelda lofi** automatically when it rains in Honolulu — or anytime you force it 🌿✨.  

---

## ⚡ Features
- ⛅ Real-time weather check (Honolulu by default)  
- 🎧 Plays your chosen MP3 when rain is detected  
- 🌀 `--audio` flag lets you use any local file  
- 💾 Optional export to WAV  

---

## 🚀 Setup

1. **Clone this repo**
   ```bash
   git clone https://github.com/puffpuff-pass/zelda-storm-autoplay.git
   cd zelda-storm-autoplay
Install requirements

bash
Copy code
pip install -r requirements.txt
Add your track

Place your MP3 file in the assets/ folder

Name it exactly: song.mp3

▶️ Run
Default mode (checks Honolulu weather):

bash
Copy code
python storm_lofi_runner.py
Force play regardless of weather:

bash
Copy code
python storm_lofi_runner.py --audio assets/song.mp3 --out exports/storm.wav
This will:

🎵 Play assets/song.mp3

💾 Save a copy to exports/storm.wav

✨ Notes
.gitignore hides assets/*.mp3 and exports/ so your local media never leaks to GitHub.

Works with any MP3/WAV you drop into assets/.

Change the city in the script if you want weather-triggered playback for another location 🌍.

🛠️ Badges



Enjoy your rainy lofi kinda day coding! 🌧🎶🌿
