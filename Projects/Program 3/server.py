# server.py
#   Server accepts connections, receives custom packets from clients, logs actions, and executes
#       command for LIGHT ON/OFF.

import argparse
import socket
import struct
import logging
import connection_handling
import packet_handling

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
    logging.basicConfig(filename=log_location, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
                hello_ver = receive(conn, header_format)[0]
                hello_msg_type = receive(conn, header_format)[2]
                hello_msg_length = receive(conn, header_format)[3]
                hello = receive(conn, header_format)[4]
                logging.info("Received {hello} from client")

                # create (server_hello) packet
                server_hello = create_packet(hello_ver, hello_msg_type, hello_msg_length, hello_msg)

                # send hello packet to client
                try:
                    conn.send(server_hello)
                except socket.error:
                    print("\nFailed to send.")

                # Receive and unpack COMMAND packet
                version = receive(conn, header_format)[0]
                message_type = receive(conn, header_format)[2]
                message_length = receive(conn, header_format)[3]
                command = receive(conn, header_format)[4]
    
                # Check if version is correct value
                if version != 17:
                    print("VERSION MISMATCH. Return to listening.")
                    logging.info("VERSION MISMATCH. Return to listening.")
                    continue

                else:
                    print("VERSION ACCEPTED")
                    logging.info("VERSION ACCEPTED")

                    # Message Type = 1 --> LIGHT ON
                    if message_type == 1:
                        print("EXECUTING SUPPORTED COMMAND: {command}")
                        print("Returning SUCCESS")
                        logging.info("EXECUTING SUPPORTED COMMAND: {command}")

                    # Message Type = 2 --> LIGHT OFF
                    elif message_type == 2:
                        print("EXECUTING SUPPORTED COMMAND: {command}")
                        logging.info("EXECUTING SUPPORTED COMMAND: {command}")

                    # Any other message type is not supported
                    else:
                        print("IGNORING UNKNOWN COMMAND: {command})
                        logging.info("RECEIVED UNKNOWN COMMAND: {command})
                        
                    # create (server_success) packet
                    success = 'SUCCESS'                
                    server_success = create_packet(version, message_type, message_length, success)

                    # send SUCCESS packet to client
                    try:
                        conn.send(server_success)
                    except socket.error:
                        print("\nFailed to send.")

            # Close the client socket
            conn.close()
