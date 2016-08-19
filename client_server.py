from event_manager import translate_protocol
from log_console import get_message
from peer import Peer
from server import Server
from appsettings import get_appsettings

appsettings = get_appsettings()

PORT = appsettings["clientListenerPort"]
ENCODING = 'utf-8'
LISTEN_NUMBER = appsettings["concurrencyLevel"]
QUEUE_SIZE = appsettings["maxEventSourceBatchSize"]


class ClientPeer(Peer):
    def on_received(self, bytes):
        self.id = int(bytes.decode(ENCODING))
        self._server.regist(self)


class ClientServer(Server):
    def __init__(self, loop, port, logger):
        self._clients = {}
        self._followers = {}
        self._logger = logger
        self._message_queue = []
        self._current_message_index = 1
        super().__init__(loop, port)
        self.listen(LISTEN_NUMBER)

    def remove(self, peer):
        self._logger.quit_log(peer.id)
        del self._clients[peer.id]

    def regist(self, peer):
        self._logger.regist_log(peer)

        # check id if exist in client list
        if peer.id in self._clients.keys():
            peer.send(bytearray('ID exsited in connected clients. You disconnected.',ENCODING))
            self.remove(peer)
        else:
            self._clients[peer.id] = peer

    def process(self, message):
        event = translate_protocol(message)

        if event.sequence_number == self._current_message_index:
            self.do_event(event)

            while len(self._message_queue) != 0 \
                and self._message_queue[0].sequence_number == self._current_message_index:
                popped_event = self._message_queue[0]
                self._message_queue.remove(popped_event)
                self.do_event(popped_event)

        else:
            if len(self._message_queue) >= QUEUE_SIZE:
                # Python don't and do not need limit of list
                # if another work is needed, do it here
                pass

            self._message_queue.append(event)
            self._message_queue.sort(key = lambda e : e.sequence_number)

    def do_event(self, event):
        self._logger.log(event)

        if event.event_type == 'B':
            self.broadcast(event)
        elif event.event_type == 'S':
            self.update_profile(event)
        elif event.event_type == 'P':
            self.private_message(event)
        elif event.event_type == 'F':
            self.follow(event)
        elif event.event_type == 'U':
            self.unfollow(event)

        self._current_message_index += 1

    def private_message(self, event):
        message = get_message(event)
        self.send_message(event.to_id, message)

    def broadcast(self, event):
        message = get_message(event)

        for peer in self._clients.values():
            peer.send(bytearray(message, ENCODING))

    def follow(self, event):
        if event.to_id in self._followers.keys():
            if not event.from_id in self._followers[event.to_id]:
                self._followers[event.to_id].append(event.from_id)
        else:
            self._followers[event.to_id] = [ event.from_id ]

        message = get_message(event)
        self.send_message(event.to_id, message)

    def unfollow(self, event):
        if event.to_id in self._followers.keys():
            if event.from_id in self._followers[event.to_id]:
                self._followers[event.to_id].remove(event.from_id)

    def update_profile(self, event):
        if event.from_id in self._followers.keys():
            message = get_message(event)
            for to_id in self._followers[event.from_id]:
                self.send_message(to_id, message)

    def send_message(self, id, message):
        if id in self._clients.keys():
            self._clients[id].send(bytearray(message, ENCODING))

    def get_peer(self, peer_sock, peer_name):
        return ClientPeer(self, peer_sock, peer_name)

    def on_connected(self, peer):
        self._logger.connect_log(peer)

def run_client_server(loop, logger):
    server = ClientServer(loop, PORT, logger)
    print(server)
    return server
