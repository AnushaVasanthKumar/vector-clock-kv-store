# src/client.py

import requests

nodes = [
    "http://node0:5000",
    "http://node1:5000",
    "http://node2:5000"
]

# Write to Node 0
res1 = requests.post(f"{nodes[0]}/put", json={"key": "x", "value": "A"})
print("Node 0 response:", res1.json())

# Write to Node 1
res2 = requests.post(f"{nodes[1]}/put", json={"key": "x", "value": "B"})
print("Node 1 response:", res2.json())

# Read from Node 2
res3 = requests.get(f"{nodes[2]}/get")
print("Node 2 state:", res3.json())
