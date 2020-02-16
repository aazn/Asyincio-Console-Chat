import asyncio
import argparse


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, loop, on_con_lost, name):
        self.on_con_lost = on_con_lost
        self.transport = None
        self.loop = loop
        self.name = name

    def connection_made(self, transport):
        self.transport = transport
        transport.write(self.name.encode())

    def data_received(self, data):
        print('{}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

    def send(self, data):
        if data and self.name:
            self.transport.write(data.encode())

    async def stdout_forever(self, loop):
        while True:
            mes = await loop.run_in_executor(None, input, "Me: ")
            self.send(mes)



async def main():
    settings = argparse.ArgumentParser()
    settings.add_argument("--addr", default="127.0.0.1", type=str)
    settings.add_argument("--port", default="8887", type=int)
    args = vars(settings.parse_args())

    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    print('Please, write your name')
    name = input()

    client = EchoClientProtocol(loop, on_con_lost, name)
    transport, protocol = await loop.create_connection(
        lambda: client,
        args['addr'], args["port"])

    asyncio.ensure_future(client.stdout_forever(loop))

    try:
        await on_con_lost
    finally:
        transport.close()

asyncio.run(main())
