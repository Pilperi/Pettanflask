import setuptools
import os

setuptools.setup(
    name="pettanflask",
    version="2022.03.22",
    url="https://www.github.com/Pilperi/Pettanflask",
    author="Pilperi",
    description="Pettankone HTTP-palvelimena.",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires = [
        "tiedostohallinta @ git+https://github.com/Pilperi/Tiedostohallinta",
        "requests"
		],
	python_requires=">=3.8, <4",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ]
)

# Luo asetustiedostot ymv
from requests import get as rget
import configparser

KOTIKANSIO = os.path.expanduser("~")
print(f"Kotikansio: {KOTIKANSIO}")
LOKAALI_KONE = os.path.basename(KOTIKANSIO)
print(f"Lokaali kone: {LOKAALI_KONE}")
TYOKANSIO = os.path.join(KOTIKANSIO, ".pettanflask")
print(f"Työkansio (asetuksille ja juoksevalle datalle): {TYOKANSIO}")
if not os.path.exists(TYOKANSIO):
    print(f"  Luodaan työkansio...")
    os.makedirs(TYOKANSIO)
    print("  Luotiin.")
THUMBIKANSIO = os.path.join(TYOKANSIO, "Thumbit")
print(f"Thumbikansio: {THUMBIKANSIO}")
if not os.path.exists(THUMBIKANSIO):
    print(f"  Luodaan thumbikansio...")
    os.makedirs(THUMBIKANSIO)
    print("  Luotiin.")

config = configparser.ConfigParser(default_section=LOKAALI_KONE)

# Defaulttaa koneen (globaali) IP & portti 5000
IP_OSOITE = rget("https://api.ipify.org").content.decode("ascii")
print(f"Paikallinen IP-osoite: {IP_OSOITE}")
PORTTI = "5000"
print(f"Oletusportti: {PORTTI}")

config.set(LOKAALI_KONE, "ip", IP_OSOITE)
config.set(LOKAALI_KONE, "portti", PORTTI)

ASETUSTIEDOSTO = os.path.join(TYOKANSIO, 'pettanvakiot.ini')
print(f"Tallennetaan asetukset kohteeseen: {ASETUSTIEDOSTO}")
with open(ASETUSTIEDOSTO, 'w+') as configfile:
    for key in config.keys():
        print(key)
        for asetus in config[key]:
            print(f"  {asetus} = {config[key][asetus]}")
    config.write(configfile)
    print("Tallennettu.")

