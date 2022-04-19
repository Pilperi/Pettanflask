'''
Pettanin flaskipalvelimen pääscripti.
Hoitaa juttelun eli käytännössä
kutsuu oikeaa funktiota pyyntöargumentin
perusteella.
'''
import os

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

app = Flask(__name__) # flask
api = Api(app) # rest


#-------------------------------------------------------------------------------
# Polut

# Ylläpito
api.add_resource(api_main.MoiMaailma, "/")
api.add_resource(api_main.Kuole, "/kuole")
api.add_resource(api_main.VaihdaMoodia, "/aktivoi_moodi")
api.add_resource(api_main.PaivitaTietokannat, "/paivita_tietokannat")

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
    app.run(debug=True)
