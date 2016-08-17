from server_source import run_source_server
from server_client import run_client_server
from asyncio import get_event_loop

if __name__ == "__main__":

    loop = get_event_loop()

    client_server = run_client_server(loop)
    source_server = run_source_server(loop, client_server)
    
    loop.run_forever()
