import os
import time
import shutil
import subprocess

import pettanflask as vakiot
from pettanflask.html import funktiot_htmlgen as htmlgen


def moi_maailma():
 return("Moikka maailma")


def moi_kissa():
 return("<p>Kissa hevonen sika</p>")


def kuvakansio(kansio, hakutermi, sivu):
	'''
	Näytä kansion kuvat ruudukkona.
	'''
	return luo_kuvaruudukko(kansio, hakutermi=hakutermi, sivu=sivu)


def hauskatkansiot():
	'''
	Näytä kansion kuvat ruudukkona.
	'''
	return htmlgen.hauskatkansiot()


def luo_kuvaruudukko(kuvakansio, hakutermi=None, sivu=0, n=5, m=5):
	'''
	Luo kuvaruudukko jossa n x m kuvaa.
	'''
	# Luo HTML ja luo kuvien thumbnailit
	htmlstr, kohdetiedostot = htmlgen.kuvaruudukko(
		kuvakansio, hakutermi, sivu, n, m
		)
	t = time.time()
	timeout = 10
	while time.time()-t < timeout:
		if any(not os.path.exists(kuva) for kuva in kohdetiedostot):
			time.sleep(1E-3)
		else:
			break
	return htmlstr
