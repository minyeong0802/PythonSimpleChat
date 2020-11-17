import json
import socket
import struct
import threading

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(("", 4000))
s.listen()

users = {}
rooms = {}

def send(conn, data):
    data = data.encode("utf-8")
    conn.send(struct.pack("I", len(data)) + data)

def handle_client(conn):
    buf = b""
    nickname = ""

    while True:
        rawLength = conn.recv(4)
        if (not rawLength) or len(rawLength) < 4:
            print("close")
            return
        length = struct.unpack("I", rawLength)[0]

        while len(buf) < length :
            part = conn.recv(512)
            if not part:
                print("close")
                conn.close()
                return
            buf += part

        recv_packet = json.loads(buf[:length])
        buf = buf[length:]

        if recv_packet["name"] == "HELLO":
            nickname = recv_packet["data"]["nickname"]
            
            if nickname in users or not nickname:
                conn.send('{"status":1}')
                conn.close()
                return
            
            users[nickname] = {
                "conn":conn,
            }
            send(conn, '{"status":0}')

        if recv_packet["name"] == "JOIN":
            if not nickname:
                send(conn, '{"status":1}')
                conn.close()
                return

            if not rooms in recv_packet["data"]["roomId"]:
                send(conn, '{"status":2}')
                conn.close()
                return
            
            rooms[recv_packet["data"]["roomId"]]["users"].append(nickname)
            send(conn, '{"status":0}')

        if recv_packet["name"] == "SENDMSG":
            if not nickname:
                send(conn, '{"status":1}')
                conn.close()
                return

            if not rooms in recv_packet["data"]["roomId"]:
                send(conn, '{"status":2}')
                conn.close()
                return
            
            if not nickname in rooms[recv_packet["data"]["roomId"]]["users"]:
                send(conn, '{"status":3}')
                conn.close()
                return

            for user in rooms[recv_packet["data"]["roomId"]]["users"]:
                try:
                    send(users[user], json.dumps({"name":"RECVMSG", "data":{"nickname":nickname, "msg":recv_packet["data"]["msg"]}}))
                except:
                    del users[user]
            send(conn, '{"status":0}')

while True:
    conn, (ip, port) = s.accept()
    print("Connected {}".format(ip))
    threading.Thread(target=handle_client, args=(conn,)).start()
