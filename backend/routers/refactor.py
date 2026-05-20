import requests

payload = {
    "model": "tinyllama",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10,
    "temperature": 0.2,
}

r = requests.post("http://127.0.0.1:11434/v1/chat/completions", json=payload, timeout=20)
print(r.status_code)
print(r.text)
