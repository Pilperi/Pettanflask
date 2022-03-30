'''
Pettanin flaskipalvelimen pääscripti.
Hoitaa juttelun eli käytännössä
kutsuu oikeaa funktiota pyyntöargumentin
perusteella.
'''

import logging

from flask import Flask
from flask_restful import Api

# Vakiot
import pettanflask as vakiot

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

if __name__=="__main__":
    vakiot.IP = "127.0.0.1:5000"
    app.run(debug=True)
