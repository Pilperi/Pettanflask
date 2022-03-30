'''
Kuvakansioiden API-rajapintafunktiot.
'''
import os
import time

from flask import make_response, send_from_directory, abort
from flask_restful import Resource, reqparse

import pettanflask.pettan_html as htmlvak
from pettanflask.pettan_html import funktiot_htmlgen as htmlgen

parser_haku = reqparse.RequestParser()
parser_haku.add_argument(name="kansio", type=str, help="Alikansio INTERNET-kansiossa.")
parser_haku.add_argument(name="termi", type=str, help="Hakutermi (tiedostonimi).")


class Kuvakansio(Resource):
    '''Anna joko lista kuvakansioista tai kuvakansion sisältö.

    Sisään
    ------
    kansio : str tai None
        Kansio joka tarkoitus näyttää.
        Jos str, näyttää kyseisen kansion sisällön ruudukkona,
        polku @ INTERNET, esim "Art (kankore)"
        tai "Art (kankore)/Murakumo".
        Jos None, näyttää listan saatavilla olevista kansioista.
    hakutermi : str tai None
        Rajaa näytettävä sisältö tiedostonimen perusteella,
        kirjainkoko-invariantti ja mielekäs vain jos `kansio` on str.
        Jos None, ei tee rajausta vaan näyttää kaiken.
    sivu : int
        Monesko sivu näkymästä halutaan näyttää.
        (kuvathumbit n x m ruudukkona, joita k kappaletta)
        Mielekäs vain jos `kansio` on str.

    Ulos
    ----
    str tai 404
        HTML-sivudata stringinä, paluukoodi 200.
        Jos kansiota ei löydy, 404.
    '''
    def luo_ruudukkohtml(self, kansio, hakutermi, sivu):
        '''Luo HTML-stringi joka vastaa toivottua näkymää.

        Sisään
        ------
        kansio : str
            Alikansion polku @ INTERNET, esim "Art (kankore)"
            tai "Art (kankore)/Murakumo"
        hakutermi : str
            Karsi tulokset tiedostonimen mukaan.

        sivu : int
            Monennettako sivua kansionäkymästä halutaan katsoa.

        Ulos
        ----
        str
            HTML-dokumentti stringinä, kuvat ruudukkona,
            alhaalla napit sivunvaihtoon sekä hakupalkki.
            ks. htmlgen.kuvaruudukko()
        '''
        n_rivia, m_kolumnia = htmlvak.RUUDUKKO_KOKO
        # Luo HTML ja luo kuvien thumbnailit
        htmlstr, kohdetiedostot = htmlgen.kuvaruudukko(
            kansio, hakutermi, sivu, n_rivia, m_kolumnia
            )
        # Tarvittaessa odota että thumbit saadaan luotua
        aika = time.time()
        timeout = 2
        while time.time()-aika < timeout:
            if any(not os.path.exists(kuva) for kuva in kohdetiedostot):
                time.sleep(1E-3)
            else:
                break
        return htmlstr

    def get(self, kansio=None, hakutermi=None, sivu=0):
        '''Palauttaa ruudukko-HTML polun perusteella'''
        if not isinstance(kansio, str):
            htmlstr = htmlgen.hauskatkansiot(htmlvak.INTERNET)
        elif os.path.exists(os.path.join(htmlvak.INTERNET, kansio)):
            htmlstr = self.luo_ruudukkohtml(kansio, hakutermi, sivu)
        else:
            abort(404)
        return make_response(htmlstr, 200)

    def post(self, kansio=None, hakutermi=None, sivu=0):
        '''Palauttaa ruudukko-HTML haun perusteella'''
        args = parser_haku.parse_args()
        kansio = args["kansio"]
        hakutermi = args["termi"]
        if os.path.exists(os.path.join(htmlvak.INTERNET, kansio)):
            htmlstr = self.luo_ruudukkohtml(kansio, hakutermi, sivu=0)
            return make_response(htmlstr, 200)
        abort(404)


class Kuvadata(Resource):
    '''
    Kuvien thumbit, binääridatana.

    Sisään
    ------
    peruspolku : str {"thumb", "INTERNET"}
        Halutaanko kuva thumbikansiosta vaiko täyskokokansiosta.
    tiedostopolku : str
        Tiedoston polku @ peruspolku, esim.
        "/Art (kankore)/Murakumo/0/Murakumo001.jpg" (thumb) tai
        "/Art (kankore)/Murakumo/Murakumo001.jpg" (kokokuva)

    Ulos
    ----
    binääridata tai 404
        Kuvadata binäärinä, jos löytyy.
        Muutoin 404.
    '''
    def get(self, peruspolku, tiedostopolku):
        '''Palauttaa kuvadatan binäärinä'''
        if peruspolku == "thumb":
            peruspolku = htmlvak.THUMBIKANSIO
        elif peruspolku == "INTERNET":
            peruspolku = htmlvak.INTERNET
        else:
            abort(404)
        try:
            return send_from_directory(peruspolku, tiedostopolku)
        except (FileNotFoundError, PermissionError) as err:
            if isinstance(err, FileNotFoundError):
                abort(404)
            abort(403)
