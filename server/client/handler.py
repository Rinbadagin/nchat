import asyncio
client_list_lock = asyncio.Lock()
client_list = []
import client.commands as com

class ClientHandler:
    def __init__(self, writer, reader, handle):
        self.writer, self.reader = (writer, reader)
        self.set_handle(handle)
    
    def set_handle(self, new_handle):
        fail = False
        if com.PREFIX in new_handle:
            self.writer.write(f"Handles cannot contain {com.PREFIX}. Terminating. ".encode())
            fail = True
        if not new_handle.isalnum():
            self.writer.write(f"Handles must be alphanumeric (A to Z, a to z, 0 to 9). Terminating. ".encode())
            fail = True
        #potential race condition
        #Todo: remove
        for user in client_list:
            if user.handle == new_handle:
                self.writer.write(f"Handle is already in use. Terminating. ".encode())
                fail = True
                break
        if fail:
            self.writer.close()
            raise Exception
            return
        self.handle = new_handle

    async def get_line(self):
        return (await self.reader.read(65535))

    async def send(self, message):
        self.writer.write(message.encode())

    async def disconnect(self, message=False):
        #disconnect client
        if message:
            self.send(message)
            await self.writer.drain()
        self.writer.close()

    async def handle_conn(self):
        while True:
            try:
                data = await self.get_line()
                msg = data.decode()
                print(f"{self.handle}{com.PREFIX}{msg}")
                if msg[0] == com.PREFIX:
                    if len(msg.split(' ', 1)) == 2:
                        await (await com.get_command(msg.split(' ', 1)[0]))(self, msg.split(' ', 1)[1].strip())
                    else:
                        await (await com.get_command(msg))(self, msg.strip())
                else:
                    await send_all(self.handle+com.PREFIX+msg)
            except (ConnectionError, IndexError) as e:
                await self.disconnect()
                async with client_list_lock:
                    client_list.remove(self)
                await send_all(f"{self.handle} has left.\n")
                break

async def send_all(message, exempt_client = False):
    async with client_list_lock:
        for outbound in client_list:
            if not outbound is exempt_client:
                await outbound.send(com.PREFIX + message)


