from server_source import run_source_server
from server_client import run_client_server
#from multiprocessing import Process
from time import sleep
#from threading import Thread
#import asyncio
#import threading
from asyncio import Task, coroutine, get_event_loop

ENCODING = 'utf-8'

list_process = []

#client_server = run_client_server()
#source_server = run_source_server(client_server)

def run_server_source():
    #while not client_server:
    #    print('client_server is None')
    #    sleep(0.1)
    #print(client_server)
    source_server = run_source_server(client_server)
    source_server.loop.run_forever()

def run_server_client():
    #client_server = run_client_server()
    #print('client',client_server)
    client_server.loop.run_forever()

if __name__ == "__main__":
    #process1 = Process(target=run_server_client)
    #list_process.append(process1)
    #process1.start()

    #source_thread = Thread(target=run_server_source)
    #source_thread.start()

    #process2 = Process(target=run_server_source)
    #list_process.append(process2)
    #process2.start()
    loop = get_event_loop()
    client_server = run_client_server(loop)
    source_server = run_source_server(loop, client_server)
    
    loop.run_forever()
