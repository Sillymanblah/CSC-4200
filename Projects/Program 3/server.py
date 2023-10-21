# server.py
#   Server accepts connections, receives custom packets from clients, logs actions, and executes
#       command for LIGHT ON/OFF.

import argparse
import socket
import logging
# Collecting our personal functions:
from connection_handling import *
from packet_handling import *

if __name__ == '__main__':
    # Server takes 2 arguments: port & log file location
    parser = argparse.ArgumentParser(description="Light Server Argument Parser")
    parser.add_argument('--port', type=int, required=True, help='Port server listens on')
    parser.add_argument('--log_file_location', type=str, required=True, help='Log File location that stores record of actions')

    args = parser.parse_args()

    host = "127.0.0.1"
    port = args.port
    log_location = args.log_file_location

    # Configure logging settings
    logging.basicConfig(filename=log_location, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

    # Specify the header format
    # header_format = 'BBBH'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address
        try:
            s.bind((host, port))
        except OSError:
            print("\nOSError: Invalid address.")
        except ValueError:
            print("\nInvalid Port Number.")

        # Listen for incoming connections
        try:
            s.listen()
            print("\nServer is listening on", host, "\n")
        except OSError:
            print("\nOSError: Socket listen failed.")

        # Wait for a client to connect
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            print("\nAccept operation interrupted by keyboard input. Connection ended.")
            
        with conn:
            print("Received connection from (IP, PORT): ('", addr, "', ", port, ")" )
            logging.info("Received connection from <", addr, ",", port, ">")
            while True:
                # Receive and unpack HELLO packet
                try:
                    version, message_type, message_length, message = receive_packet(conn)
                except socket.error as exc:
                    logging.error('Packet recieve from client failed')
                except ValueError as exc:
                    logging.error(exc) # This catches a version mismatch
                    continue
                
                logging.info('Received "{}" from client'.format(message))

                # send hello packet to client
                try:
                    conn.send(server_hello)
                except socket.error:
                    print("\nFailed to send.")

                # Receive and unpack COMMAND packettry:
                try:
                    version, message_type, message_length, command = receive_packet(conn)
                except socket.error as exc:
                    logging.error('Packet recieve from client failed')
                except ValueError as exc:
                    logging.error(exc) # This catches a version mismatch
                    continue
    
                # Check if version is correct value
                if version != 17: # We can probably remove this because the recieve function will handle it.
                    print("VERSION MISMATCH. Return to listening.")
                    logging.info("VERSION MISMATCH. Return to listening.")
                    continue

                else:
                    print("VERSION ACCEPTED")
                    logging.info("VERSION ACCEPTED")

                    # Message Type = 1 --> LIGHT ON
                    if message_type == 1 and command == "LIGHTON":
                        print("EXECUTING SUPPORTED COMMAND: LIGHTON")
                        print("Returning SUCCESS")
                        logging.info("EXECUTING SUPPORTED COMMAND: LIGHTON")

                    # Message Type = 2 --> LIGHT OFF
                    elif message_type == 2 and command == "LIGHTOFF":
                        print("EXECUTING SUPPORTED COMMAND: LIGHTOFF")
                        print("Returning SUCCESS")
                        logging.info("EXECUTING SUPPORTED COMMAND: LIGHTOFF")

                    # Any other message type is not supported
                    else:
                        print("IGNORING UNKNOWN COMMAND: {command}")
                        logging.info("RECEIVED UNKNOWN COMMAND: {command}")
                        
                    # create (server_success) packet
                    success = 'SUCCESS'                
                    server_success = create_packet(version, message_type, message_length, success)

                    # send SUCCESS packet to client
                    try:
                        conn.send(server_success)
                    except socket.error:
                        print("\nFailed to send.")

