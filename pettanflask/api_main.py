'''
Palvelimen ylläpitokutsut (tappo ymv)
'''
import os
import logging

from flask import make_response, request
from flask_restful import Resource, reqparse

from tiedostohallinta import main as th_main

import pettanflask as vakiot
import pettanflask.pettan_musatietokanta as musavakiot
import pettanflask.pettan_html as htmlvakiot

LOGGER = logging.getLogger(__name__)


# Mahdolliset moodit
MOODIVAIHTOEHDOT = ["normaali", "testi"]
parser_moodi = reqparse.RequestParser()
parser_moodi.add_argument(
    name="MOODI",
    type=str,
    help=f"Aktivoitava moodi. Vaihtoehdot {MOODIVAIHTOEHDOT}",
    choices=MOODIVAIHTOEHDOT,
    default="normaali",
    location="json"
    )
PAIVITYS_MENOSSA = False


class MoiMaailma(Resource):
    '''
    Moikkaa kutsujaa.
    '''
    def get(self):
        paluustr = "Moikka maailma"
        LOGGER.debug(paluustr)
        return make_response(paluustr, 200)

def lopeta():
    '''
    Tapa flaskirosessi.
    '''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        errmsg = "Ei pyöri Werkzeug-palvelinalustalla!"
        LOGGER.error(errmsg)
        raise RuntimeError(errmsg)
    func()

class Kuole(Resource):
    '''
    Tapa flaskirosessi (ehkä tähän keksii joskus jotain järkevämpää lol)
    '''
    def get(self):
        lopeta()
        paluustr = "Hyvästi maailma"
        LOGGER.debug(paluustr)
        return make_response(paluustr, 200)

class VaihdaMoodia(Resource):
    '''
    Vaihda asetukset testimoodin asetuksiin.
    (yksikkötestejä varten)
    '''
    def post(self):
        args = parser_moodi.parse_args()
        moodi = args.get("MOODI")
        # Testimoodi
        if moodi == "testi":
            # Testi-ini @ ../
            inisijainti = os.path.dirname(os.path.dirname(__file__))
            inisijainti = os.path.join(inisijainti, "tests", "data", "testiasetukset.ini")
            vakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
            musavakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
            htmlvakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
            paluustr = f"Vaihdettu moodiin {moodi}."
            paluukoodi = 200
        elif moodi == "normaali":
            vakiot.lue_asetukset_tiedostosta()
            musavakiot.lue_asetukset_tiedostosta()
            htmlvakiot.lue_asetukset_tiedostosta()
            paluustr = f"Vaihdettu moodiin {moodi}."
            paluukoodi = 200
        else:
            paluustr = f"Ei moodia {moodi}."
            paluukoodi = 400
        LOGGER.debug(paluustr)
        return make_response(paluustr, paluukoodi)

class PaivitaTietokannat(Resource):
    '''
    Päivitä palvelimen tietokannat ajan tasalle.
    '''
    def post(self):
        global PAIVITYS_MENOSSA
        if PAIVITYS_MENOSSA:
            paluustr = "Tietokantojen päivitys on jo menossa."
            paluukoodi = 400
            LOGGER.debug(f"{paluukoodi}: {paluustr}")
        else:
            PAIVITYS_MENOSSA = True
            try:
                th_main.main()
                vakiot.lue_asetukset_tiedostosta()
                musavakiot.lue_asetukset_tiedostosta()
                htmlvakiot.lue_asetukset_tiedostosta()
                paluustr = "Asetukset päivitetty."
                paluukoodi = 200
            except (ValueError, OSError, KeyError) as err:
                paluustr = "Päivitys ei onnistunut: {err}"
                paluukoodi = 400
            PAIVITYS_MENOSSA = False
        return make_response(paluustr, paluukoodi)
