'''
Pettanin flaskipalvelimen pääscripti.
Hoitaa juttelun eli käytännössä
kutsuu oikeaa funktiota pyyntöargumentin
perusteella.
'''
import os
import logging

from flask import Flask
from flask_restful import Api

# Vakiot
import pettanflask as vakiot
import pettanflask.pettan_musatietokanta as musavakiot
import pettanflask.pettan_html as htmlvakiot

# API
from pettanflask import api_main
from pettanflask.pettan_html import api_html
from pettanflask.pettan_musatietokanta import api_musatietokanta

LOGGER = logging.getLogger(__name__)

app = Flask(__name__) # flask
api = Api(app) # rest


#-------------------------------------------------------------------------------
# Polut

# Ylläpito
api.add_resource(api_main.MoiMaailma, "/")
api.add_resource(api_main.Kuole, "/kuole")

# HTML-jutut
api.add_resource(api_html.Kuvakansio,
    "/html/hauskatkuvat/",
    "/html/hauskatkuvat/<path:kansio>",
    "/html/hauskatkuvat/<path:kansio>&s=<int:sivu>",
    "/html/hauskatkuvat/<path:kansio>&etsi=<string:hakutermi>",
    "/html/hauskatkuvat/<path:kansio>&s=<int:sivu>&etsi=<string:hakutermi>",
    "/html/hauskatkuvat/<path:kansio>&etsi=<string:hakutermi>&s=<int:sivu>"
    )
api.add_resource(api_html.Kuvadata,
    "/html/<string:peruspolku>" # {thumb, INTERNET}
    +"/<path:tiedostopolku>" # polku thumbikansiossa tai INTERNET-kansiossa
    )

# Musatietokantajutut
api.add_resource(api_musatietokanta.Musatietokanta_haku,
    "/musatietokanta"
    )
api.add_resource(api_musatietokanta.Musatietokanta_lataus,
    "/musatietokanta/biisi",
    "/musatietokanta/biisi/<path:polku>",
    )

#-------------------------------------------------------------------------------

# Devaussetit
if __name__=="__main__":
    # Testi-ini @ ../
    inisijainti = os.path.dirname(os.path.dirname(__file__))
    inisijainti = os.path.join(inisijainti, "tests", "data", "testiasetukset.ini")
    vakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
    musavakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
    htmlvakiot.lue_asetukset_tiedostosta(polku=inisijainti, asetusnimi="testi")
    app.run(debug=True)
