import asyncio
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def tcp_echo_client(host):
    try:
        addr_info = socket.getaddrinfo(host, 12345, socket.AF_UNSPEC, socket.SOCK_STREAM)

        for family, socktype, proto, _, sockaddr in addr_info:
            try:
                reader, writer = await asyncio.open_connection(sockaddr[0], sockaddr[1], family=family)
                logging.info(f"Client: Connected to server at {sockaddr}")

                # Keep the connection open for multiple messages
                while True:
                    message = input("Enter message to send (or type 'exit' to quit): ")
                    if message.lower() == 'exit':
                        logging.info("Client: Exiting.")
                        break

                    # Send the message
                    logging.info(f"Client: Sending '{message}'")
                    writer.write(message.encode())
                    await writer.drain()

                    # Receive and print the echoed message
                    data = await reader.read(1024)
                    logging.info(f"Client received: {data.decode()}")

                # Close the connection after 'exit'
                logging.info("Client: Closing connection")
                writer.close()
                await writer.wait_closed()
                return  # Exit after successful communication

            except (ConnectionRefusedError, OSError) as e:
                logging.warning(f"Client: Failed to connect with {family}, trying next address: {e}")
                continue

        logging.error("Client: Unable to connect to the server on any address")

    except socket.gaierror as e:
        logging.error(f"Client: Address resolution error - {e}")

# Run the client with a persistent connection
asyncio.run(tcp_echo_client("localhost"))

