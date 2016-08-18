from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine, get_event_loop
from event_manager import translate_protocol


HOST = 'localhost'
PORT = 9099
ADDR = (HOST, PORT)
ENCODING = 'utf-8'
BUFFER_SIZE = 1024


class Peer(object):
    def __init__(self, server, sock, name):
        self.loop = server.loop
        self.name = name
        self._sock = sock
        self._server = server
        Task(self._peer_handler())

    def send(self, data):
        return self.loop.sock_sendall(self._sock, data)

    @coroutine
    def _peer_handler(self):
        try:
            yield from self._peer_loop()
        except IOError:
            pass
        finally:
            self._server.remove(self)

    @coroutine
    def _peer_loop(self):
        while True:
            buf = yield from self.loop.sock_recv(self._sock, BUFFER_SIZE)
            if buf == b'':
                break

            id = int(buf.decode(ENCODING))
            self._server.regist(id, self)


class Server(object):
    def __init__(self, loop, port):
        self.loop = loop
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('', port))
        self._serv_sock.listen(5)
        self._clients = {}
        self._followers = {}
        Task(self._server())

    def remove(self, peer):
        print('[%s] quit!' % (str(self._clients[peer])))
        del self._clients[peer]

    def regist(self, id, peer):
        # check id if exist in client list
        peers = [p for p,i in self._clients.items() if i == id]

        print(len(peers), peers)

        if len(peers) > 0:
            peer.send(bytearray('ID exsited in connected clients. You disconnected.',ENCODING))
            self.remove(peer)
        else:
            self._clients[peer] = id

        print(self._clients)

    def forward(self, message):

        sequence_number, event_type, from_user_id, to_user_id = translate_protocol(message)

        if event_type == 'B':
            self.broadcast(sequence_number)
        elif event_type == 'S':
            self.update_profile(from_user_id, sequence_number)
        elif event_type == 'P':
            self.private_message(from_user_id, to_user_id, sequence_number)
        elif event_type == 'F':
            self.follow(from_user_id, to_user_id, sequence_number)
        elif event_type == 'U':
            self.unfollow(from_user_id, to_user_id, sequence_number)
        
    def private_message(self, from_id, to_id, sequence_number):
        print('[%s] : print message from [%s] to [%s]' % (str(sequence_number), str(from_id), str(to_id)))
        message = '[%s] : private message from [%s].' % (str(sequence_number), str(from_id))
        self.send_message(to_id, message)

    def broadcast(self, sequence_number):
        message = '[%s] : This is broadcast message' % (str(sequence_number))

        for peer in self._clients.keys():
            peer.send(bytearray(message, ENCODING))

    def follow(self, from_id, to_id, sequence_number):

        #ignore if user is on connection status
        '''
        if not self.find_id(to_id):
            print('[%s] : Follow failed. [%s] is not connected.' % (str(sequence_number), str(to_id)))
            return
        '''

        if to_id in self._followers.keys():
            if not from_id in self._followers[to_id]:
                self._followers[to_id].append(from_id)
        else:
            self._followers[to_id] = [ from_id ]

        message = '[%s] : [%s] follows you.' % (str(sequence_number), str(from_id))
        print(message)
        self.send_message(to_id, message)

        print(self._followers)

    def unfollow(self, from_id, to_id, sequence_number):

        #ignore if user is on connection status

        message = '[%s] : [%s] unfollows [%s].' % (str(sequence_number), str(from_id), str(to_id))
        print(message)

        if to_id in self._followers.keys():
            if from_id in self._followers[to_id]:
                self._followers[to_id].remove(from_id)

        print(self._followers)

    def update_profile(self, from_id, sequence_number):
        if from_id in self._followers.keys():
            message = '[%s] : [%s] profile updated.' % (str(sequence_number), str(from_id))
            for to_id in self._followers[from_id]:
                self.send_message(to_id, message)

    def send_message(self, id, message):
        peers = [ p for p, i in self._clients.items() if i == id ]
        if len(peers) > 0:
            peers[0].send(bytearray(message, ENCODING))

    def find_id(self, id):
        peers = [ p for p, i in self._clients.items() if i == id ]
        return len(peers) > 0

    @coroutine
    def _server(self):
        while True:
            peer_sock, peer_name = yield from self.loop.sock_accept(self._serv_sock)
            peer_sock.setblocking(0)
            peer = Peer(self, peer_sock, peer_name)
            #self._peers.append(peer)
            print('Peer Connected : ', peer)

def run_client_server(loop):
    server = Server(loop, PORT)

    print(server)
    return server

if __name__ == '__main__':
    run_server(PORT)
