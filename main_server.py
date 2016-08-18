from server_source import run_source_server
from server_client import run_client_server
from asyncio import get_event_loop
from log_console import ConsoleLogger

if __name__ == "__main__":

    loop = get_event_loop()
    log_console = ConsoleLogger()

    client_server = run_client_server(loop, log_console)
    source_server = run_source_server(loop, client_server)
    
    loop.run_forever()
