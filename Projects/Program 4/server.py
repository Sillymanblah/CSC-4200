# Title: Server.py
# Date: 11/7/2023
# Description: Client file for Program 4 of CSC-4200 (Networks)
# Purpose: Accept connections from clients and perform commands on a light.
# Required files:
#       connection_handling.py  packet_handling.py 

import argparse
import socket
import logging
# Between multiprocessing and multithreading, multithreading seems to work a little better for what we are doing here.
from threading import Thread
import random # Necessary to send SYN
# Collecting our personal functions:
from connection_handling import *
from packet_handling import *
from LED import BlinkLed

VERSION = 17

def server_handshake(conn: socket.socket):

    # Need to type this.

    return (seq_num, ack_num)

def communicate(conn: socket.socket):

    # Need to type this (probably can copy code)

    return

# This will be the function that is used for every communication with a client.
# It is still a mess of stuff that will not be needed (from program 3), so I will continue to prune and clean it.
def client_communicate(conn: socket.socket):
    with conn:
        print("Received connection from (IP, PORT): ", addr )
        logging.info("Received connection from {}".format(addr))

        # Perform a 3-way handshake.
        try:
            # This should be close to how the data will be formatted, might need to modify it slightly.
            server_handshake(conn)
        except socket.error:
            logging.error('Packet recieve from client failed')
            return # Failed handshake drops connection
        

        # Receive and unpack COMMAND packet:
        try:
            *header, command = receive_packet(conn)
        except socket.error:
            logging.error('Packet recieve from client failed')
            return # Failed command drops connection

        # Log the interaction
            
        # Communicate until told to stop.
        while True:
            (client_seq_num, client_ack_num, ack, syn, fin, payload) = communicate(conn)

            if (fin == 'Y'):
                return



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
    logging.basicConfig(filename=log_location, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d-%H-M-%S', filemode='a')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the server address
        try:
            s.bind((host, port))
        except OSError:
            print("\nOSError: Socket failed to bind to that address.")
        except ValueError:
            print("\nInvalid Port Number.")

        # Listen for incoming connections
        try: # Will probably move this to 
            s.listen(5) # Setting a backlog of 5 connections, so that we can handle multiple connections.
            print("\nServer is listening on {}:{}\n".format(host,port))
        except OSError:
            print("\nOSError: Socket listen failed.") # NOTE: With this how it is, a socket listen failure will still send us into the loop forever.
        
        logging.info('Server has started and is listening for connections on {}:{}'.format(host,port))
        while True:
            # Wait for a client to connect
            try:
                conn, addr = s.accept()
            except KeyboardInterrupt:
                print("\nAccept operation interrupted by keyboard input. Connection ended.")
                continue # If connection fails, we need to not try to use it and instead listen
                        ## NOTE: If the threading line was also in the try with the accept we do not need the continue.

            try:
                Thread(target=client_communicate, args=(conn,)) # This opens a thread to handle the connections, while we still listen in the loop.
            except:
                pass # The exception handling for this will probably need to have one for a multithread failure, one for socket error,
                    ## and maybe 2 more (one for handling mis-comms, one for a general catch of anything that gets missed).
            
            