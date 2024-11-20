import asyncio
import socket 
import logging as lg

# Configure lg
lg.basicConfig(level=lg.INFO, format='%(asctime)s - %(message)s')

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    lg.info(f"Server: Connection established with {addr}")

    while True:
        try:
            data = await reader.read(1024)
            if not data:
                break
            lg.info(f"Server received: {data.decode()} from {addr}")

            writer.write(data)
            await writer.drain()
            lg.info(f"Server echoed back: {data.decode()} to {addr}")
        except ConnectionResetError:
            lg.warning(f"Server: Connection reset by client {addr}")
            break

    lg.info(f"Server: Closing connection to {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, host=None, port=12345, family=socket.AF_UNSPEC
    )

    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    lg.info(f"Server started on {addresses}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
