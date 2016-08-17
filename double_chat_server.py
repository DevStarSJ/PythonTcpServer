from chat_server import run_server
from multiprocessing import Process

HOST = 'localhost'
PORT_SOURCE = 9090
PORT_CLIENT = 9099
ENCODING = 'utf-8'

list_process = []
list_server = []

def run_server_source():
    server = run_server(PORT_SOURCE)
    list_server.append(server)

def run_server_client():
    server = run_server(PORT_CLIENT)
    list_server.append(server)

if __name__ == "__main__":
    process1 = Process(target=run_server_source)
    process2 = Process(target=run_server_client)
    list_process.append(process1)
    list_process.append(process2)

    for p in list_process:
        p.start()

    for p in list_process:
        p.join()