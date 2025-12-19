# Home Appliance Control for Visually & Verbally Impaired

Real-time hand gesture recognition to control home appliances using MediaPipe + Raspberry Pi GPIO.

![Benchmark](https://github.com/Msundara19/Home_appliance_control/actions/workflows/benchmark.yml/badge.svg)

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Gesture Recognition Accuracy | 100% |
| Average Latency | 33ms |
| P95 Latency | 48ms |
| P99 Latency | 49ms |

Run `python benchmark.py` to reproduce results locally.

## Features
- Real-time hand/palm landmark detection using MediaPipe + OpenCV
- Simple gesture → action mapping (1-5 fingers)
- HTTP client on Raspberry Pi with `/on` and `/off` endpoints
- Simulation mode for testing without hardware

## Architecture
```
+------------------+          HTTP          +-------------------+
|  Hand Gesture    |  ──────────────►      |  Raspberry Pi     |
|  Server (PC)     |                        |  GPIO Client      |
|  OpenCV+MediaPipe|  ◄──────────────       |  Flask / GPIO 18  |
+------------------+    responses           +-------------------+
```

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Create config
cp src/common/config.example.yaml src/common/config.yaml

# Run benchmark
python benchmark.py

# Run gesture server (needs webcam)
python -m src.server.hand_gesture_server
```

## Gesture Mapping
- **1 finger** → OFF
- **2 fingers** → ON
- **3 fingers** → VOL+
- **4 fingers** → VOL-
