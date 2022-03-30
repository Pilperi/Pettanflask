'''
Testaa musatietokantasetit main-puolelta.
Palvelimen tulee pyöriä paikallisesti testien ajan,
jotta juttelufunktioita voi testata.
'''
import json
import requests as req
from pettanflask import pettan_musatietokanta as musapettan

from . import IP, INI

try:
    r = req.get(IP)
except req.exceptions.ConnectionError:
    print(f"Palvelin ei pyöri osoitteessa {IP}, ei voida testata...")
    assert False
assert r.status_code == 200
print("Palvelin pyörii.")

musapettan.lue_asetukset_tiedostosta(INI, "testi")

def test_juuri_huonokutsu():
    '''
    Katso että palauttaa oikean virhekoodin väärillä TOIMENPIDE-argumenteilla.
    '''
    args = {"TOIMENPIDE": "eiole", "ARGUMENTIT": "eiole"}
    # Ilman json-kenttää
    r = req.post(IP+"musatietokanta")
    assert r.status_code == 400
    # Ei-dictillä json-kentän datalla
    r = req.post(IP+"musatietokanta", json={1:2})
    assert r.status_code == 400
    j = r.json()
    assert j.get("VIRHE")
    # Huonolla funktionimellä
    r = req.post(IP+"musatietokanta", json=args)
    assert r.status_code == 400
    j = r.json()
    assert j.get("message") # väärällä datatyypillä virheviesti


def test_musatietokanta_tietokannat():
    '''Testaa että musatietokantapuolen tietokantahakujuttu toimii.'''
