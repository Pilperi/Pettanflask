'''
Testaa musatietokantasetit main-puolelta.
Palvelimen tulee pyöriä paikallisesti testien ajan,
jotta juttelufunktioita voi testata.
'''
import json
import time
import threading
import requests as req

from tiedostohallinta.class_http import Vastaus

from pettanflask import main as pettanmain
from pettanflask import api_main
from pettanflask import pettan_musatietokanta as musavak
from pettanflask.pettan_musatietokanta import api_musatietokanta as musa_api

from . import IP

startattiin_manuaalisesti = False
thread = threading.Thread(target=pettanmain.app.run)

def test_palvelin_kaynnissa():
    '''
    Tarkista pyöriikö palvelin. Jos ei, käynnistä.
    Laita testien ajaksi testimoodiin.
    '''
    global startattiin_manuaalisesti
    try:
        vastaus = req.post(IP+"aktivoi_moodi",
            json={"MOODI":"testi"})
        assert vastaus.status_code == 200
        assert "testi" in vastaus.text
        print(f"Palvelin pyörii osoitteessa {IP}")
    except req.exceptions.ConnectionError:
        print(f"Palvelin ei pyöri osoitteessa {IP}, yritetään aktivoida...")
        startattiin_manuaalisesti = True
        thread.start()
        time.sleep(1)
        try:
            vastaus = req.post(IP+"aktivoi_moodi",
                json={"MOODI":"testi"})
        except req.exceptions.ConnectionError:
            print(f"Palvelin ei pyöri osoitteessa {IP}, ei saada ajettua testejä...")
            assert False

def test_haku_huonot_data_avaimet_parseri():
    '''
    Katso että palauttaa oikean virhekoodin kun sisäänmenodata on killissä.
    '''
    # Kokonaan ilman json-kenttää
    vastaus = Vastaus(req.post(IP+"musatietokanta"))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe
    # Huonoilla avainsanoilla:
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"VÄÄRÄ": "anna_tietokanta", "NIMI": ["testi-1"]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe


def test_haku_huonot_toimenpiteet_parseri():
    '''
    Katso että TOIMENPIDE-kenttä vaaditaan oikein.
    '''
    # Puuttuu kokonaan
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"ARGUMENTIT": ["testi-1"]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe
    # Ei tunnettu
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "väärä", "ARGUMENTIT": ["testi-1"]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe
    # Datatyypit killissä
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE":1, "ARGUMENTIT":["testi-1"]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe


def test_haku_huonot_argumentit_parseri():
    '''
    Katso että argumentit vaaditaan aina.
    '''
    # Argumenttikenttä puuttuu
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_tietokanta"}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe


def test_haku_get():
    '''
    Testaa että GET antaa pyyntödokumentaation.
    '''
    # Standardi kutsu
    vastaus = Vastaus(req.get(IP+"musatietokanta"))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.vastaus == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }
    assert vastaus.virhe is None
    # Argumentit saa olla messissä kun ei niillä tehdä mitään
    vastaus = Vastaus(req.get(IP+"musatietokanta", json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT":["testi-1"]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }
    # Myös ihan missä muodossa sattuu
    vastaus = Vastaus(req.get(IP+"musatietokanta", json={"VÄÄRÄ": 1, "ARVO": 2}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus == {
        pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
        for pyynto,tyyppilista in musa_api.ARGUMENTTITYYPIT.items()
        }


def test_haku_listaa_tietokannat():
    '''
    Käytettävissä olevat tietokannat listautuu oikein.
    '''
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "listaa_tietokannat", "ARGUMENTIT": [None]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert isinstance(vastaus.vastaus, list)
    for tietokanta in musavak.TIETOKANNAT:
        assert tietokanta in vastaus.vastaus


def test_anna_tietokanta_huonot_agumentit():
    '''
    Tietokanta-JSONin lataus ei toimi jos pyynnöt on tyhmiä.
    '''
    # Väärä datatyyppi
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": None}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe
    # Väärä määrä argumentteja
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["None", "None"]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.vastaus is None
    assert vastaus.virhe
    # Ei löydy
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["None"]}))
    print(vastaus.json())
    assert vastaus.koodi == 404
    assert vastaus.vastaus is None
    assert vastaus.virhe


def test_anna_tietokanta():
    '''
    Anna tietokanta nimen perusteella.
    '''
    # Ykkössetti
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["testi-1"]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus == musavak.BIISIDIKTIT["testi-1"]
    # Kakkossetti
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_tietokanta", "ARGUMENTIT": ["testi-2"]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus == musavak.BIISIDIKTIT["testi-2"]


def test_etsi_tietokannasta_huonot_argumentit():
    '''
    Etsi dataa tietokannasta, katso että feilaa odotetusti.
    '''
    tietokanta = "testi-1"
    haku = {"artistissa": ["0"]}
    # Väärä määrä argumentteja
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.virhe
    assert vastaus.vastaus is None
    # Oikea määrä argumentteja mutta väärää datatyyppiä
    # Molemmat
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [None, None]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.virhe
    assert vastaus.vastaus is None
    # eka
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [None, haku]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.virhe
    assert vastaus.vastaus is None
    # toka
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta, None]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.virhe
    assert vastaus.vastaus is None
    # Ei löydy tietokantaa
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": ["eiole", haku]}))
    print(vastaus.json())
    assert vastaus.koodi == 404
    assert vastaus.virhe
    assert vastaus.vastaus is None


def test_etsi_tietokannasta_onnistuva():
    '''
    Etsi dataa tietokannasta, katso että onnistuu.
    '''
    tietokanta = "testi-1"
    haku = {"artistissa": ["0"]} # kaikki parilliset
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "etsi_tietokannasta", "ARGUMENTIT": [tietokanta, haku]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus
    puudikti = vastaus.vastaus
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
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [{1:2}, {3:4}]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.virhe
    assert vastaus.vastaus is None
    # Oikea määrä mutta väärää datatyyppiä
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [1]}))
    print(vastaus.json())
    assert vastaus.koodi == 400
    assert vastaus.virhe
    assert vastaus.vastaus is None
    # Oikeaa datatyyppiä mutta paska puu
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [{1:2}]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus == []


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
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [dikti_1]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus
    for polku in odotettu:
        assert polku in vastaus.vastaus
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
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [dikti_1b]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus
    for polku in odotettu:
        assert polku in vastaus.vastaus
    for polku in ei_odotettu:
        assert polku not in vastaus.vastaus
    # Kakkosdikti antaa listan ml. tiedostot joita ei ole
    dikti_2 = musavak.BIISIDIKTIT["testi-2"]
    odotettu = [
        "testi-2/0.mp3",
        "testi-2/1/1.mp3",
        "testi-2/2/2.mp3",
        "testi-2/2/3-4/3.mp3",
        "testi-2/2/3-4/4.mp3",
        ]
    vastaus = Vastaus(req.post(IP+"musatietokanta",
        json={"TOIMENPIDE": "anna_latauslista", "ARGUMENTIT": [dikti_2]}))
    print(vastaus.json())
    assert vastaus.koodi == 200
    assert vastaus.virhe is None
    assert vastaus.vastaus
    for polku in odotettu:
        assert polku in vastaus.vastaus


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
    # Tapa jos käynnistettiin ite
    if startattiin_manuaalisesti:
        vastaus = req.get(IP+"kuole")
        assert vastaus.status_code == 200
