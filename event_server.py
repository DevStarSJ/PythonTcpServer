from datetime import datetime, timedelta
from peer import Peer
from server import Server
from appsettings import get_appsettings

appsettings = get_appsettings()

PORT = appsettings["eventListenerPort"]
LOG_DEBUG = appsettings["logLevel"] == "debug"
LOG_INTERVAL = appsettings["logInterval"]
ENCODING = 'utf-8'

class EventPeer(Peer):
    def on_received(self, bytes):
        if LOG_DEBUG:
            print(self.name, bytes.decode(ENCODING))
        self._server.process(self, bytes)


class EventServer(Server):
    def __init__(self, loop, port, client_server, logger):
        self._client_server = client_server
        self._logger = logger
        self._message_count = 0
        self._message_accumulator = 0
        self._timedelta = timedelta(milliseconds = LOG_INTERVAL)
        self._last_log_time = datetime.now()
        super().__init__(loop, port)
        self.listen(5)

    def remove(self, peer):
        self._logger.quit_log(peer)
        super().remove(peer)

    def process(self, peer, message):
        self._logger.event_message_log(peer, message)
        self._client_server.process(message)

        if LOG_DEBUG:
            self._message_count += 1
            now =  datetime.now()
            timedelta = now - self._last_log_time
            if timedelta > self._timedelta:
                self._message_accumulator += self._message_count
                print('[Event Accumulator Log][{0}] : total message : {1} , current interval message : {2}'.format(now, self._message_accumulator, self._message_count))
                self._message_count = 0

    def get_peer(self, peer_sock, peer_name):
        return EventPeer(self, peer_sock, peer_name)

    def on_connected(self, peer):
        self._logger.connect_log(peer)
        self._peers.append(peer)


def run_event_server(loop, client_server, logger):
    server = EventServer(loop, PORT, client_server, logger)

    if LOG_DEBUG:
        print(server)

    return server
