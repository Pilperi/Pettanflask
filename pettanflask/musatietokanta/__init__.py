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

LOGGER.info(
    f"Paikallinen kone {LOKAALI_KONE}"
    +f", kotikansio {KOTIKANSIO}"
    +f", työkansio {TYOKANSIO}"
    +f", asetustiedosto {ASETUSTIEDOSTO_TIETOKANNAT}"
    )


# Tiedostopuut dictinä, {str: Tiedostopuu tai None}
TIETOKANNAT = {}
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

def lue_asetukset_tiedostosta(polku=ASETUSTIEDOSTO_TIETOKANNAT, asetusnimi=LOKAALI_KONE):
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
    global TIETOKANNAT
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
            +f" (löytyy: {[nimi for nimi in config]})"
            )
        LOGGER.error(errmsg)
        raise OSError(errmsg)
    TIETOKANNAT = json.loads(config.get(asetusnimi, "paikalliset_tietokannat"))
    lue_biisitietokannat()


# Luetaan tietokannat mielellään vain kun tarvitsee
if not BIISIPUUT:
    lue_asetukset_tiedostosta()
