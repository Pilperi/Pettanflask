'''
Lue asetukset ja testidata.
'''
import os
import json
import configparser

import pettanflask as vakiot
import pettanflask.pettan_musatietokanta as musavakiot
import pettanflask.pettan_html as htmlvakiot

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisi import Biisi

IP_OSOITE = "localhost"
PORTTI = "5000"
IP = f"http://{IP_OSOITE}:{PORTTI}/"


TESTIPOHJA = os.path.join(os.path.dirname(__file__), "data")
TESTIKANSIO_1 = os.path.join(TESTIPOHJA, "data1")
TESTIKANSIO_2 = os.path.join(TESTIPOHJA, "data2")
INI = os.path.join(TESTIPOHJA, "testiasetukset.ini")
JSON_1 = os.path.join(TESTIPOHJA, "testitietokanta_1.json")
JSON_2 = os.path.join(TESTIPOHJA, "testitietokanta_2.json")
TESTIPUU_1 = None
TESTIPUU_2 = None

def luo_testidata():
    '''Uudelleenluo uupuva testidata.'''
    global TESTIKANSIO_1
    global TESTIKANSIO_2
    global INI
    global IP_OSOITE
    global PORTTI
    global TESTIPUU

    config = configparser.ConfigParser(default_section="testi")
    # Biisit sellaisia että syvennystason kasvaessa numero kasvaa
    biisilista = [
        {
        "tiedostonimi": f"{b}.mp3",
        "albuminimi": f"{b}",
        "albumiesittaja": f"{b}",
        "esittaja": f"{b%2}",
        "biisinimi": f"{b}",
        "vuosi": f"{b}",
        "raita": b,
        "raitoja": b,
        "lisayspaiva": b,
        "hash": f"{b}",
        }
        for b in range(5)
        ]

    puudikti = {
        "tiedostotyyppi": Biisi.TYYPPI,
        "kansio": TESTIKANSIO_1,
        "tiedostot": [biisilista[0]],
        "alikansiot": [
            {
            "tiedostotyyppi": Biisi.TYYPPI,
            "kansio": "1",
            "tiedostot": [biisilista[1]],
            "alikansiot": []
            },
            {
            "tiedostotyyppi": Biisi.TYYPPI,
            "kansio": "2",
            "tiedostot": [biisilista[2]],
            "alikansiot": [
                {
                "tiedostotyyppi": Biisi.TYYPPI,
                "kansio": "3-4",
                "tiedostot": [biisilista[3], biisilista[4]],
                "alikansiot": []
                }
                ]
            }
            ]
        }

    config.set("testi", "paikalliset_tietokannat",
        json.dumps(
            {"testi-1":{
                "tietokannan_sijainti": JSON_1,
            	"tietokannan_kohde": TESTIKANSIO_1,
            	"tiedostotyyppi": "biisi"
                },
            "testi-2":{
                "tietokannan_sijainti": JSON_2,
            	"tietokannan_kohde": TESTIKANSIO_2,
            	"tiedostotyyppi": "biisi"
                }
            }, indent=4)
        )
    config.set("testi", "ip", IP_OSOITE)
    config.set("testi", "portti", PORTTI)
    with open(INI, 'w+') as configfile:
        config.write(configfile)

    # Yhdessä puussa kaikki läsnä
    puu = Tiedostopuu.diktista(puudikti)
    def luo_puuttuvat(kansio, vainparilliset=False):
        kansiopolku = kansio.hae_nykyinen_polku()
        if not os.path.exists(kansiopolku):
            os.makedirs(kansiopolku)
        for biisi in kansio.tiedostot:
            polku = os.path.join(kansiopolku, biisi.tiedostonimi)
            # Skippaa parillinen / poista jos löytyy
            if biisi.raita%2 and vainparilliset:
                if os.path.exists(polku):
                    os.remove(polku)
                continue
            with open(polku, "w+") as f:
                f.write(biisi.biisinimi)
        for alikansio in kansio.alikansiot:
            luo_puuttuvat(alikansio)
    luo_puuttuvat(puu)
    TESTIPUU_1 = puu.copy()
    # Toisessa vaan parilliset
    puu.kansio = TESTIKANSIO_2
    luo_puuttuvat(puu, vainparilliset=True)
    TESTIPUU_2 = puu

    # Kirjoita puut
    with open(JSON_1, "w+") as f:
        json.dump(TESTIPUU_1.diktiksi(), f)
    with open(JSON_2, "w+") as f:
        json.dump(TESTIPUU_2.diktiksi(), f)

if not TESTIPUU_1:
    luo_testidata()

inisijainti = os.path.dirname(os.path.dirname(__file__))
inisijainti = os.path.join(inisijainti, "tests", "data", "testiasetukset.ini")
vakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
musavakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
htmlvakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
