#!/usr/bin/env python3

import functools
from contextlib import AsyncExitStack

from naive_asyncio.aiosocket import aiosocket
from naive_asyncio.ioloop import gather, Loop, Future
from naive_asyncio.utils import Waiter


async def server(server_socket, server_started):
    print('binding server')
    await server_socket.bind(('localhost', 8888))

    await server_socket.listen()
    print('server ready')
    server_started.done()

    client_socket = await server_socket.accept()

    msg = await client_socket.recv(1024)
    print('Received from client', msg)
    await client_socket.send(msg[::-1])

    await client_socket.close()


async def client(client_socket):
    print('client connecting')
    await client_socket.connect(('localhost', 8888))

    await client_socket.send(b'Hello World!')
    msg = await client_socket.recv(1024)

    print('Received from server', msg)


async def main():
    _client = aiosocket()
    _server = aiosocket()

    async with AsyncExitStack() as stack:
        stack.enter_async_context(_server)
        stack.enter_async_context(_client)

        server_started = Future(callback=client(_client))
        await gather(server(_server, server_started))
        print('done')


if __name__ == '__main__':
    Loop().run_tasks(main())
