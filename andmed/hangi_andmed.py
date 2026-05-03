"""Lae andmed, arvuta tõenäosused ja tee tõenäosuste skaala."""

import json
import sys
from itertools import product
from pathlib import Path

import pandas as pd
import requests


stat_api = "https://andmed.stat.ee/api/v1/et/stat"
projekti_kaust = Path(__file__).parent.parent
andmete_kaust = projekti_kaust / "andmed"
valjundite_kaust = projekti_kaust / "valjundid"

sys.path.append(str(projekti_kaust))
from joonised.loo_graafik import loo_graafik


# ID-d ja päringud, mida challenge küsib.
tabelid = [
    {
        "tabeli_id": "RV047",
        "fail": "RV047_abielud_lahutused.json",
        "paring": [
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2025"]}},
            {"code": "Näitaja", "selection": {"filter": "item", "values": ["1", "5"]}},
        ],
    },
    {
        "tabeli_id": "RV56",
        "fail": "RV56_surnud_enesetapp.json",
        "paring": [
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2024"]}},
            {
                "code": "Surmapõhjus RHK-10 järgi",
                "selection": {"filter": "item", "values": ["1", "82"]},
            },
            {"code": "Sugu", "selection": {"filter": "item", "values": ["1"]}},
            {"code": "Vanuserühm", "selection": {"filter": "item", "values": ["1"]}},
        ],
    },
    {
        "tabeli_id": "JS154",
        "fail": "JS154_2015.json",
        "paring": [
            {
                "code": "Kuriteo liik",
                "selection": {
                    "filter": "item",
                    "values": ["2", "3", "4", "5", "7", "8", "9", "10", "12"],
                },
            },
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2015"]}},
        ],
    },
    {
        "tabeli_id": "JS153",
        "fail": "JS153_2015.json",
        "paring": [
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2015"]}},
        ],
    },
]


def hangi_stat_tabel(tabeli_id, paring):
    """Võtab tabeli id-le vastava andmestiku Statistikaameti API-st."""
    aadress = f"{stat_api}/{tabeli_id}"
    paringu_keha = {
        "query": paring,
        "response": {
            "format": "json-stat2",
        },
    }

    try:
        vastus = requests.post(aadress, json=paringu_keha, timeout=30)
        if vastus.status_code == 200:
            andmestik = vastus.json()
            if "value" in andmestik or "data" in andmestik:
                return andmestik
    except Exception as viga:
        print(f"{tabeli_id} päring ebaõnnestus: {viga}")

    return None


def salvesta_puuduvad_andmed():
    """Laeb alla ainult need JSON-failid, mida kaustas veel ei ole."""
    andmete_kaust.mkdir(exist_ok=True)

    leitud = False
    for tabel in tabelid:
        json_fail = andmete_kaust / tabel["fail"]
        if json_fail.exists():
            leitud = True
            continue

        andmestik = hangi_stat_tabel(tabel["tabeli_id"], tabel["paring"])

        # Salvestamisloogika on jäetud sinu algse koodi stiilis.
        if andmestik:
            with open(json_fail, "w", encoding="utf-8") as fail:
                json.dump(andmestik, fail, ensure_ascii=False, indent=2)
            leitud = True
        else:
            print(f"{tabel['tabeli_id']} ei saanud")

    if not leitud:
        print("andmeid ei leitud")
        exit()


def json_stat_tabeliks(json_fail):
    """Teisendab JSON-stat2 struktuuri tavaliseks pandas tabeliks."""
    with open(json_fail, "r", encoding="utf-8") as fail:
        andmestik = json.load(fail)

    mõõtmed = andmestik["id"]
    suurused = andmestik["size"]
    väärtused = andmestik["value"]
    mõõtme_valikud = []

    for mõõde in mõõtmed:
        kategooria = andmestik["dimension"][mõõde]["category"]
        indeksid = kategooria["index"]
        nimetused = kategooria["label"]

        if isinstance(indeksid, dict):
            koodid = sorted(indeksid, key=indeksid.get)
        else:
            koodid = indeksid

        mõõtme_valikud.append(
            [(mõõde, kood, nimetused.get(kood, kood)) for kood in koodid]
        )

    read = []
    for koht, kombinatsioon in enumerate(product(*mõõtme_valikud)):
        rida = {}
        for mõõde, kood, nimetus in kombinatsioon:
            rida[mõõde] = nimetus
            rida[f"{mõõde}_kood"] = kood
        rida["väärtus"] = väärtused[koht] if koht < len(väärtused) else None
        read.append(rida)

    oodatud_ridade_arv = 1
    for suurus in suurused:
        oodatud_ridade_arv *= suurus
    if oodatud_ridade_arv != len(read):
        raise ValueError(f"{json_fail.name}: mõõtmete suurused ei klapi ridade arvuga")

    return pd.DataFrame(read)


def leia_väärtus(tabel, veerg, otsitav_tekst):
    """Leiutab väärtuse rea järgi, mille nimetuses on otsitav tekst."""
    sobivad_read = tabel[tabel[veerg].str.contains(otsitav_tekst, case=False, na=False)]
    if sobivad_read.empty:
        raise ValueError(f"Ei leidnud kategooriat '{otsitav_tekst}' veerus '{veerg}'")
    return float(sobivad_read.iloc[0]["väärtus"])


def arvuta_tõenäosused():
    """Arvutab kõik graafikul näidatavad tõenäosused."""
    rv047 = json_stat_tabeliks(andmete_kaust / "RV047_abielud_lahutused.json")
    rv56 = json_stat_tabeliks(andmete_kaust / "RV56_surnud_enesetapp.json")
    js154 = json_stat_tabeliks(andmete_kaust / "JS154_2015.json")
    js153 = json_stat_tabeliks(andmete_kaust / "JS153_2015.json")

    abielud = leia_väärtus(rv047, "Näitaja", "Abielusid kokku")
    lahutused = leia_väärtus(rv047, "Näitaja", "Lahutusi kokku")

    kõik_surmad = leia_väärtus(rv56, "Surmapõhjus RHK-10 järgi", "Kõik põhjused")
    enesetapud = leia_väärtus(rv56, "Surmapõhjus RHK-10 järgi", "enesetapp")

    tapmise_eest_vangis = leia_väärtus(js154, "Kuriteo liik", "tahtlik tapmine")
    valitud_vangid = float(js154["väärtus"].fillna(0).sum())

    # Pika vangistuse eeldus: 10+ aastat, üle 30 aasta ja eluaegne vangistus.
    pika_vangistuse_koodid = ["6", "7", "8", "9"]
    pikk_vangistus = float(
        js153.loc[js153["Karistusaeg_kood"].isin(pika_vangistuse_koodid), "väärtus"].sum()
    )
    kõik_karistusajad = float(js153["väärtus"].fillna(0).sum())

    read = [
        ("Surm enesetapu tõttu", enesetapud / kõik_surmad, "Statistikaamet"),
        ("Kahe täringu summa 12", 1 / 36, "Võrdluspunkt"),
        ("Pikk vangistus", pikk_vangistus / kõik_karistusajad, "Statistikaamet"),
        ("Täring: kuus", 1 / 6, "Võrdluspunkt"),
        ("Vangis tapmise eest", tapmise_eest_vangis / valitud_vangid, "Statistikaamet"),
        ("Mündivise: kull", 1 / 2, "Võrdluspunkt"),
        ("Lahutused / abielud", lahutused / abielud, "Statistikaamet"),
    ]

    tõenäosused = pd.DataFrame(read, columns=["sündmus", "tõenäosus", "allikas"])
    return tõenäosused.sort_values("tõenäosus").reset_index(drop=True)


def põhiprogramm():
    """Käivitab kogu töövoo algusest lõpuni."""
    salvesta_puuduvad_andmed()
    tõenäosused = arvuta_tõenäosused()

    valjundite_kaust.mkdir(exist_ok=True)
    tõenäosused.to_csv(valjundite_kaust / "toenaosused.csv", index=False)
    loo_graafik(tõenäosused, valjundite_kaust / "toenaosuste_skaala.png")

    print(tõenäosused.to_string(index=False))
    print(f"\nGraafik salvestatud: {valjundite_kaust / 'toenaosuste_skaala.png'}")


if __name__ == "__main__":
    põhiprogramm()
