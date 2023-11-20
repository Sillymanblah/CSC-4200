# Title: Server.py
# Date: 11/7/2023
# Description: Client file for Program 4 of CSC-4200 (Networks)
# Purpose: Accept connections from clients and perform commands on a light.
# Required files:
#       connection_handling.py  packet_handling.py 

import argparse
import socket
import logging
# Collecting our personal functions:
from connection_handling import *
from packet_handling import *
from LED import BlinkLed

VERSION = 17

if __name__ == '__main__':
    # Server takes 2 arguments: port & log file location
    parser = argparse.ArgumentParser(description="Light Server Argument Parser")
    parser.add_argument('--port', '-p', type=int, required=True, help='Port server listens on')
    parser.add_argument('--log_file_location', '-l', type=str, required=True, help='Log File location that stores record of actions')

    args = parser.parse_args()

    host = "10.128.0.3" # There might be a way to set this up so the computer finds its own port.
    port = args.port
    log_location = args.log_file_location

    # Configure logging settings
    logging.basicConfig(filename=log_location, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

    # Specify the header format
    header_format = '3I'

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
            print("\nServer is listening on {}:{}\n".format(host,port))
        except OSError:
            print("\nOSError: Socket listen failed.")
        
        logging.info('Server started and is listening for connections')
        while True:
            # Wait for a client to connect
            try:
                conn, addr = s.accept()
            except KeyboardInterrupt:
                print("\nAccept operation interrupted by keyboard input. Connection ended.")
                continue # If connection fails, we need to not try to use it and instead listen
            
            with conn:
                print("Received connection from (IP, PORT): ", addr )
                logging.info("Received connection from {}".format(addr))
            
                # Receive and unpack HELLO packet
                try:
                    version, message_type, message_length, message = receive_packet(conn)
                except socket.error as exc:
                    logging.error('Packet recieve from client failed')
                    continue # Failed handshake drops connection
                except ValueError as exc:
                    logging.error(exc) # This catches a version mismatch
                    continue
                
                logging.info('Received "{}" from client'.format(message))

                # Create the hello packet.
                hello = 'Hello!'
                server_hello = create_packet(VERSION, message_type, len(hello), hello)

                # send hello packet to client
                try:
                    conn.send(server_hello)
                except socket.error:
                    print("\nFailed to send.")
                    continue # Failed handshake drops connection

                # Receive and unpack COMMAND packettry:
                try:
                    version, message_type, message_length, command = receive_packet(conn)
                except socket.error as exc:
                    logging.error('Packet recieve from client failed')
                    continue # Failed command drops connection
                except ValueError as exc:
                    logging.error(exc) # This catches a version mismatch
                    continue
    
                # Check if version is correct value
                # if version != 17: 
                #     print("VERSION MISMATCH. Return to listening.")
                #     logging.info("VERSION MISMATCH. Return to listening.")
                #     continue

                print("VERSION ACCEPTED")
                logging.info("VERSION ACCEPTED")

                # Message Type = 1 --> LIGHT ON
                if message_type == 1 and command == "LIGHTON":
                    print("EXECUTING SUPPORTED COMMAND: LIGHTON")
                    print("Returning SUCCESS")
                    logging.info("EXECUTING SUPPORTED COMMAND: LIGHTON")
                    success = 'SUCCESS'

                # Message Type = 2 --> LIGHT OFF
                elif message_type == 2 and command == "LIGHTOFF":
                    print("EXECUTING SUPPORTED COMMAND: LIGHTOFF")
                    print("Returning SUCCESS")
                    logging.info("EXECUTING SUPPORTED COMMAND: LIGHTOFF")
                    success = 'SUCCESS'

                # Any other message type is not supported
                else:
                    print("IGNORING UNKNOWN COMMAND: {}".format(command))
                    logging.info("RECEIVED UNKNOWN COMMAND: {}".format(command))
                    success = 'FAILURE'
                    
                # create (server_success) packet
                server_success = create_packet(VERSION, message_type, len(success), success)

                logging.info('Returning {}'.format(success))
                # send SUCCESS packet to client
                try:
                    conn.send(server_success)
                except socket.error:
                    print("\nFailed to send.")

