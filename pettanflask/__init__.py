'''
Globaalit vakiot.
'''
import os
import json
import configparser
import pkg_resources
import logging

LOGGER = logging.getLogger(__name__)

# Lue tiedostopolut kotikansion .ini-tiedostosta
KOTIKANSIO = os.path.expanduser("~")
TYOKANSIO = os.path.join(KOTIKANSIO, ".pettanflask")
LOKAALI_KONE = os.path.basename(KOTIKANSIO)

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
ASETUSTIEDOSTO = os.path.join(TYOKANSIO, "pettanvakiot.ini")
LOGGER.info(
    f"Paikallinen kone {LOKAALI_KONE}"
    +f", kotikansio {KOTIKANSIO}"
    +f", työkansio {TYOKANSIO}"
    +f", asetustiedosto {ASETUSTIEDOSTO}"
    )
config = configparser.ConfigParser(default_section="taira")

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

IP_OSOITE = config.get(LOKAALI_KONE, "ip")
PORTTI = config.get(LOKAALI_KONE, "portti")

# Jos ei annettu, koeta selvittää
if not IP_OSOITE:
    from requests import get as rget
    IP_OSOITE = rget("https://api.ipify.org").content.decode("ascii")
if not PORTTI:
    PORTTI = "5000"

IP = f"{IP_OSOITE}:{PORTTI}"
