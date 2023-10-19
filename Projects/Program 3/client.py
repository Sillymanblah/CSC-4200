# Title: Client.py
# Authors: John Grzegorczyk
# Date: 10/19/2023
# Description: Client file for Program 3 of CSC-4200 (Networks)
# Purpose: Establish a connection to a server and send a command for the program to run.
# Required files:
#       connection_handling.py  packet_handling.py 

import argparse
import socket
import struct
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

    # Opening a socket for the client using with so it will auto close.
    with socket.socket() as client:
    
        # Putting the whole thing in a try so we can catch and handle exceptions that break the flow at the end.
        try:
            # Trying to connect the server 5 times:
            for tries in range(1,6):
                try:
                    # Trying to connect using the parser arguments.
                    client.connect((parser.server, parser.port))
                    # Variable to catch if we actually connected.
                    connected = True
                except socket.error as exc:
                    print('Attempt %s failed...', tries)
                    print(exc)


            ## We start by sending a greeting to the server:

            # Asking the user for a message to greet the server.
            message = get_message(8, 'message')
            # Type does not matter here.
            message_type = 0

            # Building the header out of a tuple of 3 integers, as required.
            header = build_header((VERSION, message_type, len(message)))

            # Encoding the message to transfer.
            data = message.encode()

            # Here is the packet we will send across the network.
            packet = header + data

            # Performing the transmissions across the network.
            try:
                client.send(packet)
            except socket.error as exc:
                new_exc = socket.error('Packet send to server failed...\n')
                raise new_exc from exc

            try:
                receive_packet(client)
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

            # Building the header to use.
            header = build_header((VERSION, message_type, len(command)))

            # Encoding the command to transfer.
            data = command.encode()

            # Creating the packet:
            command_packet = header + data

            # Sending it across the network
            client.send(command_packet)

        except:
            pass
