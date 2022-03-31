'''
Testaa musatietokantasetit main-puolelta.
Palvelimen tulee pyöriä paikallisesti testien ajan,
jotta juttelufunktioita voi testata.
'''
import json
import requests as req
from pettanflask import pettan_musatietokanta as musavak
from pettanflask.pettan_musatietokanta import api_musatietokanta as musa_api

from . import IP, INI

try:
    r = req.get(IP)
except req.exceptions.ConnectionError:
    print(f"Palvelin ei pyöri osoitteessa {IP}, ei voida testata...")
    assert False
assert r.status_code == 200
print("Palvelin pyörii.")

musavak.lue_asetukset_tiedostosta(INI, "testi")


def test_haku_huonot_data_avaimet():
    '''Katso että palauttaa oikean virhekoodin kun sisäänmenodata on killissä.'''
    # Pyynnön avainsanat väärin -> message
    args = {"VÄÄRÄ": "anna_tietokanta", "NIMI": ["testi-1"]}
    # Kokonaan ilman json-kenttää
    r = req.post(IP+"musatietokanta")
    assert r.status_code == 400
    j = r.json()
    assert j.get("message")
    assert j.get("VASTAUS") is None
    # Huonoilla avainsanoilla:
    r = req.post(IP+"musatietokanta", json=args)
    assert r.status_code == 400
    j = r.json()
    assert j.get("message")
    assert j.get("VASTAUS") is None


def test_haku_huonot_toimenpiteet():
    '''Katso että TOIMENPIDE-kenttä vaaditaan oikein'''
    # Puuttuu kokonaan
    r = req.post(IP+"musatietokanta", json={"ARGUMENTIT": ["testi-1"]})
    assert r.status_code == 400
    j = r.json()
    assert j.get("message")
    assert j.get("VASTAUS") is None
    # Ei tunnettu
    r = req.post(IP+"musatietokanta", json={"TOIMENPIDE": "väärä", "ARGUMENTIT": ["testi-1"]})
    assert r.status_code == 400
    j = r.json()
    assert j.get("message")
    assert j.get("VASTAUS") is None
    # Datatyypit killissä
    r = req.post(IP+"musatietokanta", json={"TOIMENPIDE":1, "ARGUMENTIT":["testi-1"]})
    assert r.status_code == 400
    j = r.json()
    assert j.get("message")
    assert j.get("VASTAUS") is None


def test_haku_huonot_argumentit():
    '''Katso että argumentit vaaditaan aina.'''
    # Argumenttikenttä puuttuu
    r = req.post(IP+"musatietokanta", json={"TOIMENPIDE": "anna_tietokanta"})
    assert r.status_code == 400
    j = r.json()
    assert j.get("message")


def test_haku_get():
    '''Testaa että GET antaa pyyntödokumentaation'''
    # Standardi kutsu
    r = req.get(IP+"musatietokanta")
    assert r.status_code == 200
    j = r.json()
    assert "VIRHE" in j
    assert j.get("VIRHE") is None
    assert "VASTAUS" in j
    assert j.get("VASTAUS") == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }
    # Argumentit saa olla messissä kun ei niillä tehdä mitään
    r = req.get(IP+"musatietokanta", json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT":["testi-1"]})
    assert r.status_code == 200
    j = r.json()
    assert "VIRHE" in j
    assert j.get("VIRHE") is None
    assert "VASTAUS" in j
    assert j.get("VASTAUS") == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }
