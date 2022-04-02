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
    vastaus = req.post(IP+"aktivoi_moodi", json={"MOODI":"testi"})
except req.exceptions.ConnectionError:
    print(f"Palvelin ei pyöri osoitteessa {IP}, ei voida testata...")
    assert False
assert vastaus.status_code == 200
assert "testi" in vastaus.text


def test_haku_huonot_data_avaimet_parseri():
    '''
    Katso että palauttaa oikean virhekoodin kun sisäänmenodata on killissä.
    '''
    # Pyynnön avainsanat väärin -> message
    args = {"VÄÄRÄ": "anna_tietokanta", "NIMI": ["testi-1"]}
    # Kokonaan ilman json-kenttää
    vastaus = req.post(IP+"musatietokanta")
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message")
    assert "VASTAUS" not in vastaus_json
    # Huonoilla avainsanoilla:
    vastaus = req.post(IP+"musatietokanta", json=args)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message")
    assert "VASTAUS" not in vastaus_json


def test_haku_huonot_toimenpiteet_parseri():
    '''
    Katso että TOIMENPIDE-kenttä vaaditaan oikein.
    '''
    # Puuttuu kokonaan
    vastaus = req.post(IP+"musatietokanta", json={"ARGUMENTIT": ["testi-1"]})
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message")
    assert "VASTAUS" not in vastaus_json
    # Ei tunnettu
    vastaus = req.post(IP+"musatietokanta", json={"TOIMENPIDE": "väärä", "ARGUMENTIT": ["testi-1"]})
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message")
    assert "VASTAUS" not in vastaus_json
    # Datatyypit killissä
    vastaus = req.post(IP+"musatietokanta", json={"TOIMENPIDE":1, "ARGUMENTIT":["testi-1"]})
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message")
    assert "VASTAUS" not in vastaus_json


def test_haku_huonot_argumentit_parseri():
    '''
    Katso että argumentit vaaditaan aina.
    '''
    # Argumenttikenttä puuttuu
    vastaus = req.post(IP+"musatietokanta", json={"TOIMENPIDE": "anna_tietokanta"})
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message")
    assert "VASTAUS" not in vastaus_json


def test_haku_get():
    '''
    Testaa että GET antaa pyyntödokumentaation.
    '''
    # Standardi kutsu
    vastaus = req.get(IP+"musatietokanta")
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "VIRHE" in vastaus_json
    assert vastaus_json.get("VIRHE") is None
    assert "VASTAUS" in vastaus_json
    assert vastaus_json.get("VASTAUS") == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }
    # Argumentit saa olla messissä kun ei niillä tehdä mitään
    vastaus = req.get(IP+"musatietokanta", json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT":["testi-1"]})
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "VIRHE" in vastaus_json
    assert vastaus_json.get("VIRHE") is None
    assert "VASTAUS" in vastaus_json
    assert vastaus_json.get("VASTAUS") == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }
    # Myös ihan missä muodossa sattuu
    vastaus = req.get(IP+"musatietokanta", json={"VÄÄRÄ": 1, "ARVO": 2})
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "VIRHE" in vastaus_json
    assert vastaus_json.get("VIRHE") is None
    assert "VASTAUS" in vastaus_json
    assert vastaus_json.get("VASTAUS") == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }


def test_haku_listaa_tietokannat():
    '''
    Käytettävissä olevat tietokannat listautuu oikein.
    '''
    pyynto = {"TOIMENPIDE": "listaa_tietokannat", "ARGUMENTIT": [None]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("message") is None
    assert "VIRHE" in vastaus_json
    assert vastaus_json.get("VIRHE") is None
    assert isinstance(vastaus_json.get("VASTAUS"), list)
    for tietokanta in musavak.TIETOKANNAT:
        assert tietokanta in vastaus_json.get("VASTAUS")


def test_anna_tietokanta_huonot_agumentit():
    '''
    Tietokanta-JSONin lataus ei toimi jos pyynnöt on tyhmiä.
    '''
    # Väärä datatyyppi
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": None}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VASTAUS"] is None
    assert vastaus_json["VIRHE"]
    # Väärä määrä argumentteja
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["None", "None"]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VASTAUS"] is None
    assert vastaus_json["VIRHE"]
    # Ei löydy
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["None"]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 404
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VASTAUS"] is None
    assert vastaus_json["VIRHE"]


def test_anna_tietokanta():
    '''
    Anna tietokanta nimen perusteella.
    '''
    # Ykkössetti
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["testi-1"]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"] is not None
    assert vastaus_json["VASTAUS"] == musavak.BIISIDIKTIT["testi-1"]
    # Kakkossetti
    pyynto = {"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["testi-2"]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"] is not None
    assert vastaus_json["VASTAUS"] == musavak.BIISIDIKTIT["testi-2"]


def test_etsi_tietokannasta_huonot_argumentit():
    '''
    Etsi dataa tietokannasta, katso että feilaa odotetusti.
    '''
    tietokanta = "testi-1"
    haku = {"artistissa": ["0"]}
    # Väärä määrä argumentteja
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"]
    assert vastaus_json["VASTAUS"] is None
    # Oikea määrä argumentteja mutta väärää datatyyppiä
    # Molemmat
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [None, None]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"]
    assert vastaus_json["VASTAUS"] is None
    # eka
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [None, haku]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"]
    assert vastaus_json["VASTAUS"] is None
    # toka
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta, None]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"]
    assert vastaus_json["VASTAUS"] is None
    # Ei löydy tietokantaa
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": ["eiole", haku]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 404
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"]
    assert vastaus_json["VASTAUS"] is None


def test_etsi_tietokannasta_onnistuva():
    '''
    Etsi dataa tietokannasta, katso että onnistuu.
    '''
    tietokanta = "testi-1"
    haku = {"artistissa": ["0"]} # kaikki parilliset
    pyynto = {"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta, haku]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert "message" not in vastaus_json
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"]
    puudikti = vastaus_json["VASTAUS"]
    # Juuri: 0.mp3
    assert puudikti["kansio"] == tietokanta
    assert len(puudikti["tiedostot"]) == 1
    assert puudikti["tiedostot"][0]["tiedostonimi"] == "0.mp3"
    # Kansio 2: 2.mp3
    assert len(puudikti["alikansiot"]) == 1
    assert len(puudikti["alikansiot"][0]["tiedostot"]) == 1
    assert puudikti["alikansiot"][0]["tiedostot"][0]["tiedostonimi"] == "2.mp3"
    # Kansio 3-4: 4.mp3
    assert len(puudikti["alikansiot"][0]["alikansiot"]) == 1
    assert len(puudikti["alikansiot"][0]["alikansiot"][0]["tiedostot"]) == 1
    assert puudikti["alikansiot"][0]["alikansiot"][0]["tiedostot"][0]["tiedostonimi"] == "4.mp3"


def test_anna_latauslista_huonot_argumentit():
    '''
    Testaa että tulee oikeat virheet kun yritetään tehdä tyhmästi.
    '''
    # Väärä määrä dataa
    pyynto = {"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [{1:2}, {3:4}]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("VIRHE")
    assert vastaus_json["VASTAUS"] is None
    # Oikea määrä mutta väärää datatyyppiä
    pyynto = {"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [1]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 400
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json.get("VIRHE")
    assert vastaus_json["VASTAUS"] is None
    # Oikeaa datatyyppiä mutta paska puu
    pyynto = {"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [{1:2}]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"] == []


def test_anna_latauslista():
    '''
    Testaa että saadaan odotetut listat.
    '''
    # Ykköstesti (kaikki biisit) tulee odotetusti
    dikti_1 = musavak.BIISIDIKTIT["testi-1"]
    odotettu = [
        "testi-1/0.mp3",
        "testi-1/1/1.mp3",
        "testi-1/2/2.mp3",
        "testi-1/2/3-4/3.mp3",
        "testi-1/2/3-4/4.mp3",
        ]
    pyynto = {"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [dikti_1]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"]
    for polku in odotettu:
        assert polku in vastaus_json["VASTAUS"]
    # Karsittu versio
    dikti_1b = musavak.BIISIDIKTIT["testi-1"]["alikansiot"][1]
    odotettu = [
        "2/2.mp3",
        "2/3-4/3.mp3",
        "2/3-4/4.mp3",
        ]
    ei_odotettu = [
        "testi-1/0.mp3",
        "testi-1/1/1.mp3",
        ]
    pyynto = {"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [dikti_1b]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"]
    for polku in odotettu:
        assert polku in vastaus_json["VASTAUS"]
    for polku in ei_odotettu:
        assert polku not in vastaus_json["VASTAUS"]
    # Kakkosdikti antaa listan ml. tiedostot joita ei ole
    dikti_2 = musavak.BIISIDIKTIT["testi-2"]
    odotettu = [
        "testi-2/0.mp3",
        "testi-2/1/1.mp3",
        "testi-2/2/2.mp3",
        "testi-2/2/3-4/3.mp3",
        "testi-2/2/3-4/4.mp3",
        ]
    pyynto = {"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [dikti_2]}
    vastaus = req.post(IP+"musatietokanta", json=pyynto)
    assert vastaus.status_code == 200
    vastaus_json = vastaus.json()
    print(vastaus_json)
    assert vastaus_json["VIRHE"] is None
    assert vastaus_json["VASTAUS"]
    for polku in odotettu:
        assert polku in vastaus_json["VASTAUS"]


def test_musatietokanta_lataus_onnistuva_args():
    '''
    Katso että olemassaolevat tiedostot saadaan ladattua toimivasti argumenteilla.
    '''
    polut = [
        "testi-1/0.mp3",
        "testi-1/1/1.mp3",
        "testi-1/2/2.mp3",
        "testi-1/2/3-4/3.mp3",
        "testi-1/2/3-4/4.mp3",
        ]
    for biisinumero,polku in enumerate(polut):
        print(polku)
        pyynto = {"polku": polku}
        vastaus = req.get(IP+"musatietokanta/biisi", json=pyynto)
        vastaus_data = vastaus.content
        print(vastaus_data)
        assert vastaus.status_code == 200
        assert int(vastaus_data) == biisinumero


def test_musatietokanta_lataus_onnistuva_polku():
    '''
    Katso että olemassaolevat tiedostot saadaan ladattua toimivasti argumenteilla.
    '''
    polut = [
        "testi-1/0.mp3",
        "testi-1/1/1.mp3",
        "testi-1/2/2.mp3",
        "testi-1/2/3-4/3.mp3",
        "testi-1/2/3-4/4.mp3",
        ]
    for biisinumero,polku in enumerate(polut):
        print(polku)
        pyynto = {"polku": polku}
        vastaus = req.get(IP+f"musatietokanta/biisi/{polku}")
        vastaus_data = vastaus.content
        print(vastaus_data)
        assert vastaus.status_code == 200
        assert int(vastaus_data) == biisinumero


def test_musatietokanta_lataus_eiole():
    '''
    Katso että puuttuvat polut antavat 404
    '''
    polut = [
        "testi-2/0.mp3",
        "testi-2/1/1.mp3",
        "testi-2/2/2.mp3",
        "testi-2/2/3-4/3.mp3",
        "testi-2/2/3-4/4.mp3",
        ]
    for biisinumero,polku in enumerate(polut):
        print(polku)
        pyynto = {"polku": polku}
        vastaus = req.get(IP+f"musatietokanta/biisi/{polku}")
        # Ei pitäisi olla
        if biisinumero%2:
            assert vastaus.status_code == 404
        else:
            vastaus_data = vastaus.content
            print(vastaus_data)
            assert vastaus.status_code == 200
            assert int(vastaus_data) == biisinumero

def test_palauta_normitilaan():
    vastaus = req.post(IP+"aktivoi_moodi", json={"MOODI":"normaali"})
    assert vastaus.status_code == 200
    assert "normaali" in vastaus.text
