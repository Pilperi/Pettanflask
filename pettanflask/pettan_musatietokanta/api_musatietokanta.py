'''
Musapuolen API-funktiot.
'''
import os
import json
from flask import make_response, jsonify, abort, send_from_directory, request
from flask_restful import Resource, reqparse

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import Hakukriteerit

import pettanflask.pettan_musatietokanta as musavak
from pettanflask.pettan_musatietokanta import funktiot_musatietokanta as musapet


#-------------------------------------------------------------------------------
# Pyyntöjen ja argumenttien määritelmät

# Pyyntönimet:
PYYNTOMAP_HAKU = {
    "listaa_tietokannat": musapet.listaa_tietokannat,
    "anna_tietokanta": musapet.anna_tietokanta,
    "etsi_tietokannasta": musapet.etsi_tietokannasta,
    "anna_latauslista": musapet.anna_latauslista,
    }
# Argumenttien datatyypit
ARGUMENTTITYYPIT = {
    "listaa_tietokannat": [type(None)],
    "anna_tietokanta": [str],
    "etsi_tietokannasta": [str, dict],
    "anna_latauslista": [dict],
    }
# Stringimuotoilu
AGUMENTTIKUVAUKSET = {
    pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
    for pyynto,tyyppilista in ARGUMENTTITYYPIT.items()
    }

#-------------------------------------------------------------------------------
# Parserifunktiot

# Hakutoiminnot
parser_tietokantahaku = reqparse.RequestParser()
parser_tietokantahaku.add_argument(
    name="TOIMENPIDE",
    type=str,
    help=f"Suoritettava toimenpide (str). Vaihtoehdot: {list(PYYNTOMAP_HAKU)}",
    choices=list(PYYNTOMAP_HAKU),
    required=True,
    location="json",
    )
parser_tietokantahaku.add_argument(
    name="ARGUMENTIT",
    #type=list,
    action="append",
    required=True,
    default=[None]
    )

# Biisidatan toimitus
parser_biisilataus = reqparse.RequestParser()
parser_biisilataus.add_argument(
    name="polku",
    type=str,
    help="Ladattavan biisin kohde, formaatilla /tietokannan_nimi/loppu/pol.ku"
    )

#-------------------------------------------------------------------------------


class Musatietokanta_haku(Resource):
    '''Hae musatietokantojen dataa.

    Ottaa sisään pyynnön + argumenttilista
    ja muodostaa näiden perusteella vastauksen + virheen
    diktinä
    {
    "VASTAUS": str/dict/list/None,
    "VIRHE": str/None
    }
    Vastauksen sisältö riippuu pyynnöstä, epäonnistuessa aina None.
    '''
    def get(self):
        '''GET kertoo mitä voi tehdä ja miten.'''
        paluuarvo = {
            "VASTAUS": {
                pyynto: [tyyppi.__name__ for tyyppi in tyyppilista]
                for pyynto,tyyppilista in ARGUMENTTITYYPIT.items()
                },
            "VIRHE": None
            }
        return make_response(jsonify(paluuarvo), 200)

    def post(self):
        '''POST suorittaa asianmukaisen hakutoimenpiteen:

        listaa_tietokannat()
            Antaa listan tietokantanimistä

        anna_tietokanta(str)
            Antaa annetun nimisen tietokannan

        etsi_tietokannasta(str, dict)
            Suorittaa määritellyn haun määritynnimiseen tietokantaan

        anna_latauslista(dict)
            Muuntaa annetun tiedostopuun listaksi latauskelpoisia polkuja
        '''
        args = parser_tietokantahaku.parse_args()
        toimenpide = args.get("TOIMENPIDE")
        # Parseri ei osaa hoitaa sisäkkäisiä tyyppitarkastuksia,
        # lue rautalangalla (läh. dictit taipui str(dict))
        argumentit = request.get_json(force=True)["ARGUMENTIT"]
        if not isinstance(argumentit, list):
            argumentit = [argumentit]
        # Toimenpide määrittelemätön tai tuntematon
        if toimenpide not in PYYNTOMAP_HAKU:
            paluuarvo = {
                "VASTAUS": None,
                "VIRHE": f"Ei toimintoa pyynnölle TOIMENPIDE={toimenpide}"
                }
            return make_response(jsonify(paluuarvo), 400)
        # Tarkista sisäänmenoargumenttien määrä
        if len(argumentit) != len(ARGUMENTTITYYPIT[toimenpide]):
            paluuarvo = {
                "VASTAUS": None,
                "VIRHE": (
                    f"Toimenpide {toimenpide} vaatii"
                    +f" {len(ARGUMENTTITYYPIT[toimenpide])} argumenttia,"
                    +f" saatiin {len(argumentit)}."
                    )
                }
            return make_response(jsonify(paluuarvo), 400)
        # Tarkista sisäänmenoargumenttien laatu
        if not all(isinstance(argumentit[i], ARGUMENTTITYYPIT[toimenpide][i])
            for i in range(len(argumentit))
            ):
            paluuarvo = {
                "VASTAUS": None,
                "VIRHE": (
                    f"Toimenpiteen {toimenpide} argumentit ovat"
                    +f" {AGUMENTTIKUVAUKSET[toimenpide]}"
                    +f", saatiin {[type(arg).__name__ for arg in argumentit]}."
                    )
                }
            return make_response(jsonify(paluuarvo), 400)
        # Suorita kutsu. Toimenpidefunktio huolehtii vastauksen kasaamisesta
        return PYYNTOMAP_HAKU[toimenpide](*argumentit)


class Musatietokanta_lataus(Resource):
    '''Lataa yksittäinen biisi.'''
    def get(self, polku=None):
        '''Hae biisi polun takaa.

        Hae biisi polun perusteella, juurena tietokannan nimi
        ja sen jälkeen tiedostopolku vastaavan tiedostopuun alla.
        Jos sisäänmenoargumenttia ei ole annettu, yritä lukea polku datakentistä.

        Sisään
        ------
        polku : str tai None
            Tiedostopolku /tietokannan_nimi/loppupolku/tiedos.to -formaatilla
            Polun voi toimittaa joko URL:in kautta tai datakentässä.

        Ulos
        ----
        binääriä tai 404
            Jos biisi löytyy polun takaa ja se saadaan luettua, biisin sisältö.
            Muutoin virhekoodi-abortti.
        '''
        if not isinstance(polku, str):
            args = parser_biisilataus.parse_args()
            polku = args.get("polku")
        if not isinstance(polku, str):
            abort(400)
        # Katso mikä on polun juuri
        splitattu = os.path.split(polku)
        juuri = os.path.dirname(polku)
        while splitattu[1]:
            juuri = splitattu[1]
            splitattu = os.path.split(splitattu[0])
        # Hae "juuren" todellinen polku
        oikeapolku = musavak.PAIKALLISPOLUT.get(juuri)
        if oikeapolku is None or len(polku) <= len(juuri)+1:
            abort(404)
        alipolku = polku[len(juuri)+1:]
        try:
            return send_from_directory(oikeapolku, alipolku)
        except (FileNotFoundError, PermissionError) as err:
            if isinstance(err, FileNotFoundError):
                abort(404)
            else:
                abort(403)
