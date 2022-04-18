Flask-pohjainen http-palvelin pettankoneelle.

Kirjoitushetkellä vanha kunnon pettankone on hyvin pitkälti pelkkä ssh-palvelin ja tavarasäilö.
Sellaisenaankin se on asiansa ihan hyvin ajanut, ja esim. Musatietokanta ja synkkasetit on pelittänyt
(enimmäkseen) ihan hyvin, mutta on se silti rajoittava tekijä.
Lähinnä jossain kohtaa havahduin siihen, että ainoa mikä tekee Musatietokannasta linux-spesifin
on se, että se käyttää tiedostojen lataamiseen bashin scp-kutsua.

Nyt kun [töissä] opin Flaskin olemassaolon, tajusin että http-pohjainen tiedostojenlatailu
olisi itse asiassa varsin helppo toteuttaa. Ja samaan syssyyn saisi esim. verkkosivupohjaisen pääsyn
kuvakansioihin, kaikkia niitä tilanteita varten kun tarttis näyttää
`se yks kuva` mutta google/danbooru ei toimita ja tötterissä se on jossain iäisyyden päässä.

Asennus ja riippuvuudet:

- Riippuvuudet on aika kevyet, lukee `setup.py`. Läh. Tiedostohallinta, flask, requests.

- Setit saa asennettua `pip`illä kun laittaa siihen että `pip install git+https://github.com/Pilperi/Pettanflask`

- Flask-palvelinten ajoon löytyy ohjeet netistä, oleellista pitää huolta että `FLASK_APP` osoittaa paketin `main.py`-tiedostoon ja että ajaessa kutsuu nimenomaan `flask run --host=0.0.0.0` jos haluaa että palvelin näkyy ulkomaailmallekin eikä vain sisäverkossa.
