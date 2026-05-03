# Tõenäosuste skaala

Lihtne Python projekt RMK data team internship 2026 test challenge'i jaoks. Skript laeb Statistikaameti JSON-stat2 andmed, arvutab valitud sündmuste tõenäosused ja salvestab lineaarse 0-1 skaalaga graafiku.

## Käivitamine

```bash
pip install -r requirements.txt
python andmed/hangi_andmed.py
```

Tulemused:

- `valjundid/toenaosuste_skaala.png`
- `valjundid/toenaosused.csv`

## Andmed

Kasutatud Statistikaameti tabelid:

- `RV047` - abielud ja lahutused, 2025
- `RV56` - surmad ja enesetapud, 2024
- `JS154` - vangid süüteoliigi järgi, 2015
- `JS153` - vangid karistusaja järgi, 2015

JSON-id on kaustas `andmed/`. Kui mõni fail puudub, laeb skript selle API-st alla.

## Arvutused

- Lahutused / abielud = lahutused / abielud
- Surm enesetapu tõttu = enesetapud / kõik surmad
- Vangis tapmise eest = tapmise ja tapmiskatse eest vangis / valitud süüteoliikide vangid
- Pikk vangistus = 10+ aasta, üle 30 aasta ja eluaegse karistusega vangid / kõik karistusajad

Lisaks on graafikul võrdluspunktid: mündivise 1/2, täring 1/6 ja kahe täringu summa 12 ehk 1/36.

## Märkused

Graafik kasutab lineaarset x-telge vahemikus 0-1, et punktide tegelikud vahemaad säiliksid. Mõned arvud on pigem osakaalud kui päris tulevikutõenäosused, aga skaalal saab neid hästi võrrelda.
