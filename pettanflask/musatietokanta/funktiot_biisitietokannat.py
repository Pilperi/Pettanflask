'''
Funktiot joilla etsiskellään biisipuista kamaa.
Lähinnä kutsutaan main-puolelta aina kun
toinen pääty haluaa jotain biiseihin liittyvää kamaa.
'''
import logging

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import Hakukriteerit, Artistipuu


LOGGER = logging.getLogger(__name__)


def etsi_puusta(puu, hakudikti, artistipuuna=False):
    '''Suorita haku puun sisällöstä.

    Sisään
    ------
    puu : Tiedostopuu
        Puu josta hakutuloksia etsitään.
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
        Jos True, anna tulospuu artistipuun
        muodossa (artisti-albumi-biisi eikä
        tavallinen kansio-biisi).
        Valinnainen, oletuksena False
        (anna tulos tavallisena tiedostopuuna).
        EI VIELÄ IMPLEMENTOITU

    Ulos
    ----
    dict
        Tulospuu dictin muodossa.
        (Tiedostopuu.diktiksi() ulostulo).
        Virheen tapauksessa {"VIRHE": str}
    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    haku = Hakukriteerit(hakudikti)
    tuloksia, hakutulokset = haku.etsi_tietokannasta(puu)
    if artistipuuna:
        errmsg = "Artistipuun diktimuunnosta ei ole vielä implementoitu..."
        LOGGER.error(errmsg)
        paluuarvo["VIRHE"] = errmsg
    hakutulokset.kansio = puu.kansio
    paluuarvo["VASTAUS"] = hakutulokset.diktiksi()
    return paluuarvo


def puun_latauslista(puu):
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
    lista = []
    if isinstance(puu, dict):
        puu = Tiedostopuu.diktista(puu)
    for tiedosto in puu.tiedostot:
        lista.append(puu.hae_nykyinen_polku() + f"/{tiedosto.tiedostonimi}")
    for alikansio in puu.alikansiot:
        lista += puun_latauslista(alikansio)
    return lista
