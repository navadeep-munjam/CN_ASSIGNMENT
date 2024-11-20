
# Server Code
import asyncio
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f"Server: Connection established with {addr}")

    while True:
        try:
            data = await reader.read(1024)  # Read up to 1024 bytes
            if not data:
                break
            logging.info(f"Server received: {data.decode()} from {addr}")

            # Echo the received data back to the client
            writer.write(data)
            await writer.drain()
            logging.info(f"Server echoed back: {data.decode()} to {addr}")
        except ConnectionResetError:
            logging.warning(f"Server: Connection reset by client {addr}")
            break

    logging.info(f"Server: Closing connection to {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    # Use getaddrinfo to set up both IPv4 and IPv6 addresses
    server = await asyncio.start_server(
        handle_client, host=None, port=12345, family=socket.AF_UNSPEC
    )

    # Retrieve and print bound server addresses (IPv4 and/or IPv6)
    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f"Server started on {addresses}")

    # Run the server
    async with server:
        await server.serve_forever()

# Run the server
asyncio.run(main())
