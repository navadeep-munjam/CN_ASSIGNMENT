import asyncio
import socket
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def tcp_echo_client(host, port, protocol='ipv4'):
    try:
        if protocol == 'ipv4':
            addr_info = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        elif protocol == 'ipv6':
            addr_info = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_STREAM)
        else:
            addr_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)

        for family, socktype, proto, _, sockaddr in addr_info:
            try:
                input0=sockaddr[0]
                input1=sockaddr[1]
                reader, writer = await asyncio.wait_for(asyncio.open_connection(input0, input1, family=family), timeout=5)
                logging.info(f"Client: Connected to server at {sockaddr}")

                while True:
                    message = input("Enter message to send (or type 'exit' to quit): ")
                    if message.lower() == 'exit':
                        logging.info("Client: Exiting.")
                        break

                    # Send the message
                    logging.info(f"Client: Sending '{message}'")
                    writer.write(message.encode())
                    await writer.drain()

                    data = await reader.read(1024)
                    logging.info(f"Client received: {data.decode()}")

                logging.info("Client: Closing connection")
                writer.close()
                await writer.wait_closed()
                return

            except (ConnectionRefusedError, OSError) as e:
                logging.warning(f"Client: Failed to connect with {family}, trying next address: {e}")
                continue
            except asyncio.TimeoutError:
                logging.error("Client: Connection attempt timed out.")
                return
            except Exception as e:
                logging.error(f"Unexpected error occurred: {e}")
                return

        logging.error("Client: Unable to connect to the server on any address")

    except socket.gaierror as e:
        logging.error(f"Client: Address resolution error - {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

host = input("Enter server address (e.g., 127.0.0.1 for IPv4 or ip6-localhost for IPv6): ")
port = int(input("Enter server port: "))
protocol = input("Enter protocol (ipv4/ipv6, default is ipv4): ").lower() or 'ipv4'
asyncio.run(tcp_echo_client(host, port, protocol))




