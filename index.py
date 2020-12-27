import os,requests

address_list = []
for fi in range(1, 7):
    response = requests.get("https://raw.githubusercontent.com/thearthouse/kcmxpro/master/data/"+str(fi)+".data", timeout=60)
    for x in response.text.splitlines():
        address_list.append(x)

print(len(address_list))
for fi in range(1, 7):
    response = requests.get("https://raw.githubusercontent.com/thearthouse/kcmxpro/master/data/"+str(fi)+".data", timeout=60)
    for x in response.text.splitlines():
        address_list.append(x)

print(len(address_list))
for fi in range(1, 7):
    response = requests.get("https://raw.githubusercontent.com/thearthouse/kcmxpro/master/data/"+str(fi)+".data", timeout=60)
    for x in response.text.splitlines():
        address_list.append(x)

print(len(address_list))
address_list = set(address_list)
