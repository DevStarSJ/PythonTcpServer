import tcp_async_server
import socketserver
import multiprocessing
import uuid
import sys

HOST = 'localhost'
PORT_SOURCE = 9090
PORT_CLIENT = 9099

ENCODING = 'utf-8'

list_server = []
list_process = []
list_client = []

class AudienceTcpHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(self.client_address,'connected')
        list_client.append(self)

        while True:
            data = self.request.recv(1024)
            if not data:
                break;

        self.request.close()

class SourceHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break;

            text = data.decode(ENCODING)
            print(text)

            self.request.send('OK'.encode(ENCODING))
            for client in list_client:
                client.request.send(data)

        self.request.close()

def run_server_source():
    server = tcp_async_server.SimpleServer((HOST, PORT_SOURCE), SourceHandler)

    print(uuid.uuid1(),server.server_address)
    list_server.append(server)

    try:
        server.serve_forever()
    except KeyboardInterrupt: # Ctrl+C
        server.server_close()
        #sys.exit(0)

def run_server_client():
    server = tcp_async_server.SimpleServer((HOST, PORT_CLIENT), AudienceTcpHandler)

    print(uuid.uuid1(),server.server_address)
    list_server.append(server)

    try:
        server.serve_forever()
    except KeyboardInterrupt: # Ctrl+C
        server.server_close()
        #sys.exit(0)

if __name__ == "__main__":
    process1 = multiprocessing.Process(target=run_server_source)
    process2 = multiprocessing.Process(target=run_server_client)
    list_process.append(process1)
    list_process.append(process2)

    for p in list_process:
        p.start()

    for p in list_process:
        p.join()