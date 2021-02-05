import time
data = {}
for x in range(3000000):
  data[str(x)] = x

for x in range(3):
  time.sleep(3)
  print(len(data)) 


print(data["5"]) 
import os
os.environ["last"] = "1"
is_prod = os.environ.get('last', None)
print(is_prod)
