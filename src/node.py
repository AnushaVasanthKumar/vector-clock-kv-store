# src/node.py

from flask import Flask, request, jsonify
import requests
import threading
import time
import os

app = Flask(__name__)
node_id = int(os.environ.get("NODE_ID"))
total_nodes = 3
vector_clock = [0] * total_nodes
store = {}
buffer = []
peers = [f"http://node{i}:5000" for i in range(total_nodes)]

def is_causally_ready(vc_msg):
    for i in range(total_nodes):
        if i == node_id:
            if vc_msg[i] != vector_clock[i] + 1:
                return False
        elif vc_msg[i] > vector_clock[i]:
            return False
    return True

def apply_write(data):
    global vector_clock
    key = data['key']
    value = data['value']
    vc = data['vc']
    store[key] = value
    vector_clock = [max(vector_clock[i], vc[i]) for i in range(total_nodes)]
    print(f"Applied: {key}={value}, Clock: {vector_clock}")

@app.route('/put', methods=['POST'])
def put():
    global vector_clock
    data = request.json
    key, value = data['key'], data['value']
    vector_clock[node_id] += 1
    store[key] = value

    msg = {'key': key, 'value': value, 'vc': vector_clock.copy()}
    for i in range(total_nodes):
        if i != node_id:
            try:
                requests.post(f"{peers[i]}/replicate", json=msg)
            except:
                pass
    return jsonify({'message': 'write success', 'vector_clock': vector_clock})

@app.route('/replicate', methods=['POST'])
def replicate():
    data = request.json
    if is_causally_ready(data['vc']):
        apply_write(data)
    else:
        buffer.append(data)
    return '', 200

@app.route('/get', methods=['GET'])
def get():
    return jsonify({'store': store, 'vector_clock': vector_clock})

def buffer_check_loop():
    while True:
        for item in buffer[:]:
            if is_causally_ready(item['vc']):
                apply_write(item)
                buffer.remove(item)
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=buffer_check_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
