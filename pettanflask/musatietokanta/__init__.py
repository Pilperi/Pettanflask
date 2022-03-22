'''
Määritä operointiin tarvittavat tiedostopolut ymv. vakioiksi.
'''

import os
import json
import configparser
import pkg_resources
import logging

LOGGER = logging.getLogger(__name__)

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import Artistipuu

# Lue tiedostopolut kotikansion .ini-tiedostosta
KOTIKANSIO = os.path.expanduser("~")
TYOKANSIO = os.path.join(KOTIKANSIO, ".tiedostohallinta")
LOKAALI_KONE = os.path.basename(KOTIKANSIO)

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
ASETUSTIEDOSTO = os.path.join(TYOKANSIO, "kansiovakiot.ini")
LOGGER.info(
    f"Paikallinen kone {LOKAALI_KONE}"
    +f", kotikansio {KOTIKANSIO}"
    +f", työkansio {TYOKANSIO}"
    +f", asetustiedosto {ASETUSTIEDOSTO}"
    )
config = configparser.ConfigParser(default_section="pilperi")

# Lue asetustiedosto
if os.path.isfile(ASETUSTIEDOSTO):
    config.read(ASETUSTIEDOSTO)
else:
    errmsg = f"Ei löydy asetustiedostoa {ASETUSTIEDOSTO}!"
    LOGGER.error(errmsg)
    raise OSError(errmsg)

# Lue tietokantojen sijainnit ja tyypit asetuksista
if LOKAALI_KONE not in config:
    errmsg = (
        f"Ei löydy asetuskokoonpanoa {LOKAALI_KONE}"
        +f" (löytyy: {[nimi for nimi in config]})"
        )
    LOGGER.error(errmsg)
    raise OSError(errmsg)
TIETOKANNAT = json.loads(config.get(LOKAALI_KONE, "paikalliset_tietokannat"))

# Tiedostopuut dictinä, {str: Tiedostopuu tai None}
BIISIPUUT = {}
ARTISTIPUUT = {}
PAIKALLISPOLUT = {}

def lue_biisitietokannat():
    '''
    Lue biisitietokannat INI-tiedoston osoittamista sijainneista.
    Käyttökelpoinen jos tietokantojen sisältö halutaan
    päivittää ajan tasalle (ts. tietokantatiedosto luetaan uusiksi).
    '''
    global TIETOKANNAT
    global PAIKALLISPOLUT
    global BIISIPUUT
    global ARTISTIPUUT
    for nimi,tietokanta in TIETOKANNAT.items():
        # Vain biisejä koskevat tiedostopuut
        if tietokanta["tiedostotyyppi"] != "biisi":
            continue
        puutiedosto = tietokanta["tietokannan_sijainti"]
        # Jos tiedostopuuta ei ole, ilmaistaan asia
        # (muttei kaadeta mitään)
        if not os.path.exists(puutiedosto):
            BIISIPUUT[nimi] = None
            ARTISTIPUUT[nimi] = None
            PAIKALLISPOLUT[nimi] = None
            continue
        with open(puutiedosto, "r") as f:
            puu = Tiedostopuu.diktista(json.load(f))
            # Muokkaa puun juurisolmu juttelumuotoon
            puu.kansio = nimi
            # Juurisolmu yhä palvelinpuolella saatavilla:
            PAIKALLISPOLUT[nimi] = tietokanta["tietokannan_kohde"]
            BIISIPUUT[nimi] = puu
            ARTISTIPUUT[nimi] = Artistipuu(puu) # tää muunnos on aika rumba


# Luetaan tietokannat mielellään vain kun tarvitsee
if not BIISIPUUT:
    lue_biisitietokannat()
