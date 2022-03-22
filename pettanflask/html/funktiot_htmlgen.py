'''
HTML-kasausfunktiot.
'''
import os
import subprocess

from pettanflask import IP
import pettanflask.html as vakiot


def kuvaruudukko(kuvakansio, hakutermi, sivu, n, m):
	'''
	Luo ruudukko kuvia:
	kuvakansion hakutermiä vastaavista kuvista n x m ruudukko,
	annetulla sivunumerolla (ts. ruudukoita monta).
	Luo samalla tarvittavat thumbnailit.
	
	Sisään
	------
	kuvakansio : str
		Kansio jossa kuvat sijaitsevat.
	'''
	if not isinstance(hakutermi, str):
		kuvat = [
			a for a in os.listdir(os.path.join(vakiot.INTERNET, kuvakansio))
			if a.split(".")[-1].lower() in vakiot.KUVATIEDOSTOT
			]
	else:
		kuvat = [
			a for a in os.listdir(os.path.join(vakiot.INTERNET, kuvakansio))
			if a.split(".")[-1].lower() in vakiot.KUVATIEDOSTOT
			and hakutermi.lower() in a.lower()
			]
	kuvia_per_sivu = n*m
	alkukuva = min(len(kuvat), sivu*kuvia_per_sivu)
	loppukuva = min(len(kuvat), (sivu+1)*kuvia_per_sivu)
	kohdekuvat = kuvat[alkukuva:loppukuva]
	# Luo thumbnailit
	pohja = vakiot.THUMBIKANSIO
	if not os.path.isdir(os.path.join(pohja, kuvakansio)):
		os.mkdir(os.path.join(pohja, kuvakansio))
	if not os.path.isdir(os.path.join(pohja, kuvakansio, str(sivu))):
		os.mkdir(os.path.join(pohja, kuvakansio, str(sivu)))
	htmlstr = '''<!DOCTYPE html>
<html>
<div class="row">
  <div class="column">
  '''
	kohdetiedostot = [""]*len(kohdekuvat)
	for k,kuvatiedosto in enumerate(kohdekuvat):
		lahdepolku = f"/mnt/data/Jouni/INTERNET/{kuvakansio}/{kuvatiedosto}"
		kohdepolku = f"{pohja}/{kuvakansio}/{sivu}"
		kohdetiedostot[k] = "{kohdepolku}/{kuvatiedosto}"
		if not os.path.exists(kohdetiedostot[k]):
			subprocess.Popen([
				"mogrify", "-resize", "200x200",
				"-path", kohdepolku,
				lahdepolku
				])
		htmlstr += (
			f"    <a href=\"http://{IP}/INTERNET/{kuvakansio}/{kuvatiedosto}\">"
			+f"<img src=\"http://{IP}/thumb/{kuvakansio}/{sivu}/{kuvatiedosto}\" ></a>\n"
			)
		if k and not k%n:
			htmlstr += "</div><div class=\"column\">"
	htmlstr += "  </div>\n</div>\n"
	kutsupohja = f"http://{IP}/hauskatkuvat/{kuvakansio}"
	kutsupohja += f"&etsi={hakutermi}"*isinstance(hakutermi, str)
	edellinenkutsu = kutsupohja + f"&s={sivu-1}"
	seuraavakutsu = kutsupohja + f"&s={sivu+1}"
	if sivu-1 >= 0:
		htmlstr+= f"<form><button type=\"button\"  onclick=\"location.href=\'{edellinenkutsu}\'\">Edellinen ({sivu-1})</button></form>"
	if (sivu+1)*kuvia_per_sivu < len(kuvat):
		htmlstr+= f"<form><button type=\"button\"  onclick=\"location.href=\'{seuraavakutsu}\'\">Seuraava ({sivu+1})</button></form>\n"
	htmlstr += kansion_hakunappi(kuvakansio)
	htmlstr += "</html>"
	return htmlstr, kohdetiedostot


def kansion_hakunappi(kansio):
	htmlstr = '''<form action = "http://{}/etsikuvaa" method = "post">
	<p><input type="text" name="termi" /></p>
	<p><input type="hidden" value="{}" name="kansio"/></p>
</form>'''.format(IP, kansio)
	return htmlstr


def hae_alikansiot(kansio):
	alikansiot = [
		a
		for a in os.listdir(kansio)
		if os.path.isdir(os.path.join(kansio, a))
		]
	# alikansiot...
	return alikansiot


def hauskatkansiot():
	'''
	Anna linkit kaikkiin kansioihin joita on katseltavissa.
	'''
	alikansiot = hae_alikansiot(vakiot.INTERNET)
	htmlstr = '''<div class="text"><pre>'''
	for alikansio in alikansiot:
		htmlstr += "<a href=\"http://{}/hauskatkuvat/{}\">{}</a>\n".format(IP, alikansio, alikansio)
	htmlstr += '''</pre></div>'''
	return htmlstr
