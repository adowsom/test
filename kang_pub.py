import time
data = {}
for x in range(2000000):
  data[str(x)] = x

for x in range(60):
  time.sleep(3)
  print(len(data)) 


print(data["5"]) 
