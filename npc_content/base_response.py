import os
import requests
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.environ.get("WORLDANVIL_API_TOKEN", "")
WORLD_ID = "zarthuga-aecorn"
BASE_URL = f"https://www.worldanvil.com/api/aragorn/world/{WORLD_ID}"

headers = {"x-auth-token": TOKEN,
"x-application-key": "Tt8RbuX7KD65F6QSHmhWvZLT7VAfCbZqbyBT6vY6BhbwfH4R2Y3",
"Content-type": "application/json",
"User-Agent":  "Zarthuga ( $url, $version )"}


result = requests.get(BASE_URL + "/article/captain-busgar-person", headers=headers)
print(result.text, result.status_code)
