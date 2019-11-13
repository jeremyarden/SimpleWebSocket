import socketserver
import base64
import hashlib
from struct import *

GUID_STR = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class WebSocketServer(socketserver.ThreadingMixIn, socketserver.BaseRequestHandler):
    def handle(self):
        # Receive data from client and split the headers
        self.data = self.request.recv(1024).strip()
        headers = self.data.split(b"\r\n")

        # "Connection: Upgrade" and "Upgrade: websocket" indicates a WebSocket connection
        if b"Connection: Upgrade" in self.data and b"Upgrade: websocket" in self.data:
            # Take the WebSocket key and initiate handshake process
            for h in headers:
                if b"Sec-WebSocket-Key" in h:
                    key = h.split(b" ")[1]

            self.request.sendall(self.handshake(key))

            # Connection is open, receiving all incoming frames
            while True:
                recv_data = self.request.recv(8192).strip()
                print("received data: ", recv_data)
                # if (len(recv_data) == 0):
                #     continue
                payload, opcode_and_fin = self.decode_frame(bytearray(recv_data))
                fin = opcode_and_fin >> 7
                opcode = opcode_and_fin & 15
                print("opcode: ", opcode)
                print("payload: ", payload)
                
                # opcode = 1 denotes a text frame
                if (opcode == 1):
                    decoded_payload = payload.decode('utf-8').split(" ")
                    print("decoded payload: ", decoded_payload)
                    if (decoded_payload[0] == "!echo"):
                        self.send_frame(decoded_payload[1].encode())
                    elif (decoded_payload[0] == "!submission"):
                        with open('a.zip', 'rb') as f:
                            zip_file = f.read()
                            self.send_file(zip_file)
                # opcode = 2 denotes a binary file
                # elif (opcode == 2):
                    

                #     with open('return.zip', 'wb') as f:
                #         f.write(payload)

                # opcode = 9 denotes a ping, send a pong back
                elif (opcode == 9):
                    print("ping")
                    self.send_pong(payload)
                # opcode = 8 denotes a connection close
                elif (opcode == 8):
                    self.send_close(payload)
                    self.request.close()
                    break
        # Violation of handshake
        else:
            print("incorrect request")
            stringErr = "HTTP/1.1 400 Bad Request\r\n" + "Content-Type: text/plain\r\n" + "Connection: close\r\n" + "\r\n" + "Incorrect request"
            self.request.sendall(bytes(stringErr, encoding='utf8'))

    # Constructing a handshake reply
    def handshake(self, key):
        key = key + GUID_STR
        resp_key = base64.standard_b64encode(hashlib.sha1(key).digest())

        resp = b"HTTP/1.1 101 Switching Protocols\r\n" + \
            b"Upgrade: websocket\r\n" + \
            b"Connection: Upgrade\r\n" + \
            b"Sec-WebSocket-Accept: %s\r\n\r\n"%(resp_key)

        return resp

    # Decoding message within frame received
    def decode_frame(self, frame):
        opcode_and_fin = frame[0]
        print("frame[0]: ", frame[0])
        print("opcode n fin in decode: ", opcode_and_fin)
        payload_len = frame[1]-128
        print("frame[1]: ", frame[1])
        print("payload length: ", payload_len)

        if (payload_len <= 125):
            mask = frame[2:6]
            print("mask: ", mask)

            encrypted_payload = frame[6: 6+payload_len]

            print(encrypted_payload)

            payload = bytearray([encrypted_payload[i] ^ mask[i%4] for i in range(payload_len)])
        elif (payload_len == 126):
            print("frame[2:4] big endian: ", int.from_bytes(frame[2:4], byteorder='big'))
            payload_len = int.from_bytes(frame[2:4], byteorder='big')
            print("len frame: ", len(frame))
            mask = frame[4:8]
            encrypted_payload = frame[8: 8+payload_len]

            print(encrypted_payload)
            print("len encrypted: ", len(encrypted_payload))

            with open('a.zip', 'rb') as f:
                data = f.read()

                if (payload_len != len(data)):
                    self.send_frame("0".encode())

            payload = []

        elif (payload_len == 127):
            print("frame[2:9] big endian: ", int.from_bytes(frame[2:9], byteorder='big'))
            payload_len = int.from_bytes(frame[2:9], byteorder='big')

            mask = frame[10:14]
            encrypted_payload = frame[14: 14+payload_len]

            print(encrypted_payload)
            print("len encrypted: ", len(encrypted_payload))
            with open('a.zip', 'rb') as f:
                data = f.read()

                if (payload_len != len(data)):
                    self.send_frame("0".encode())

            payload = []
        return (payload, opcode_and_fin)

    # Construct and then send frame
    def send_frame(self, payload):
        frame = [129]

        frame += [len(payload)]

        frame_to_send = bytearray(frame) + payload

        print("frame to send: ", frame_to_send)
        self.request.sendall(frame_to_send)

    # Send pong after ping received to notify that connection is still alive
    def send_pong(self, ping):
        pong = [138]

        pong += [len(ping)]

        pong_frame = bytearray(pong) + ping

        self.request.sendall(pong_frame)
        print("pong")

    def send_file(self, file):
        file_header = [130]

        if (len(file) <= 125):
            file_header += [len(file)]
        else:
            if (len(file) <= 65535): # if payload len is 126, it denotes that payload len is the next 2 bytes
                file_header += [126]
            elif (len(file) <= 18446744073709551615 and len(file) > 65535): # if payload len is 127, it denotes that payload len is the next 8 bytes
                file_header += [127]

        file_frame = bytearray(file_header) + pack('>h', len(file)) + file

        self.request.sendall(file_frame)

    # Close WebSocket server
    def send_close(self, payload):
        close_frame = [136]

        close_frame += [len(payload)]

        frame_to_send = bytearray(close_frame) + payload

        self.request.sendall(frame_to_send)
        print("close\n")

    # def verify_hash(self, file):
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 3000

    server = socketserver.TCPServer((HOST, PORT), WebSocketServer)

    server.serve_forever()