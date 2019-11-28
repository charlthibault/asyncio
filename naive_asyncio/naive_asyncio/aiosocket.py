import select
import socket

from naive_asyncio.ioloop import EventHandler, Future, gather


def epoll_handler(epoll, *poll_args, **poll_kwargs):
    def condition():
        return bool(epoll.poll(*poll_args, **poll_kwargs))

    return EventHandler(condition=condition)


def select_handler(*epolls):
    future = Future()

    def condition():
        results = [epoll.poll(0) for epoll in epolls]

        is_done = any(results)
        if is_done:
            future.result = results
        return is_done

    return EventHandler(condition=condition, future=future)



class AIOSocket:
    def __init__(self, socket):
        self.socket = socket
        self.pollin = select.epoll()
        self.pollin.register(self, select.EPOLLIN)
        self.pollout = select.epoll()
        self.pollout.register(self, select.EPOLLOUT)

    async def close(self):
        pollin_ready, pollout_ready = await select_handler(self.pollin, self.pollout)
        if pollin_ready:
            self.pollin.close()
        if pollout_ready:
            self.pollout.close()

        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    async def bind(self, addr):
        await epoll_handler(self.pollin)
        self.socket.bind(addr)

    async def listen(self):
        await epoll_handler(self.pollin)
        self.socket.listen()

    async def connect(self, addr):
        await epoll_handler(self.pollin)
        self.socket.connect(addr)

    async def accept(self):
        await epoll_handler(self.pollin, 0)
        client, _ = self.socket.accept()
        return self.__class__(client)

    async def recv(self, bufsize):
        await epoll_handler(self.pollin, 0)
        return self.socket.recv(bufsize)

    async def send(self, bytes):
        await epoll_handler(self.pollout, 0)
        return self.socket.send(bytes)

    async def sendall(self, bytes):
        SSL_WRITE_BLOCKSIZE = 1024

        await epoll_handler(self.pollout, 0)

        total_sent = 0
        while total_sent < len(bytes):
            sent = await self.send(bytes[total_sent: total_sent + SSL_WRITE_BLOCKSIZE])
            total_sent += sent

        return total_sent

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def aiosocket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):
    return AIOSocket(socket.socket(family, type, proto, fileno))
