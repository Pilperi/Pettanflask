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
from pettanflask import KOTIKANSIO, TYOKANSIO, LOKAALI_KONE, ASETUSTIEDOSTO_TIETOKANNAT

# Thumbnailien peruskansio:
THUMBIKANSIO = os.path.join(KOTIKANSIO, ".pettanflask", "Thumbit")
if not os.path.exists(THUMBIKANSIO):
    LOGGER.info(f"Thumbikansiota {THUMBIKANSIO} ei ole, luodaan...")
    os.makedirs(THUMBIKANSIO)
    LOGGER.info("Luotiin.")

# Sallitut kuvaformaatit:
KUVATIEDOSTOT = (
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webm"
    )

LOGGER.info(
    f"Paikallinen kone {LOKAALI_KONE}"
    +f", kotikansio {KOTIKANSIO}"
    +f", työkansio {TYOKANSIO}"
    +f", asetustiedosto {ASETUSTIEDOSTO_TIETOKANNAT}"
    )

# Tiedostopuut dictinä, {str: Tiedostopuu tai None}
TIETOKANNAT = {}
INTERNETPUU = None
INTERNET = None

def lue_kuvatietokannat():
    '''
    Lue kuvatietokannat INI-tiedoston osoittamista sijainneista.
    Käyttökelpoinen jos tietokantojen sisältö halutaan
    päivittää ajan tasalle (ts. tietokantatiedosto luetaan uusiksi).
    '''
    global TIETOKANNAT
    global INTERNETPUU
    global INTERNET

    internet = TIETOKANNAT.get("internet")
    if internet is None:
        INTERNETPUU = None
        INTERNET = None
        errmsg = "Asetuksissa ei ole määritelty kuvakansion sijaintia..."
        LOGGER.error(errmsg)
        return
    # Määritä puu ja laita paikallinen kansiopolku saataville
    INTERNET = TIETOKANNAT["internet"]["tietokannan_kohde"]
    with open(TIETOKANNAT["internet"]["tietokannan_sijainti"], "r") as f:
        INTERNETPUU = Tiedostopuu.diktista(json.load(f))
        # Muokkaa puun juurisolmu juttelumuotoon
        INTERNETPUU.kansio = "internet"

def lue_asetustiedosto(polku=ASETUSTIEDOSTO_TIETOKANNAT, asetusnimi=LOKAALI_KONE):
    '''
    Määritä asetukset annetusta ini-tiedostosta.
    '''
    global TIETOKANNAT
    config = configparser.ConfigParser(default_section="pilperi")
    # Lue asetustiedosto
    if os.path.isfile(polku):
        config.read(polku)
    else:
        errmsg = f"Ei löydy asetustiedostoa {polku}"
        LOGGER.error(errmsg)
        raise OSError(errmsg)
    # Lue tietokantojen sijainnit ja tyypit asetuksista
    if asetusnimi not in config:
        errmsg = (
            f"Ei löydy asetuskokoonpanoa {asetusnimi}"
            +f" (löytyy: {[nimi for nimi in config]})"
            )
        LOGGER.error(errmsg)
        raise OSError(errmsg)
    TIETOKANNAT = json.loads(config.get(asetusnimi, "paikalliset_tietokannat"))
    lue_kuvatietokannat()

# Luetaan tietokannat mielellään vain kun tarvitsee
if not INTERNET:
    lue_asetustiedosto()
