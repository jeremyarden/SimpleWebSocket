import socketserver
import base64
import hashlib
import threading

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
                recv_data = self.request.recv(1024).strip()
                payload, opcode_and_fin = self.decode_frame(bytearray(recv_data))
                fin = opcode_and_fin >> 7
                opcode = opcode_and_fin & 15
                
                # opcode = 1 denotes a text frame
                if (opcode == 1):
                    decoded_payload = payload.decode('utf-8').split(" ")
                    if (decoded_payload[0] == "!echo"):
                        self.send_frame(decoded_payload[1].encode())
                # opcode = 9 denotes a ping, send a pong back
                elif (opcode == 9):
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

        payload_len = frame[1]-128

        mask = frame[2:6]
        encrypted_payload = frame[6: 6+payload_len]

        payload = bytearray([encrypted_payload[i] ^ mask[i%4] for i in range(payload_len)])

        return (payload, opcode_and_fin)

    # Construct and then send frame
    def send_frame(self, payload):
        frame = [129]

        frame += [len(payload)]

        frame_to_send = bytearray(frame) + payload

        print(frame_to_send)
        self.request.sendall(frame_to_send)

    # Send pong after ping received to notify that connection is still alive
    def send_pong(self, ping):
        pong = [129]

    # Close WebSocket server
    def send_close(self):
        



    
if __name__ == "__main__":
    HOST, PORT = "localhost", 3000

    server = socketserver.TCPServer((HOST, PORT), WebSocketServer)

    server.serve_forever()