import json
import struct
import socket

def send(conn, data):
    conn.send(struct.pack("I", len(data)) + data)

def readInt(conn):
    return struct.unpack("I", conn.recv(4))[0]

s = socket.socket()
s.connect(("", 4000))

helloData = json.dumps({"name":"HELLO", "data":{"nickname":"testPy"}}).encode("utf-8")
send(s, helloData)

print(s.recv(readInt(s)))
