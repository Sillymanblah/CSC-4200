# Title: Client.py
# Authors: John Grzegorczyk
# Date: 10/19/2023
# Description: Client file for Program 3 of CSC-4200 (Networks)
# Purpose: Establish a connection to a server and send a command for the program to run.
# Required files:
#       connection_handling.py  packet_handling.py 

import argparse
import socket
import logging
# Collecting all the shared functions from our extra files.
from connection_handling import *
from packet_handling import *

# Global declaration that version is 17
VERSION = 17

# Function to get a message from the user within a size constraint.
def get_message(max_size: int = None, specification: str = 'message'):
    message = input('Please type a %s to send to the server:' % specification)
    if (len(message) > max_size):
        raise ValueError('Size of input string was longer than allowed.')
    return message

# Main implementation for the client:
if (__name__ == '__main__'):
    # Parser to get the server, port, and logfile
    parser = argparse.ArgumentParser(description='Parser for the client of the light-server program.')
    parser.add_argument('--server', type=str, required=True, help='Server IP address')
    parser.add_argument('--port', type=int, required=True, help='Server port address')
    parser.add_argument('--log_file', type=str, required=True, help='The file this document logs to')

    # Acquiring the data from the parser in a tuple that can be broken later.
    args = parser.parse_args()
    
    # Configure logging settings
    logging.basicConfig(filename=parser.log_file, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

    # Opening a socket for the client using with so it will auto close.
    with socket.socket() as client:
    
        # Putting the whole thing in a try so we can catch and handle exceptions that break the flow at the end.
        try:
            # We are not connected, now try to connect
            connected = False

            # Trying to connect the server 5 times:
            for tries in range(1,6):
                try:
                    # Using the parser arguments to do so.
                    client.connect((parser.server, parser.port))
                    # Variable set if we actually connected.
                    connected = True
                except socket.error as exc:
                    print('Server connection attempt #%s failed...', tries)
                    print(exc)

            if (not connected):
                raise socket.error('Server failed to respond 5 times, make sure it is online and reachable and try agian.')
            
            ## We start by sending a greeting to the server:

            # Asking the user for a message to greet the server.
            message = get_message(8, 'message')
            # Type does not matter here.
            message_type = 0

            # Get our packet to send across the network.
            packet = create_packet(VERSION, message_type, len(message), message)

            # Performing the transmissions across the network.
            try:
                client.send(packet)
            except socket.error as exc:
                new_exc = socket.error('Packet send to server failed...\n')
                raise new_exc from exc

            try:
                packet = receive_packet(client)
            except socket.error as exc:
                new_exc = socket.error('Packet recieve from server failed...\n')
                raise new_exc from exc

            ## Now we need to send the command:

            # Getting the command from the user to send to the server.
            command = get_message(8, 'command')

            if (command == 'LIGHTON'):
                message_type = 1
            elif (command == 'LIGHTOFF'):
                message_type = 2
            else:
                message_type = 0

            # Get our packet to send across the network.
            command_packet = create_packet(VERSION, message_type, len(command), command)

            # Second transmission on the network
            try:
                client.send(command_packet)
            except socket.error as exc:
                new_exc = socket.error('Packet send to server failed...\n')
                raise new_exc from exc

            try:
                success_packet = receive_packet(client)
            except socket.error as exc:
                new_exc = socket.error('Packet recieve from server failed...\n')
                raise new_exc from exc

        except socket.error as exc:
            print('There appears to have been an error with network communications:')
            print(exc)
        except:
            pass
