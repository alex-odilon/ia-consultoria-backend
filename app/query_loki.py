import requests
import urllib.parse
import json
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

LOKI_URL = os.getenv("LOKI_URL")
GRAFANA_EXPLORE_URL = os.getenv("GRAFANA_EXPLORE_URL")

def query_logs(application: str, limit: int = 10):
    query = f'{{application="{application}"}}'
    params = {
        "query": query,
        "limit": str(limit)
    }
    resp = requests.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
    data = resp.json()
    logs = []
    for stream in data.get("data", {}).get("result", []):
        for entry in stream.get("values", []):
            logs.append(entry[1])
    return logs

def build_grafana_link(application: str):
    expr = {
        "expr": f'{{application="{application}"}}'
    }
    payload = ["now-1h", "now", "Loki", expr]
    encoded = urllib.parse.quote(json.dumps(payload))
    return GRAFANA_EXPLORE_URL + encoded
