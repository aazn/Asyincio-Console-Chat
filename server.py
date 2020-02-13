import asyncio
import argparse


class EchoServerProtocol(asyncio.Protocol):
    def __init__(self, data_base):
        self.data_base = data_base
        self.name = None
        self.peername = None
        self.transport = None

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        self.data_base += [transport]
        self.transport = transport
        print('Connection from {}'.format(self.peername))

    def data_received(self, data):
        if data:
            if not self.name:
                self.name = data.decode()
                print('Connection from: {} (Name: {})'.format(self.peername, data.decode()))
                self.transport.write('You connect <{}> from {}'.format(self.name, self.peername).encode())
            elif data.decode()[0] == "-":
                if data.decode() == "-h" or data.decode() == "-help":
                    pass

            else:
                for trans in self.data_base:
                    mes = '<{}> {}'.format(self.name, data.decode())
                    trans.write(mes.encode())
                print('<{}> {}'.format(self.name, data.decode()))

    def connection_lost(self, ext):
        print('Close the client socket {} (Name: {})'.format(self.peername, self.name))
        for trans in self.data_base:
            mes = '<{}> disconnect'.format(self.name)
            trans.write(mes.encode())
        self.data_base.remove(self.transport)
        self.transport.close()


async def main():
    settings = argparse.ArgumentParser()
    settings.add_argument("--addr", default="127.0.0.1", type=str)
    settings.add_argument("--port", default="8887", type=int)
    args = vars(settings.parse_args())

    loop = asyncio.get_running_loop()
    data_base = []

    server = await loop.create_server(
        lambda: EchoServerProtocol(data_base),
        args["addr"], args["port"])

    async with server:
        await server.serve_forever()


asyncio.run(main())


