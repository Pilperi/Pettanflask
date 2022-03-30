'''
Funktiot joilla etsiskellään biisipuista kamaa.
Lähinnä kutsutaan main-puolelta aina kun
toinen pääty haluaa jotain biiseihin liittyvää kamaa.
'''
import logging
from flask import make_response, jsonify

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import Hakukriteerit

import pettanflask.pettan_musatietokanta as musavak

LOGGER = logging.getLogger(__name__)


def listaa_tietokannat(*args):
    '''Listaa tarjolla olevat tietokannat.

    Sisään
    ------
    (ei tarvii, voi antaa muttei tee mitään)

    Ulos
    ----
    response
        Standardi vastaus, eli flaskin HTTP-JSON vastauskoodin kera.
        Diktiosiossa arvot {"VASTAUS": [str], "VIRHE": None}
        missä vastauksena käytettävissä olevien tietokantojen nimet
        ja virhe on aina None.
    '''
    paluuarvo = {
        "VASTAUS": list(musavak.BIISIPUUT),
        "VIRHE": None
        }
    return make_response(jsonify(paluuarvo), 200)



def anna_tietokanta(tietokannan_nimi):
    '''Hae tietokantaa nimen perusteella.

    Sisään
    ------
    tietokannan_nimi : str
        Tietokannan nimi.

    Ulos
    ----
    response
        Standardi vastaus, eli flaskin HTTP-JSON vastauskoodin kera.
        Diktiosiossa arvot {"VASTAUS": dict, "VIRHE": str tai None}
        missä vastauksena löytyneen tietokannan diktiversio
        tai None jos tietokantaa ei löytynyt, ja virheen alla
        virhekuvatusstringi jos jokin mättää.
    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    puu = musavak.BIISIPUUT.get(tietokannan_nimi)
    # Ei löydy nimellä
    if puu is None:
        errmsg = (
            f"Ei löydy tietokantaa nimeltä {tietokannan_nimi}."
            +f" Löytyy: {list(musavak.BIISIPUUT)}"
            )
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 404)
    paluuarvo["VASTAUS"] = puu.diktiksi()
    return make_response(jsonify(paluuarvo), 200)


def etsi_tietokannasta(puu, hakudikti, artistipuuna=False):
    '''Suorita haku puun sisällöstä.

    Sisään
    ------
    puu : str
        Puu josta hakutuloksia etsitään, puun nimen muodossa.
    hakudikti : dict
        Hakukriteerit dictinä.
        Rakenne
        {
        "ehtona_ja": bool,
        "artistissa": [str],
        "biisissa": [str],
        "albumissa": [str],
        "tiedostossa": [str],
        "raitanumero": [int, int], # min, max
        "vapaahaku": [str],
        }
    artistipuuna : bool
        Jos True, anna tulospuu artistipuun muodossa
        (artisti-albumi-biisi eikä tavallinen kansio-biisi).
        Valinnainen, oletuksena False (anna tulos tavallisena tiedostopuuna).
        EI VIELÄ IMPLEMENTOITU

    Ulos
    ----
    response
        Tulospuu dictin muodossa.
        {"VASTAUS": dict, "VIRHE": str tai None}
    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    # Huonon niminen puu
    if puu not in musavak.BIISIPUUT:
        errmsg = f"Ei puuta nimeltä {puu}. Löytyy: {list(musavak.BIISIPUUT)}"
        LOGGER.error(errmsg)
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 404)
    haku = Hakukriteerit(hakudikti)
    hakutulokset = haku.etsi_tietokannasta(puu)
    if artistipuuna:
        errmsg = "Artistipuun diktimuunnosta ei ole vielä implementoitu..."
        LOGGER.error(errmsg)
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 400)
    hakutulokset[1].kansio = puu.kansio # def. 'biisi'
    paluuarvo["VASTAUS"] = hakutulokset[1].diktiksi()
    return make_response(jsonify(paluuarvo), 200)


def anna_latauslista(puu):
    '''Muodosta puu listaksi latauspolkustringejä.

    Sisään
    ------
    puu : Tiedostopuu tai dict
        Puu jota ollaan lataamassa.
        Yleensä käytännössä joku tietty
        kansio joka halutaan ladata alikansioineen
        (artistin tuotanto tmv)

    Ulos
    ----
    [str]
        Latauspolut listana stringejä.
        Polut sitä muotoa mitä palvelin ottaa
        "suoraan" sisäänsä.
    '''
    def muodosta_latauslista(puu):
        lista = []
        for tiedosto in puu.tiedostot:
            lista.append(puu.hae_nykyinen_polku() + f"/{tiedosto.tiedostonimi}")
        for alikansio in puu.alikansiot:
            lista += muodosta_latauslista(alikansio)
        return lista

    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    # Puu väärää datatyyppiä
    if not isinstance(puu, dict):
        errmsg = f"Puu ei ole dict vaan {type(puu)}"
        LOGGER.error(errmsg)
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 400)
    tiedostopuu = Tiedostopuu.diktista(puu)
    paluuarvo["VASTAUS"] = muodosta_latauslista(tiedostopuu)
    return make_response(jsonify(paluuarvo), 200)
