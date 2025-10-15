import os
from flask import Flask, jsonify, request

USE_GPIO = False
try:
    import RPi.GPIO as GPIO  # type: ignore
    USE_GPIO = True
except Exception:
    # Allows development on non-Pi machines
    USE_GPIO = False

PIN = int(os.environ.get("RELAY_PIN", "18"))

app = Flask(__name__)

if USE_GPIO:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PIN, GPIO.OUT)

def _set_pin(state: bool):
    if USE_GPIO:
        GPIO.output(PIN, GPIO.HIGH if state else GPIO.LOW)
    else:
        print(f"[SIMULATED GPIO] PIN {PIN} -> {'HIGH' if state else 'LOW'}")

@app.post("/on")
def turn_on():
    _set_pin(True)
    return jsonify({"status": "ok", "pin": PIN, "state": "on"})

@app.post("/off")
def turn_off():
    _set_pin(False)
    return jsonify({"status": "ok", "pin": PIN, "state": "off"})

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "gpio": USE_GPIO})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8081"))
    app.run(host="0.0.0.0", port=port)