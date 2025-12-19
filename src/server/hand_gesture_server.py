"""
Hand Gesture Server with Performance Metrics
Real-time hand gesture recognition for home appliance control
Tracks latency, accuracy, and FPS for quantifiable impact
"""

import cv2
import mediapipe as mp
import requests
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from src.common.helpers import load_config

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

cfg = load_config()
CAMERA_INDEX = int(cfg.get("camera_index", 0))
RASPI_BASE = cfg.get("raspi_base_url", "http://127.0.0.1:8081")
SIMULATION = bool(cfg.get("simulation_mode", True))
TIMEOUT = float(cfg.get("request_timeout_sec", 2.5))
DRAW_TEXT = bool(cfg.get("draw_debug_text", True))

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# -----------------------------------------------------------------------------
# Metrics Tracking
# -----------------------------------------------------------------------------

@dataclass
class PerformanceMetrics:
    """Track all performance metrics for the gesture recognition system."""
    
    # Latency metrics (in milliseconds)
    frame_capture_times: List[float] = field(default_factory=list)
    detection_times: List[float] = field(default_factory=list)
    action_times: List[float] = field(default_factory=list)
    total_latencies: List[float] = field(default_factory=list)
    
    # Accuracy metrics
    total_frames: int = 0
    frames_with_hand: int = 0
    gestures_detected: int = 0
    actions_triggered: int = 0
    
    # Per-gesture tracking
    gesture_counts: Dict[str, int] = field(default_factory=lambda: {
        "ON": 0, "OFF": 0, "VOL+": 0, "VOL-": 0, "NONE": 0
    })
    
    # FPS tracking
    fps_samples: List[float] = field(default_factory=list)
    
    # Session info
    start_time: float = field(default_factory=time.time)
    
    def add_latency(self, frame_ms: float, detect_ms: float, action_ms: float):
        """Record latency for one frame."""
        self.frame_capture_times.append(frame_ms)
        self.detection_times.append(detect_ms)
        self.action_times.append(action_ms)
        self.total_latencies.append(frame_ms + detect_ms + action_ms)
    
    def add_fps(self, fps: float):
        """Record FPS sample."""
        self.fps_samples.append(fps)
    
    def record_gesture(self, action: Optional[str]):
        """Record a gesture detection."""
        self.gestures_detected += 1
        if action:
            self.gesture_counts[action] = self.gesture_counts.get(action, 0) + 1
            self.actions_triggered += 1
        else:
            self.gesture_counts["NONE"] += 1
    
    def get_summary(self) -> Dict:
        """Generate summary statistics."""
        def safe_avg(lst):
            return sum(lst) / len(lst) if lst else 0
        
        def safe_percentile(lst, p):
            if not lst:
                return 0
            sorted_lst = sorted(lst)
            idx = int(len(sorted_lst) * p / 100)
            return sorted_lst[min(idx, len(sorted_lst) - 1)]
        
        runtime = time.time() - self.start_time
        
        return {
            "session": {
                "runtime_seconds": round(runtime, 2),
                "total_frames": self.total_frames,
                "frames_with_hand": self.frames_with_hand,
                "hand_detection_rate": round(self.frames_with_hand / max(self.total_frames, 1) * 100, 1),
            },
            "latency_ms": {
                "avg_total": round(safe_avg(self.total_latencies), 2),
                "avg_detection": round(safe_avg(self.detection_times), 2),
                "avg_action": round(safe_avg(self.action_times), 2),
                "p50_total": round(safe_percentile(self.total_latencies, 50), 2),
                "p95_total": round(safe_percentile(self.total_latencies, 95), 2),
                "p99_total": round(safe_percentile(self.total_latencies, 99), 2),
                "min_total": round(min(self.total_latencies) if self.total_latencies else 0, 2),
                "max_total": round(max(self.total_latencies) if self.total_latencies else 0, 2),
            },
            "fps": {
                "avg": round(safe_avg(self.fps_samples), 1),
                "min": round(min(self.fps_samples) if self.fps_samples else 0, 1),
                "max": round(max(self.fps_samples) if self.fps_samples else 0, 1),
            },
            "gestures": {
                "total_detected": self.gestures_detected,
                "actions_triggered": self.actions_triggered,
                "breakdown": self.gesture_counts,
            },
        }
    
    def save_report(self, filepath: str = "metrics_report.json"):
        """Save metrics report to JSON file."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "raw_latencies_sample": {
                "total_ms": self.total_latencies[-100:] if self.total_latencies else [],
                "detection_ms": self.detection_times[-100:] if self.detection_times else [],
            }
        }
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📊 Metrics saved to {filepath}")
        return report


# -----------------------------------------------------------------------------
# Core Functions
# -----------------------------------------------------------------------------

def count_extended_fingers(lm: List[List[int]]) -> int:
    """Count extended fingers from hand landmarks."""
    if not lm or len(lm) < 21:
        return 0
    
    def is_extended(tip, pip):
        return lm[tip][2] < lm[pip][2]
    
    fingers = 0
    # Index, Middle, Ring, Little
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if is_extended(tip, pip):
            fingers += 1
    # Thumb: compare x relative to knuckle
    if lm[4][1] < lm[3][1]:
        fingers += 1
    return fingers


def call_endpoint(path: str) -> float:
    """Call endpoint and return response time in ms."""
    url = f"{RASPI_BASE}{path}"
    start = time.perf_counter()
    
    if SIMULATION:
        # Simulate network latency
        time.sleep(0.01)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[SIM] {url} ({elapsed:.1f}ms)")
        return elapsed
    
    try:
        resp = requests.post(url, timeout=TIMEOUT)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[{resp.status_code}] {url} ({elapsed:.1f}ms)")
        return elapsed
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[ERR] {url} :: {e}")
        return elapsed


def gesture_to_action(fingers: int) -> tuple[Optional[str], float]:
    """Map finger count to action, return action and HTTP latency."""
    http_latency = 0.0
    
    if fingers == 2:
        http_latency = call_endpoint("/on")
        return "ON", http_latency
    if fingers == 1:
        http_latency = call_endpoint("/off")
        return "OFF", http_latency
    if fingers == 3:
        return "VOL+", 0.0
    if fingers == 4:
        return "VOL-", 0.0
    return None, 0.0


# -----------------------------------------------------------------------------
# Main Loop with Metrics
# -----------------------------------------------------------------------------

def main():
    metrics = PerformanceMetrics()
    
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {CAMERA_INDEX}")
    
    print("=" * 60)
    print("🎯 Hand Gesture Control with Performance Metrics")
    print("=" * 60)
    print(f"Camera: {CAMERA_INDEX} | Simulation: {SIMULATION}")
    print("Press 'q' to quit and see metrics report")
    print("Press 'm' to show current metrics")
    print("=" * 60)
    
    last_action = None
    last_time = 0.0
    action_cooldown = 0.75
    
    # FPS calculation
    fps_start = time.perf_counter()
    fps_frame_count = 0
    current_fps = 0.0
    
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    ) as hands:
        
        while True:
            # --- Frame Capture ---
            t_frame_start = time.perf_counter()
            ok, frame = cap.read()
            if not ok:
                break
            t_frame_end = time.perf_counter()
            frame_ms = (t_frame_end - t_frame_start) * 1000
            
            metrics.total_frames += 1
            fps_frame_count += 1
            
            # Calculate FPS every second
            fps_elapsed = time.perf_counter() - fps_start
            if fps_elapsed >= 1.0:
                current_fps = fps_frame_count / fps_elapsed
                metrics.add_fps(current_fps)
                fps_frame_count = 0
                fps_start = time.perf_counter()
            
            # --- Hand Detection ---
            t_detect_start = time.perf_counter()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)
            t_detect_end = time.perf_counter()
            detect_ms = (t_detect_end - t_detect_start) * 1000
            
            action_ms = 0.0
            
            if res.multi_hand_landmarks:
                metrics.frames_with_hand += 1
                
                for hand_lms in res.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
                
                h, w, _ = frame.shape
                lms = []
                for idx, lm in enumerate(res.multi_hand_landmarks[0].landmark):
                    lms.append([idx, int(lm.x * w), int(lm.y * h)])
                
                fingers = count_extended_fingers(lms)
                now = time.time()
                
                # --- Action Trigger ---
                if now - last_time > action_cooldown:
                    t_action_start = time.perf_counter()
                    action, http_ms = gesture_to_action(fingers)
                    t_action_end = time.perf_counter()
                    action_ms = (t_action_end - t_action_start) * 1000
                    
                    if action:
                        last_action = action
                        last_time = now
                        metrics.record_gesture(action)
                
                # Record latency
                metrics.add_latency(frame_ms, detect_ms, action_ms)
                
                # --- Display ---
                if DRAW_TEXT:
                    total_ms = frame_ms + detect_ms + action_ms
                    txt1 = f"Fingers: {fingers} | Action: {last_action or '-'}"
                    txt2 = f"Latency: {total_ms:.0f}ms | FPS: {current_fps:.0f}"
                    cv2.putText(frame, txt1, (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, txt2, (16, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            else:
                metrics.add_latency(frame_ms, detect_ms, 0)
                if DRAW_TEXT:
                    cv2.putText(frame, "No hand detected", (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(frame, f"FPS: {current_fps:.0f}", (16, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow("Gesture Control + Metrics", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                # Print current metrics
                print("\n" + "=" * 40)
                print("📊 CURRENT METRICS")
                print("=" * 40)
                summary = metrics.get_summary()
                print(json.dumps(summary, indent=2))
    
    cap.release()
    cv2.destroyAllWindows()
    
    # --- Final Report ---
    print("\n" + "=" * 60)
    print("📊 FINAL PERFORMANCE REPORT")
    print("=" * 60)
    
    summary = metrics.get_summary()
    
    print(f"\n⏱️  SESSION: {summary['session']['runtime_seconds']}s")
    print(f"   Total frames: {summary['session']['total_frames']}")
    print(f"   Hand detection rate: {summary['session']['hand_detection_rate']}%")
    
    print(f"\n⚡ LATENCY (ms):")
    print(f"   Average: {summary['latency_ms']['avg_total']}ms")
    print(f"   P50: {summary['latency_ms']['p50_total']}ms")
    print(f"   P95: {summary['latency_ms']['p95_total']}ms")
    print(f"   P99: {summary['latency_ms']['p99_total']}ms")
    print(f"   Range: {summary['latency_ms']['min_total']} - {summary['latency_ms']['max_total']}ms")
    
    print(f"\n🎬 FPS:")
    print(f"   Average: {summary['fps']['avg']}")
    print(f"   Range: {summary['fps']['min']} - {summary['fps']['max']}")
    
    print(f"\n🖐️  GESTURES:")
    print(f"   Actions triggered: {summary['gestures']['actions_triggered']}")
    for gesture, count in summary['gestures']['breakdown'].items():
        if count > 0:
            print(f"   {gesture}: {count}")
    
    # Save report
    report = metrics.save_report("metrics_report.json")
    
    print("\n" + "=" * 60)
    print("✅ Use these metrics in your resume!")
    print("=" * 60)
    
    # Generate resume bullet points
    avg_latency = summary['latency_ms']['avg_total']
    p95_latency = summary['latency_ms']['p95_total']
    detection_rate = summary['session']['hand_detection_rate']
    avg_fps = summary['fps']['avg']
    
    print(f"\n📝 SUGGESTED RESUME BULLETS:")
    print(f'   • "Achieved {detection_rate}% hand detection accuracy with {avg_latency:.0f}ms average latency"')
    print(f'   • "Real-time gesture processing at {avg_fps:.0f} FPS with P95 latency of {p95_latency:.0f}ms"')
    print(f'   • "Sub-{max(100, int(p95_latency))}ms end-to-end gesture-to-action pipeline"')


if __name__ == "__main__":
    main()