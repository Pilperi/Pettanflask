'''
Globaalit vakiot.
'''
import os
import logging
import json
import configparser
import pkg_resources
from requests import get as rget

LOGGER = logging.getLogger(__name__)

# Lue tiedostopolut kotikansion .ini-tiedostosta
KOTIKANSIO = os.path.expanduser("~")
TYOKANSIO = os.path.join(KOTIKANSIO, ".pettanflask")
LOKAALI_KONE = os.path.basename(KOTIKANSIO)

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
ASETUSTIEDOSTO = os.path.join(TYOKANSIO, "pettanvakiot.ini")
ASETUSTIEDOSTO_TIETOKANNAT = os.path.join(KOTIKANSIO, ".tiedostohallinta", "kansiovakiot.ini")
kokoonpatostr = (
    f"Paikallinen kone {LOKAALI_KONE}\n"
    +f", kotikansio {KOTIKANSIO}\n"
    +f", työkansio {TYOKANSIO}\n"
    +f", asetustiedosto {ASETUSTIEDOSTO}"
    )
print(kokoonpatostr)
LOGGER.info(
    kokoonpatostr
    )

IP = None
IP_OSOITE = None
PORTTI = 5000

def lue_asetukset_tiedostosta(polku=ASETUSTIEDOSTO, asetusnimi=LOKAALI_KONE):
    '''
    Määritä asetukset ini-tiedoston avulla.
    Mahdollistaa eri asetustiedoston käytön eri ajokerroilla
    (esim. yksikkötesteissä eri asetukset kuin normikäytössä)

    Sisään
    ------
    polku : str
        ini-tiedoston polku.
        Tiedostolla sama rakenne kuin oikealla asetustiedostolla.
    asetusnimi : str
        Asetussetti joka ini-tiedostosta olisi tarkoitus lukea.
    '''
    global IP, IP_OSOITE, PORTTI
    config = configparser.ConfigParser(default_section=asetusnimi)

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
            +f" (löytyy: {list(config)})"
            )
        LOGGER.error(errmsg)
        raise OSError(errmsg)
    IP_OSOITE = config.get(asetusnimi, "ip")
    PORTTI = config.get(asetusnimi, "portti")
    # Jos ei annettu, koeta selvittää
    if not IP_OSOITE:
        IP_OSOITE = rget("https://api.ipify.org").content.decode("ascii")
    if not PORTTI:
        PORTTI = "5000"
    IP = f"{IP_OSOITE}:{PORTTI}"

# Luetaan tietokannat mielellään vain kun tarvitsee
if not IP_OSOITE:
    lue_asetukset_tiedostosta()
