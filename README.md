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

Run `python benchmark.py` to reproduce.

## Gesture Mapping

- 1 finger = OFF
- 2 fingers = ON
- 3 fingers = VOL+
- 4 fingers = VOL-

## Quick Start
```bash
pip install -r requirements.txt
python benchmark.py
```