# Home Appliance Control for Visually & Verbally Impaired (Deep Learning + IoT)

Recreation and modernization of the original 2023 project: camera-based hand gesture recognition to control home appliances over a local network (Raspberry Pi GPIO).

## Highlights
- Real‑time hand/palm landmark detection using MediaPipe + OpenCV
- Simple gesture → action mapping (0–5 fingers)
- HTTP client on Raspberry Pi exposes `/on` and `/off` endpoints (Flask)
- Works in **Simulation Mode** on any laptop (no GPIO needed)
- Configurable endpoints & camera index via `config.yaml`
- MIT-licensed & ready for GitHub

> This repository is a clean-room re-implementation guided by the attached report and code snippets, with clearer structure, docs, and a few safety checks.

## Architecture
```
+-----------------+           HTTP            +--------------------+
|  Hand Gesture   |  ───────────────►        |  Raspberry Pi      |
|  Server (PC)    |                          |  GPIO Client       |
|  OpenCV+MP      |  ◄───────────────         |  Flask / GPIO 18   |
+-----------------+    responses              +--------------------+
        |                                             |
     Webcam                                        Relay/LED
```

### Gesture mapping (default)
- **2 fingers** → `ON` (POST/GET to `/on`)
- **1 finger** → `OFF` (POST/GET to `/off`)
- **3 / 4 fingers** → example volume actions (endpoints present for extension)
- **0 / 5 fingers** → no-op (overlay only)

You can adjust this in `src/server/hand_gesture_server.py` or extend endpoints in the client.

## Quickstart

### 1) Clone & install
```bash
git clone https://github.com/<your-user>/home-appliance-gesture-iot.git
cd home-appliance-gesture-iot
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure
Copy the example config:
```bash
cp src/common/config.example.yaml src/common/config.yaml
```
Edit:
- `camera_index`: usually `0` or `1`
- `raspi_base_url`: e.g. `http://192.168.0.108:8081`
- `simulation_mode`: `true` if you don’t have a Pi connected

### 3) Run the Raspberry Pi client (on the Pi)
```bash
source .venv/bin/activate
python src/client/raspi_gpio_client.py
```
This exposes:
- `POST /on`  → sets GPIO 18 HIGH
- `POST /off` → sets GPIO 18 LOW

### 4) Run the gesture server (on your laptop/PC)
```bash
python src/server/hand_gesture_server.py
```
Press `q` to quit.

## Simulation mode
Set `simulation_mode: true` in `config.yaml` to run without a Pi. The server will log the intended HTTP calls instead of sending them.

## Repo layout
```
home-appliance-gesture-iot/
├── src/
│   ├── client/raspi_gpio_client.py      # Flask + (optional) RPi.GPIO
│   ├── server/hand_gesture_server.py    # OpenCV + MediaPipe
│   └── common/
│       ├── config.example.yaml
│       └── helpers.py
├── scripts/
│   ├── run_client.sh
│   └── run_server.sh
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md
```

## Credits
- Original concept and report guidance by the author(s) of the uploaded document.
- MediaPipe Hands: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
- OpenCV

## Safety notes
- Always isolate mains voltage. For lamps, drive a relay rated for your load.
- Use a proper transistor/SSR/relay board between GPIO and the appliance.
- Verify your local laws and electrical codes before connecting to household mains.

## Troubleshooting
- **Black window / no camera**: try changing `camera_index` to `0` or `1`.
- **Landmarks not detected**: ensure good lighting; keep the hand 0.3–1.0m from camera.
- **HTTP errors**: check that the Pi IP is reachable; try `curl http://<pi-ip>:8081/on -X POST`.