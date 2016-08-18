from event_manager import translate_protocol
from log_console import get_message
from peer import Peer
from server import Server


HOST = 'localhost'
PORT = 9099
ADDR = (HOST, PORT)
ENCODING = 'utf-8'
BUFFER_SIZE = 1024


class ClientPeer(Peer):
    def on_received(self, bytes):
        self.id = int(bytes.decode(ENCODING))
        self._server.regist(self)


class ClientServer(Server):
    def __init__(self, loop, port, logger):
        self._clients = {}
        self._followers = {}
        self._logger = logger
        super().__init__(loop, port)

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
