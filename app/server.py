#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data)

        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r,\n", "")
                self.transport.write(
                    f"Hello, {self.login}!\r\n".encode()
                )
            else:
                self.transport.write("Wrong login\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("New client is entered")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Client is out")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"

        for user in self.server.clients:
            user.transport.write(message.encode())


class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()


        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            9999
        )

        print("Server is running ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Server is stopped manually")
