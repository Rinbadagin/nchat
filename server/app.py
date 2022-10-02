import asyncio
from client.handler import *
from client.commands import PREFIX

async def handle_conn(reader, writer):
    #sets up client information and passes to client handler
    writer.write(f'Handle? {PREFIX}'.encode())
    handle = (await reader.read(31)).decode().strip()
    print(f"Login attempt {handle}")
    try:
        client = ClientHandler(writer, reader, handle)
    except:
        writer.close()
        return
    writer.write(f'Joining as: {handle}\n'.encode())
    async with client_list_lock:
        client_list.append(client)
    await send_all(f"{handle} has connected.\n", exempt_client=client)
    await client.handle_conn()
    try:
        await writer.drain()
        writer.close()
    except ConnectionError as e:
        pass

async def main():
    server = await asyncio.start_server(
        handle_conn, '127.0.0.1', 1337)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
