import os
import sys
import json
import requests

HA_IP = os.getenv("HA_IP", "192.168.50.35")  # если HA на этой же малинке
TOKEN = os.getenv("HA_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZDU1YjE2NjAzYTY0MjJhOTE5MjMxOTZlYTE3OWNmMyIsImlhdCI6MTc2NDI0MTM0NiwiZXhwIjoyMDc5NjAxMzQ2fQ.qVnpPz8LLnE9oZCDXse8lxoCCLwVjTQJN7NSoZR-5kQ")
ENTITY = os.getenv("HA_ENTITY", "switch.sonoff_1002036b3f_1")

BASE = f"http://{HA_IP}:8123/api"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def turn(service: str):
    url = f"{BASE}/services/switch/{service}"
    r = requests.post(url, headers=HEADERS, json={"entity_id": ENTITY}, timeout=10)
    r.raise_for_status()

def state() -> str:
    url = f"{BASE}/states/{ENTITY}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json().get("state", "unknown")

def main():
    if len(sys.argv) < 2:
        print("Usage: socket.py on|off|toggle|state")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "on":
        turn("turn_on")
        print("ON")
    elif cmd == "off":
        turn("turn_off")
        print("OFF")
    elif cmd == "toggle":
        st = state()
        if st == "on":
            turn("turn_off")
            print("OFF")
        else:
            turn("turn_on")
            print("ON")
    elif cmd == "state":
        print(state())
    else:
        print("Unknown command. Use: on|off|toggle|state")
        sys.exit(2)

if __name__ == "__main__":
    main()
