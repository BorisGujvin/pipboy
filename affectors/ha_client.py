# ha_client.py
import requests

HA_IP = "192.168.50.35"
HA_PORT = 8123
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZDU1YjE2NjAzYTY0MjJhOTE5MjMxOTZlYTE3OWNmMyIsImlhdCI6MTc2NDI0MTM0NiwiZXhwIjoyMDc5NjAxMzQ2fQ.qVnpPz8LLnE9oZCDXse8lxoCCLwVjTQJN7NSoZR-5kQ"

BASE = f"http://{HA_IP}:{HA_PORT}/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def get_state(entity_id: str) -> bool:
    r = requests.get(f"{BASE}/states/{entity_id}", headers=HEADERS, timeout=8)
    r.raise_for_status()
    return r.json().get("state") == "on"

def toggle(entity_id: str) -> bool:
    cur = get_state(entity_id)
    service = "turn_off" if cur else "turn_on"
    r = requests.post(
        f"{BASE}/services/switch/{service}",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"entity_id": entity_id},
        timeout=8
    )
    r.raise_for_status()
    return get_state(entity_id)
