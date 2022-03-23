'''
Pettanin flaskipalvelimen pääscripti.
Hoitaa juttelun eli käytännössä
kutsuu oikeaa funktiota pyyntöargumentin
perusteella.
'''

import os
from flask import (
    Flask, send_from_directory, abort, request,
    redirect, url_for, make_response, jsonify
    )

import pettanflask as vakiot
import pettanflask.html as htmlvak
from pettanflask.html import funktiot_html as htmlpet
from pettanflask import musatietokanta as musavak
from pettanflask.musatietokanta import funktiot_biisitietokannat as musapet

app = Flask(__name__)


#-------------------------------------------------------------------------------
# Flaskin ittensä setit (tappo ymv)


@app.route("/", methods=['GET'])
def moi_maailma():
 return("Moikka maailma")


@app.route("/kuole")
def lopeta():
    '''
    Tapa flaskirosessi.
    '''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Hyvästi maailma"


#-------------------------------------------------------------------------------
# Kuvaselailujutut


@app.route("/hauskatkuvat/<path:kansio>",
    defaults={"hakutermi": None, "sivu": 0})
@app.route("/hauskatkuvat/<path:kansio>&etsi=<string:hakutermi>",
    defaults={"sivu": 0})
@app.route("/hauskatkuvat/<path:kansio>&s=<int:sivu>",
    defaults={"hakutermi": None})
@app.route("/hauskatkuvat/<path:kansio>&etsi=<string:hakutermi>&s=<int:sivu>")
def kuvakansio(kansio, hakutermi, sivu):
    '''
    Näytä kansion kuvat ruudukkona.
    '''
    return htmlpet.luo_kuvaruudukko(kansio, hakutermi=hakutermi, sivu=sivu)


@app.route("/hauskatkuvat")
def kuvakansiot():
    '''
    Näytä kansion alikansiot linkkilistana.
    '''
    return htmlpet.hauskatkansiot()


@app.route("/thumb/<path:tiedostopolku>")
def thumbnaili(tiedostopolku):
    '''
    Palauta thumbnailin kuvadata.
    '''
    peruspolku = htmlvak.THUMBIKANSIO
    try:
        return send_from_directory(peruspolku, tiedostopolku)
    except FileNotFoundError:
        abort(404)


@app.route("/INTERNET/<path:alipolku>")
def hauskakuva(alipolku):
    '''
    Palauta kuvatiedosto INTERNET-kansiosta
    '''
    peruspolku = htmlvak.INTERNET
    try:
        return send_from_directory(peruspolku, alipolku)
    except FileNotFoundError:
        abort(404)


@app.route('/etsikuvaa', methods=['POST', 'GET'])
def etsikuvaa():
    if request.method == 'POST':
        kansio = request.form['kansio']
        termi = request.form['termi']
    else:
        kansio = request.args.get('kansio')
        termi = request.args.get('termi')
    return redirect(url_for('kuvakansio', kansio=kansio, hakutermi=termi))


#-------------------------------------------------------------------------------
# Musatietokantajutut

@app.route("/musatietokanta", methods=["PUT"])
def musatietokannat():
    '''Musatietokannan juttelufunktio.

    Lukee kutsudatasta mitä oikein olisi tarkoitus
    tehdä ja kutsuu asianmukaista funktiota.

    Sisään
    ------
    json-dikti
        Dikti missä kuvattu, mitä halutaan tehdä ja miten.
        Rakenteena {"TOIMENPIDE": str, "ARGUMENTIT": vaadittavat_parametrit}
        Mahdollisia TOIMENPIDE-argumentteja ovat:
        - "tietokannat" : kerro minkä nimisiä tietokantoja löytyy
            - argumentit: ei tarvii
        - "anna_tietokanta" : anna tietokanta nimen perusteella
            - argumentit : dict {"tietokanta": str, "artistipuuna": bool}
              missä "tietokanta" on tietokannan nimi
        - "etsi_tietokannasta" : etsi nimen mukaisesta tietokannasta asioita
            - argumentit : {"tietokanta": str, "hakudikti": dict, "artistipuuna: bool}
              missä "tietokanta" on tietokannan nimi
              ja "hakudikti" sisältää hakuparametrit.
        - "anna_latauslista" : anna lista latauspolkuja puun perusteella
            - argumentit : dict (tiedostopuu jota ollaan lataamassa)
        - "lataa_biisi" : anna tiedostopolun mukainen biisi
            - argumentit : str (tiedoston polku)

    Ulos
    ----
    json-dikti tai binääri
        Sisältää avaimet "VASTAUS" ja "VIRHE", missä
        vastauksen arvo riippuu siitä mitä ollaan pyydetty
        ja virhe on joko str tai None, str vain jos jokin kusi.
        Paluutyypit pyynnön mukaan:
        - tietokannat : [str]
        - anna_tietokanta : dict (tietokannan diktiversio)
        - etsi_tietokannasta : dict (tietokannan diktiversio)
        - anna_latauslista [str] (lista latauspolkuja)
       Poikkeuksena lataa_biisi, joka palauttaa onnistuessaan
       biisin binääridatana sekä vastauskoodin, ja epäonnistuessaan
       joko samanlaisen diktin tai pelkän 404 jos biisiä ei ole.

    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    data = request.get_json(force=True)
    if not isinstance(data, dict):
        errmsg = (
            "Anna JSON-data diktinä plz"
            +f" (on: {type(data)})"
            )
        print(errmsg)
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 400)

    # Mäppää pyyntötyypit oikeisiin funktioihin
    pyyntomap = {
        "tietokannat": listaa_tietokannat,
        "anna_tietokanta": anna_tietokanta,
        "etsi_tietokannasta": etsi_tietokannasta,
        "anna_latauslista": anna_latauslista,
        "lataa_biisi": lataa_biisi,
        }
    pyynto = data.get("TOIMENPIDE")
    kutsufunktio = pyyntomap.get(pyynto)
    # Ei tunnettu pyyntö tai ei pyyntöä
    if kutsufunktio is None:
        errmsg = (
            f"TOIMENPIDE {pyynto} ei ole tunnettu."
            +" Mahdollisia arvoja ovat"
            +f" {[avain for avain in pyyntomap]}"
            )
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 400)
    # Muutoin suorita pyyntö.
    # Mahdolliset virheet sun muut hoidetaan funktiossa
    return kutsufunktio(data.get("ARGUMENTIT"))


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
        "VASTAUS": [nimi for nimi in musavak.BIISIPUUT],
        "VIRHE": None
        }
    return make_response(jsonify(paluuarvo), 200)

def anna_tietokanta(*args):
    '''Hae tietokantaa nimen perusteella.

    Sisään
    ------
    dict
        {
        "tietokanta": str
        "artistipuuna": bool
        }
        missä "tietokanta" on tietokannan nimi.
        Käytettävissä olevat vaihtoehdot saa kutsumalla
        /musatietokanta, se antaa listan nimistringejä.
        Valinnaisena bool-argumentti, joka jos on tosi
        niin paluuarvon puu on artistipuun muodossa tavanomaisen
        tiedostopolkupuun sijaan. Oletuksena on tiedostopolkupuu.
        Se tosin on vasta työn alla, joten tällä hetkellä
        sen laittaminen todeksi tekee vaan sen ettet saa kuin virheen.

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
    # Nimipyyntö uupuu kokonaan
    if not len(args) or args[0] is None:
        errmsg = "Pyydettävän tietokannan nimi puuttuu."
        paluuarvo["VIRHE"] = errmsg
    parametrit = args[0]
    # Sisäänmenopyyntö väärää sorttia
    if not isinstance(parametrit, dict):
        errmsg = (
            "Parametrien tulee olla {\"tietokanta\": str}."
            +" tai {\"tietokanta\": str, \"artistipuuna\": bool}"
            +f" (on: {type(parametrit)})"
            )
        paluuarvo["VIRHE"] = errmsg
    # Huono avaimet diktissä
    else:
        tietokannan_nimi = parametrit.get("tietokanta")
        if not isinstance(tietokannan_nimi, str):
            errmsg = (
                "Tietokannan nimen tulee olla str"
                +f" (on: {type(parametrit)})"
                )
            paluuarvo["VIRHE"] = errmsg
    # Jokin virhekoodi (standardeista) 400-sarjalaisista
    if paluuarvo.get("VIRHE"):
        return make_response(jsonify(paluuarvo), 400)

    # Ihajjust
    artistipuuna = parametrit.get("artistipuuna")
    if artistipuuna:
        errmsg = f"Artistipuuna palautusta ei ole vielä implementoitu lol"
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 400)
        puu = musavak.ARTISTIPUUT.get(tietokannan_nimi)
    else:
        puu = musavak.BIISIPUUT.get(tietokannan_nimi)
    # Ei löydy nimellä
    if puu is None:
        errmsg = f"Ei löydy tietokantaa nimeltä {tietokannan_nimi}."
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 404)
    paluuarvo["VASTAUS"] = puu.diktiksi()
    return make_response(jsonify(paluuarvo), 200)

def etsi_tietokannasta(*args):
    '''Suorita haku tietokannasta.

    Sisään
    ------
    dict
        {
        "tietokanta": str,
        "hakudikti": dict
        "artistipuuna": bool
        }
        missä "tietokanta" on tietokannan nimi mistä etsitään.
        Käytettävissä olevat vaihtoehdot saa kutsumalla
        /musatietokanta, se antaa listan nimistringejä.
        Hakudikti Hakukriteerit-luokan mukainen dikti.
        Valinnaisena bool-argumentti, joka jos on tosi
        niin paluuarvon puu on artistipuun muodossa tavanomaisen
        tiedostopolkupuun sijaan. Oletuksena on tiedostopolkupuu.
        Se tosin on vasta työn alla, joten tällä hetkellä
        sen laittaminen todeksi tekee vaan sen ettet saa kuin virheen.

    Ulos
    ----
    response
        Standardi vastaus, eli flaskin HTTP-JSON vastauskoodin kera.
        Diktiosiossa arvot {"VASTAUS": dict, "VIRHE": str tai None}
        missä vastauksena hakutulostietokannan (Tiedostopuu) diktiversio
        tai None jos tietokantaa ei löytynyt, ja virheen alla
        virhekuvatusstringi jos jokin mättää.
    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    # Nimipyyntö uupuu kokonaan
    if not len(args) or args[0] is None:
        errmsg = "Pyydettävän tietokannan nimi puuttuu."
        paluuarvo["VIRHE"] = errmsg
    parametrit = args[0]
    # Sisäänmenopyyntö väärää sorttia
    if not isinstance(parametrit, dict):
        errmsg = (
            "Parametrien tulee olla {\"tietokanta\": str}."
            +" tai {\"tietokanta\": str, \"artistipuuna\": bool}"
            +f" (on: {type(parametrit)})"
            )
        paluuarvo["VIRHE"] = errmsg
    # Huono avaimet diktissä
    tietokannan_nimi = parametrit.get("tietokanta")
    if not isinstance(tietokannan_nimi, str):
        errmsg = (
            "Tietokannan nimen tulee olla str"
            +f" (on: {type(parametrit)})"
            )
        paluuarvo["VIRHE"] = errmsg
    hakudikti = parametrit.get("hakudikti")
    # Hakudikti uupuu tai on outo
    if not isinstance(hakudikti, dict):
        errmsg = f"Hakudikti ei ole dikti laisinkaan ({type(hakudikti)})"
        paluuarvo["VIRHE"] = errmsg

    # Jokin virhekoodi (standardeista) 400-sarjalaisista
    if paluuarvo.get("VIRHE"):
        return make_response(jsonify(paluuarvo), 400)

    puu = musavak.BIISIPUUT.get(tietokannan_nimi)
    # Nimeä vastaavaa tietokantaa ei löydy
    if puu is None:
        errmsg = f"Ei löydy tietokantaa nimeltä {tietokannan_nimi}."
        paluuarvo["VIRHE"] = errmsg
        return make_response(jsonify(paluuarvo), 404)
    artistipuuna = parametrit.get("artistipuuna")
    paluuarvo = musapet.etsi_puusta(puu, hakudikti, artistipuuna)
    koodi = 200
    koodi *= 1+bool(paluuarvo.get("VIRHE")) # 400
    return make_response(jsonify(paluuarvo), koodi)

def anna_latauslista(*args):
    '''Anna latauspolut listana `lataa_biisi`-yhteensopivia str.

    Sisään
    ------
    dict
        Ladattava puu (Tiedostopuun diktiversio).

    Ulos
    ----
    response
        Standardi vastaus, eli flaskin HTTP-JSON vastauskoodin kera.
        Diktiosiossa arvot {"VASTAUS": [str] tai None, "VIRHE": str tai None}
        missä vastauksena on latauspolut stringeinä (tai None jos ei onnaa)
        ja virheen alla tiedot jos jokin meni pieleen.
    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    # Nimipyyntö uupuu kokonaan
    if not len(args) or args[0] is None:
        errmsg = "Ladattava tietokanta puuttuu."
        paluuarvo["VIRHE"] = errmsg
    puu = args[0]
    # Sisäänmenopyyntö väärää sorttia
    if not isinstance(puu, dict):
        errmsg = (
            "Ladattavan puun pitää olla Tietokannan diktiversio."
            +f" (on: {type(puu)})"
            )
        paluuarvo["VIRHE"] = errmsg
    # Jokin virhekoodi (standardeista) 400-sarjalaisista
    if paluuarvo.get("VIRHE"):
        return make_response(jsonify(paluuarvo), 400)
    # Laadi lista
    paluuarvo["VASTAUS"] = musapet.puun_latauslista(puu)
    return make_response(jsonify(paluuarvo), 200)

def lataa_biisi(*args):
    '''Lataa biisi tiedostopolusta.

    Sisään
    ------
    str
        Biisin tiedostopolku, s.e. juurisolmun kansionimenä
        on tietokannan nimi (eikä oikea tiedostopolku)

    Ulos
    ----
    response
        Vastaus on joko haluttu biisi binääridatana,
        tai jos jokin meni pieleen niin JSON jossa selitetty mikä mättää.
        Nämä on (vähemmän yllättäen) erotettavissa vastauskoodin perusteella,
        200 onnistuessa ja jotain muuta epäonnistuessa.
        Virhekuvaus on json-paluuarvon kentässä "VIRHE"
    '''
    paluuarvo = {
        "VASTAUS": None,
        "VIRHE": None
        }
    koodi = 200
    # Nimipyyntö uupuu kokonaan
    if not len(args) or args[0] is None:
        errmsg = "Ladattava tiedostopolku puuttuu."
        paluuarvo["VIRHE"] = errmsg
    polku = args[0]
    # Sisäänmenopyyntö väärää sorttia
    if not isinstance(polku, str):
        errmsg = (
            "Latauspolun tulee olla str."
            +f" (on: {type(puu)})"
            )
        paluuarvo["VIRHE"] = errmsg
    # Jokin virhekoodi (standardeista) 400-sarjalaisista
    if paluuarvo.get("VIRHE"):
        return make_response(jsonify(paluuarvo), 400)
    # Hae biisi
    splitattu = os.path.split(polku)
    juuri = os.path.dirname(polku)
    while splitattu[1]:
        juuri = splitattu[1]
        splitattu = os.path.split(splitattu[0])
    # Hae "juuren" todellinen polku
    oikeapolku = musavak.PAIKALLISPOLUT.get(juuri)
    if oikeapolku is None:
        errmsg = f"Tietokannalle {juuri} ei löytynyt paikallista polkua."
        paluuarvo["VIRHE"] = errmsg
        koodi = 404
    # polku rakenteella nimi/ali/polku/tiedos.to
    # eikä /nimi/ali/polku/tiedos.to
    if len(polku) <= len(juuri)+1:
        errmsg = f"Polku {polku} ei ole validi (ei kamaa {juuri} jälkeen)."
        paluuarvo["VIRHE"] = errmsg
        koodi = 400
    alipolku = polku[len(juuri)+1:]
    if not os.path.isfile(os.path.join(oikeapolku, alipolku)):
        errmsg = f"{alipolku} ei ole olemassaoleva tiedosto."
        paluuarvo["VIRHE"] = errmsg
        koodi = 404
    if paluuarvo.get("VIRHE"):
        return make_response(jsonify(paluuarvo), koodi)
    try:
        return send_from_directory(oikeapolku, alipolku)
    except FileNotFoundError:
        abort(404)
