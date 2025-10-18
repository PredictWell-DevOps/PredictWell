import httpx

payload={
  "age": 25,
  "height": 72,
  "weight": 180,
  "handedness": "right",
  "arm_slot": "overhead",
  "velocity": 86.0,
  "workload": 50
}

try:
    with httpx.Client() as c:
        r = c.post("http://127.0.0.1:8000/athletics/risk", json=payload, timeout=10.0)
    print("status", r.status_code)
    print(r.text)
except Exception as e:
    print("ERROR", e)
