import requests

resp = requests.get("http://localhost:1234/v1/cocktail/fav",
                    headers={
                        "Content-Type": "application/json",
                        "username": "user",
                        "password": "pass",
                    })
print(f"status: {resp.status_code}")
print(resp.content)
