import requests

response = requests.post(
    "http://localhost:8000/chat",
    headers={"X-Forwarded-For": "8.8.8.8"},
    json={"message": "Find labor lawyers"}
)
print(response.json())