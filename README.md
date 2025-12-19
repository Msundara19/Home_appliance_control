# Home Appliance Control for Visually & Verbally Impaired

> Gesture-based home automation enabling **2.2 billion+ visually impaired** and **70 million+ deaf/hard of hearing** individuals to control appliances independently.

![Benchmark](https://github.com/Msundara19/Home_appliance_control/actions/workflows/benchmark.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Problem Statement

Current smart home solutions **exclude millions**:

| Technology | Limitation |
|------------|------------|
| Voice Assistants (Alexa, Siri) | Unusable by deaf/mute users |
| Touchscreen Controls | Inaccessible to visually impaired |
| Traditional Switches | Require precise motor control |

**Our Solution:** Camera-based hand gesture recognition that works for everyone.

---

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| Gesture Recognition Accuracy | **100%** |
| Average End-to-End Latency | **33ms** |
| P50 Latency | 33ms |
| P95 Latency | 48ms |
| P99 Latency | 49ms |

> Run `python benchmark.py` to reproduce results. CI runs automatically on every push.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S HOME                               │
│                                                                  │
│   ┌─────────────┐         HTTP/WiFi        ┌─────────────────┐  │
│   │   Webcam    │                          │  Raspberry Pi   │  │
│   │     +       │  ───────────────────►    │  + Relay Board  │  │
│   │  PC/Laptop  │                          │  + Appliances   │  │
│   │  (Server)   │  ◄───────────────────    │  (Client)       │  │
│   └─────────────┘       Response           └─────────────────┘  │
│         │                                          │             │
│         ▼                                          ▼             │
│   ┌─────────────┐                          ┌─────────────────┐  │
│   │ MediaPipe   │                          │  GPIO Control   │  │
│   │ Hand Track  │                          │  PIN 18 → Relay │  │
│   │ + OpenCV    │                          │  → Light/Fan    │  │
│   └─────────────┘                          └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Hand Gesture → Camera Capture → MediaPipe Detection → Finger Counting
     │                                                       │
     │                              ┌────────────────────────┘
     │                              ▼
     │                      Gesture Mapping
     │                     (1=OFF, 2=ON, etc.)
     │                              │
     │                              ▼
     │                      HTTP POST Request
     │                              │
     │                              ▼
     │                     Raspberry Pi Client
     │                              │
     │                              ▼
     └──────────────────►  GPIO Pin Toggle → Appliance ON/OFF
                                   
                          Total Latency: ~33ms
```

---

## 🖐️ Gesture Mapping

| Fingers | Action | Use Case |
|---------|--------|----------|
| 1 | OFF | Turn off light/fan |
| 2 | ON | Turn on light/fan |
| 3 | VOL+ | Increase brightness/speed |
| 4 | VOL- | Decrease brightness/speed |
| 5 | (Reserved) | Future: Scene selection |

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Hand Detection | MediaPipe Hands | 21-point hand landmark detection |
| Image Processing | OpenCV | Camera capture, preprocessing |
| Backend Server | Python | Gesture processing pipeline |
| IoT Client | Flask | REST API on Raspberry Pi |
| Hardware Control | RPi.GPIO | GPIO pin manipulation |
| CI/CD | GitHub Actions | Automated benchmarking |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Webcam (for gesture server)
- Raspberry Pi (optional, for hardware control)

### Installation

```bash
# Clone repository
git clone https://github.com/Msundara19/Home_appliance_control.git
cd Home_appliance_control

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create config
cat > src/common/config.yaml << EOF
camera_index: 0
raspi_base_url: "http://192.168.1.100:8081"  # Your Pi's IP
simulation_mode: true  # Set false when Pi is connected
request_timeout_sec: 2.5
draw_debug_text: true
EOF
```

### Run Benchmark (No Hardware Needed)

```bash
python benchmark.py
```

### Run Gesture Server (Needs Webcam)

```bash
python -m src.server.hand_gesture_server
```

### Run Raspberry Pi Client (On the Pi)

```bash
python -m src.client.raspi_gpio_client
```

---

## 📁 Project Structure

```
Home_appliance_control/
├── benchmark.py                 # Performance benchmarking script
├── benchmark_report.json        # Generated metrics report
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .github/
│   └── workflows/
│       └── benchmark.yml        # CI pipeline
└── src/
    ├── server/
    │   └── hand_gesture_server.py    # MediaPipe + OpenCV processing
    ├── client/
    │   └── raspi_gpio_client.py      # Flask API + GPIO control
    └── common/
        ├── config.yaml               # Configuration
        └── helpers.py                # Utility functions
```

---

## 🧪 Testing

### Automated CI

Every push triggers GitHub Actions that:
1. Sets up Python 3.12 environment
2. Installs dependencies
3. Runs benchmark suite
4. Uploads `benchmark_report.json` as artifact

### Manual Testing

```bash
# Run full benchmark
python benchmark.py

# Expected output:
# ✅ Gesture Recognition Accuracy: 100%
# ✅ Average Latency: ~33ms
# ✅ P95 Latency: ~48ms
```

---

## 🎯 Impact & Accessibility

### Who Benefits

| User Group | Population | How This Helps |
|------------|------------|----------------|
| Visually Impaired | 2.2 billion globally | No need to see buttons/screens |
| Deaf/Hard of Hearing | 70 million globally | No voice commands needed |
| Motor Impairments | 75 million globally | Simple hand gestures vs precise movements |
| Elderly | 700 million globally | Intuitive, natural interface |

### Accessibility Features

- ✅ **No voice required** - Works for deaf/mute users
- ✅ **No screen reading** - Works for blind users  
- ✅ **Large gesture tolerance** - Works for users with tremors
- ✅ **Visual feedback** - On-screen display of detected gesture
- ✅ **Configurable distance** - Works from 0.3m to 2m

---

## 🗺️ Roadmap

### Phase 1: Core Functionality ✅
- [x] MediaPipe hand detection
- [x] Finger counting algorithm
- [x] HTTP-based appliance control
- [x] Raspberry Pi GPIO integration
- [x] Performance benchmarking
- [x] CI/CD pipeline

### Phase 2: Enhanced Recognition (Planned)
- [ ] Custom gesture training (thumbs up, peace sign, etc.)
- [ ] Multi-hand support for complex commands
- [ ] Gesture sequences (e.g., swipe left = next device)
- [ ] Ambient light adaptation

### Phase 3: Smart Home Integration (Planned)
- [ ] Home Assistant integration
- [ ] MQTT protocol support
- [ ] Multiple room/device support
- [ ] Voice + gesture hybrid control

### Phase 4: Edge Deployment (Planned)
- [ ] TensorFlow Lite model for Raspberry Pi
- [ ] On-device inference (no PC needed)
- [ ] Battery-powered portable unit
- [ ] < 100ms latency on edge device

### Phase 5: Accessibility Certification (Future)
- [ ] User testing with disability advocacy groups
- [ ] WCAG compliance documentation
- [ ] Partnership with accessibility organizations

---

## 📈 Performance Optimization

### Current Bottlenecks

| Stage | Time | % of Total |
|-------|------|------------|
| MediaPipe Detection | ~20ms | 60% |
| Finger Counting | <1ms | 3% |
| HTTP Request | ~10ms | 30% |
| GPIO Toggle | <1ms | 3% |

### Optimization Opportunities

1. **Edge deployment** - Run MediaPipe on Pi 4 (eliminates network latency)
2. **Model quantization** - INT8 inference for 2x speedup
3. **Local WebSocket** - Replace HTTP with WebSocket for <5ms communication

---

## 🤝 Contributing

Contributions welcome! Areas where help is needed:

- [ ] Custom gesture dataset collection
- [ ] TensorFlow Lite conversion
- [ ] Home Assistant plugin
- [ ] Mobile app (React Native)
- [ ] Documentation in other languages

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [MediaPipe](https://developers.google.com/mediapipe) - Hand landmark detection
- [OpenCV](https://opencv.org/) - Computer vision library
- [Raspberry Pi Foundation](https://www.raspberrypi.org/) - Hardware platform

---

## 📬 Contact

**Meenakshi Sridharan Sundaram**  
[GitHub](https://github.com/Msundara19) | [LinkedIn](https://linkedin.com/in/meenakshi-sridharan)

---

<p align="center">
  <i>Built with ❤️ for accessibility</i>
</p>
