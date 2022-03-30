'''
Palvelimen ylläpitokutsut (tappo ymv)
'''

from flask import make_response, request
from flask_restful import Resource


class MoiMaailma(Resource):
    '''Moikkaa kutsujaa.'''
    def get(self):
        return make_response("Moikka maailma")

def lopeta():
    '''Tapa flaskirosessi.'''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

class Kuole(Resource):
    '''Tapa flaskirosessi (ehkä tähän keksii joskus jotain järkevämpää lol)'''
    def get(self):
        lopeta()
        return make_response("Hyvästi maailma", 200)
