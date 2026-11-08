# 👥 People Counting & Crowd Threshold Alert

Laptop webcam (বা video file) থেকে **YOLO11n** দিয়ে মানুষ detect, **ByteTrack** দিয়ে tracking, একটি **ROI** এর ভেতরের মানুষ গোনা, এবং count **threshold ছাড়িয়ে টানা ২ সেকেন্ড** থাকলে **CROWD ALERT** দেখানো।

## ফিচার
- YOLO11n (শুধু `person` class) + ByteTrack (প্রতিজন মানুষের স্থায়ী ID)
- Polygon ROI — রান করার সময়ই মাউস দিয়ে আঁকা যায়, `roi.json` এ save হয়
- ROI এর ভেতরে এই মুহূর্তের count + মোট unique ID
- Alert: count > threshold **টানা ২ সেকেন্ড** হলে ALERT (সময়-ভিত্তিক, FPS এর উপর নির্ভর করে না)
- ২ সেকেন্ড পূরণের আগে orange progress bar (WARNING), ALERT এ লাল blinking border + banner
- Alert শেষ হওয়ার সময় ছোট delay (flicker ঠেকাতে)
- Live threshold বদল (`+`/`-`), screenshot (`s`)

## ফোল্ডার structure
```
crowd_counter/
├── main.py              # entry point (main loop)
├── config.yaml          # সব সেটিং এক জায়গায়
├── requirements.txt
├── setup_ubuntu.sh      # Ubuntu এ এক কমান্ডে setup
├── roi.json             # (auto) আঁকা ROI — প্রথমবার রানের পর তৈরি হয়
├── trackers/
│   └── bytetrack.yaml   # ByteTrack tuning
├── src/
│   ├── config.py        # config load + default
│   ├── detector.py      # YOLO11n + ByteTrack wrapper
│   ├── roi.py           # ROI polygon, point-in-polygon, মাউসে আঁকা
│   ├── alert.py         # threshold + ২ সেকেন্ড state machine
│   └── visualizer.py    # box, ROI, HUD, alert banner
└── output/              # screenshot এখানে
```

## Ubuntu setup
```bash
cd crowd_counter
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```
ম্যানুয়ালি করতে চাইলে:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip libgl1 libglib2.0-0 v4l-utils
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
> GPU না থাকলে ডাউনলোড ছোট রাখতে `pip install -r requirements.txt` এর **আগে**:
> `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`

## রান করার নিয়ম
```bash
source .venv/bin/activate
python main.py                          # webcam, config.yaml এর সেটিং
python main.py --source 1               # অন্য camera
python main.py --source test.mp4        # video file
python main.py --threshold 5 --duration 2
python main.py --conf 0.45
python main.py --reset-roi              # সেভ করা ROI মুছে default এ ফেরা
```
প্রথমবার `yolo11n.pt` নিজে download হবে (ইন্টারনেট লাগবে)। প্রজেক্ট ফোল্ডার থেকেই চালান।

### Keyboard shortcut
| Key | কাজ |
|-----|-----|
| `q` / `Esc` | বন্ধ |
| `r` | নতুন ROI আঁকা |
| `+` / `-` | threshold বাড়ানো/কমানো (live) |
| `s` | screenshot (`output/`) |

## Threshold সেট করার উপায়
এটা "ROI তে এর **বেশি** মানুষ হলে ভিড়" — অর্থাৎ `count > threshold`।

1. **স্থায়ীভাবে:** `config.yaml` এ `threshold: 3` বদলান।
2. **এক রানের জন্য:** `python main.py --threshold 5`
3. **চলন্ত অবস্থায়:** `+` / `-` চাপুন (config ফাইল বদলায় না)।

সময় বদলাতে: `alert_duration: 2.0` (বা `--duration 3`)।
Alert বন্ধ হওয়ার delay: `clear_delay: 0.5`।

**Test এর টিপস:** webcam এ একা থাকলে `--threshold 0` দিন — আপনি ROI তে ঢুকে ২ সেকেন্ড থাকলেই ALERT আসবে।

## ROI কিভাবে বদলাবে
**পদ্ধতি ১ — মাউস দিয়ে (সহজ):** রান করার সময় `r` চাপুন। frame freeze হবে:
- **Left click** = point যোগ, **Right click** = শেষ point undo, `c` = সব মুছো
- **Enter** = নিশ্চিত (কমপক্ষে ৩ point), **Esc** = বাতিল

ROI সাথে সাথে `roi.json` এ save হয়, পরের রানেও থাকে।

**পদ্ধতি ২ — হাতে:** `config.yaml` এর `default_roi` (বা `roi.json` এর `points`) এডিট করুন। মান `0.0–1.0` normalized `[x, y]`, তাই resolution বদলালেও ঠিক থাকে।
```yaml
default_roi:
  - [0.10, 0.10]   # উপরে-বামে
  - [0.90, 0.10]   # উপরে-ডানে
  - [0.90, 0.90]   # নিচে-ডানে
  - [0.10, 0.90]   # নিচে-বামে
```
> `roi.json` থাকলে সেটাই অগ্রাধিকার পায়। default এ ফিরতে `--reset-roi` বা ফাইলটি মুছুন।

**কোন বিন্দু ROI এ আছে সেটা:** `anchor: center` (box এর মাঝখান, webcam এর জন্য ভালো) অথবা `anchor: bottom` (পায়ের কাছে, CCTV এর জন্য ভালো)।

## Performance টিপস
- CPU ধীর হলে: `imgsz: 480` বা `416`, `frame_width/height: 640/480`
- ভুল detection বেশি হলে `conf` বাড়ান (0.45–0.5); মানুষ miss হলে কমান (0.25–0.3)
- ID ঘনঘন বদলালে `trackers/bytetrack.yaml` এ `track_buffer` বাড়ান (যেমন 60)
- GPU থাকলে `device: 0`

## সমস্যা সমাধান
| সমস্যা | সমাধান |
|--------|--------|
| `Video source খোলা যায়নি` | `v4l2-ctl --list-devices` চালিয়ে index দেখুন; `--source 1` চেষ্টা করুন; অন্য app (Zoom/Cheese) বন্ধ করুন |
| `Permission denied /dev/video0` | `sudo usermod -aG video $USER` তারপর logout/login |
| window খুলছে না (Wayland/SSH) | local desktop session এ চালান; SSH এ `ssh -X` লাগবে |
| `libGL.so.1` error | `sudo apt install -y libgl1 libglib2.0-0` |
| `lap` সংক্রান্ত error | `pip install lapx` |

## Pipeline
```
Webcam → YOLO11n (person) → ByteTrack (ID) → ROI check → count
      → count > threshold ? ২ সেকেন্ড টানা → CROWD ALERT
```
