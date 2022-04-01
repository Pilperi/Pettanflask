'''
Testaa musatietokantasetit main-puolelta.
Palvelimen tulee pyöriä paikallisesti testien ajan,
jotta juttelufunktioita voi testata.
'''
import json
import requests as req
from pettanflask import pettan_musatietokanta as musavak
from pettanflask.pettan_musatietokanta import api_musatietokanta as musa_api

from . import IP

try:
    r = req.get(IP)
except req.exceptions.ConnectionError:
    print(f"Palvelin ei pyöri osoitteessa {IP}, ei voida testata...")
    assert False
assert r.status_code == 200


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


def test_haku_listaa_tietokannat():
    '''Käytettävissä olevat tietokannat listautuu oikein.'''
    pyynto = {"TOIMENPIDE": "listaa_tietokannat", "ARGUMENTIT": [None]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 200
    j = r.json()
    assert j.get("message") is None
    assert j.get("VIRHE") is None
    assert "VIRHE" in j
    assert isinstance(j.get("VASTAUS"), list)
    for tietokanta in musavak.TIETOKANNAT:
        assert tietokanta in j.get("VASTAUS")


def test_anna_tietokanta_huonot_agumentit():
    '''Tietokanta-JSONin lataus ei toimi jos pyynnöt on tyhmiä'''
    # Väärä datatyyppi
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": None}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 400
    j = r.json()
    assert "message" not in j
    assert j["VASTAUS"] is None
    assert j["VIRHE"]
    # Väärä määrä argumentteja
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["None", "None"]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 400
    j = r.json()
    assert "message" not in j
    assert j["VASTAUS"] is None
    assert j["VIRHE"]
    # Ei löydy
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["None"]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 404
    j = r.json()
    assert "message" not in j
    assert j["VASTAUS"] is None
    assert j["VIRHE"]


def test_anna_tietokanta():
    '''Anna tietokanta nimen perusteella.'''
    # Ykkössetti
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["testi-1"]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 200
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"] is None
    assert j["VASTAUS"] is not None
    assert j["VASTAUS"] == musavak.BIISIDIKTIT["testi-1"]
    # Kakkossetti
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["testi-2"]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 200
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"] is None
    assert j["VASTAUS"] is not None
    assert j["VASTAUS"] == musavak.BIISIDIKTIT["testi-2"]


def test_etsi_tietokannasta_huonot_argumentit():
    '''Etsi dataa tietokannasta'''
    tietokanta = "testi-1"
    haku = {"artistissa": ["0"]}
    # Väärä määrä argumentteja
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 400
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"]
    assert j["VASTAUS"] is None
    # Oikea määrä argumentteja mutta väärää datatyyppiä
    # Molemmat
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [None, None]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 400
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"]
    assert j["VASTAUS"] is None
    # eka
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [None, haku]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 400
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"]
    assert j["VASTAUS"] is None
    # toka
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta, None]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 400
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"]
    assert j["VASTAUS"] is None
    # Ei löydy tietokantaa
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": ["eiole", haku]}
    r = req.post(IP+"musatietokanta", json=pyynto)
    assert r.status_code == 404
    j = r.json()
    assert "message" not in j
    assert j["VIRHE"]
    assert j["VASTAUS"] is None
