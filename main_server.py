from event_server import run_event_server
from client_server import run_client_server
from asyncio import get_event_loop
from log_console import ConsoleClientLogger, ConsoleEventLogger

if __name__ == "__main__":

    loop = get_event_loop()

    client_server = run_client_server(loop, ConsoleClientLogger())
    source_server = run_event_server(loop, client_server, ConsoleEventLogger())
    
    loop.run_forever()
