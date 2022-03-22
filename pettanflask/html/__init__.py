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


# Luetaan tietokannat mielellään vain kun tarvitsee
if not INTERNET:
    lue_kuvatietokannat()
