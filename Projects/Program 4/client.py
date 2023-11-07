# Title: Client.py
# Date: 11/7/2023
# Description: Client file for Program 4 of CSC-4200 (Networks)
# Purpose: Establish a connection to a server and send a command based on a sensor input.
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
    # Parser to get the server, port, and logfile.
    parser = argparse.ArgumentParser(description='Parser for the client of the light-server program.')
    parser.add_argument('--server', '-s', type=str, required=True, help='Server IP address')
    parser.add_argument('--port', '-p', type=int, required=True, help='Server port address')
    parser.add_argument('--log_file', '-l', type=str, required=True, help='The file the client logs to')

    # Acquiring the data from the parser in a tuple that can be broken later.
    args = parser.parse_args()
    
    # Configure logging settings
    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', filemode='a')

    # Opening a socket for the client using with so it will auto close.
    with socket.socket() as client:
    
        # Putting the whole thing in a try so we can catch and handle exceptions that break the flow at the end.
        try:
            # Trying to connect the server 5 times:
            for tries in range(1,6):
                try:
                    # Using the parser arguments to do so.
                    client.connect((args.server, args.port))
                    break
                except socket.error as exc:
                    logging.error('Server connection attempt #%s failed...', tries)
                    logging.error(exc)
                    
                    # If we are on our 5th failure:
                    if (tries == 5):
                        raise socket.error('Server failed to respond 5 times, make sure it is online and reachable and try agian.')

            ## We start by sending a greeting to the server:

            # Asking the user for a message to greet the server.
            message = get_message(8, 'message')
            # Type does not matter here.
            message_type = 0

            # Get our packet to send across the network.
            packet = create_packet(VERSION, message_type, len(message), message)

            logging.info('Sending HELLO packet')
            # Performing the transmissions across the network.
            try:
                client.send(packet)
            except socket.error as exc:
                send_exc = socket.error('Packet send to server failed...\n')
                raise send_exc from exc

            try:
                packet_tuple = receive_packet(client)
            except socket.error as exc:
                receive_exc = socket.error('Packet recieve from server failed...\n')
                raise receive_exc from exc

            # We are able to just say accepted because the receive packet function throws an error if there is a mismatch
            logging.info('VERSION ACCEPTED')
            
            # Breaking the packet tuple.
            version, message_type, message_length, server_message = packet_tuple

            # Logging the server response.
            logging.info('Received message: "{}"'.format(server_message))

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
            packet = create_packet(VERSION, message_type, len(command), command)

            logging.info('Sending command packet')
            # Second transmission on the network
            try:
                client.send(packet)
            except socket.error as exc:
                send_exc = socket.error('Packet send to server failed...\n')
                raise send_exc from exc

            try:
                packet_tuple = receive_packet(client)
            except socket.error as exc:
                receive_exc = socket.error('Packet recieve from server failed...\n')
                raise receive_exc from exc
            
            # Again we know the version is correct.
            logging.info('VERSION ACCEPTED')

            # Break the tuple apart.
            version, message_type, message_length, success = packet_tuple

            # Printing success data.
            logging.info('Received message: "{}"'.format(success))
            if (success == 'SUCCESS'):
                logging.info('Command Successful')

        # Catching all our errors.
        except socket.error as exc:
            logging.error('There appears to have been an error with network communications:')
            logging.error(exc)
        except ValueError as exc:
            logging.error('There seems to have been an issue with a function value:')
            logging.error(exc)
        except exc:
            logging.error('An unknown error occured:')
            logging.error(exc)
        # If no errors occured:
        else:
            logging.info('Successful server communication, closing the socket.')

