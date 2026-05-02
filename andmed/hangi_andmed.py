import json
import requests
from pathlib import Path

stat_api = "https://andmed.stat.ee/api/v1/et/stat"

# VÕtab id-le vastava tabeli API calliga
def hangi_stat_tabel(tabeli_id):
    url = f"{stat_api}/{tabeli_id}"
    pairing = {
        "query": [],
        "response": {
            "format": "json-stat2"
        }
    }
    
    try:
        response = requests.post(url, json=pairing, timeout=10)
        if response.status_code == 200:
            andmestik = response.json()
            if 'value' in andmestik or 'data' in andmestik:
                return andmestik
    except Exception as e:
        pass
    
    return None

#ID
tabel_ids = [
    "JS154",      # Vanglaasutustes viibivad
    "JS153",      # Vanglaasutustes karistusaja järgi
    "SD41",       # Narkootiliste ainete tõttu surmad
    "SD22",       # Surmad 100 000 elaniku kohta
]


#kontroll et kas tabel on olemas
leitud = False
for tabel_id in tabel_ids:
    tabel = hangi_stat_tabel(tabel_id)
    
    
    #SALVESTAMIS LOOGIKA
    if tabel:
       
        kaust = Path(__file__).parent.parent / "joonised"
        kaust.mkdir(exist_ok=True)
        
        json_fail = kaust / f"{tabel_id}.json"
        with open(json_fail, 'w', encoding='utf-8') as f:
            json.dump(tabel, f, ensure_ascii=False, indent=2)
        
        leitud = True
    else:
        print(f"{tabel_id} ei saand")


if not leitud:
    print("andmeid ei leitud ")
    exit()

