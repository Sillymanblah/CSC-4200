# Title: Client.py
# Date: 11/7/2023
# Description: Client file for Program 4 of CSC-4200 (Networks)
# Purpose: Establish a connection to a server and send a command based on a sensor input.
# Required files:
#       connection_handling.py  packet_handling.py 

import argparse
import socket
import logging
import random
# Collecting all the shared functions from our extra files.
from connection_handling import *
from packet_handling import *
# from PIR_Sensor import PollPIR

HEADER_SIZE = 16

# This will be a 3-way handshake, client sends 2, server sends 1.
# Client sends the initial message with a syn number.
# Server sends it's own syn number and an ack back.
# Client acks the last syn and ends the handshake, beginning communications.
def client_handshake( sock: socket.socket, addr ):
    try:
        # Create a sequence number for the communication.
        seq_num = random.randint( 1000, 1000000 ) # Max size of seq_num is 4,000,000,000

        # Create header
        header = build_header( seq_num, 0, b'N', b'Y', b'N', HEADER_SIZE )

        # Send client header
        sock.sendto( header, addr )

        # Increment by bytes sent
        seq_num += HEADER_SIZE

        # The loop is so that we keep trying to recieve a header until the correct one makes it to us.
        while True:
            # Server header contains: server_seq (our ack_num), server_ack (our seq_num), ack, syn, fin.
            ( server_seq_num, server_ack_num, ack, syn, fin, size, addr ) = receive_header( sock )

            # If the server's message matches our seq_num and has the syncronize bit set, set up our communication.
            if ( ack == b'Y' and syn == b'Y' and fin == b'N' and server_ack_num == seq_num ):
                ack_num = server_seq_num + size
                break

        # Create new header
        header = build_header( seq_num, ack_num, b'Y', b'N', b'N', HEADER_SIZE )

        # Send header
        sock.sendto( header, addr )
        
        # Increment by bytes sent
        seq_num += HEADER_SIZE

        # Returning our sequence and acknowledgement numbers for further communications.
        return ( seq_num, ack_num ) # Using a list because it is mutable and therefore can continue to be modified.

    except socket.error:
        raise socket.error( 'Failed the 3 way handshake with the server.' )
    
def communicate( sock, addr, end: bool, command: str, seq_num: int, ack_num: int):
    if end:
        fin = b"Y"
    else:
        fin = b"N"

    # Create the packet with our command.
    header = build_header( seq_num, ack_num, b"Y", b"N", fin, HEADER_SIZE + len(command) )
    payload = command.encode()
    seq_num += HEADER_SIZE + len(command) # Increments seq_num

    # Send the packet in 2 parts.
    sock.sendto( header, addr )
    sock.sendto( payload, addr )

    while ( True ):
        *header, size, payload, addr = receive_packet( sock )
        # Server header contains: server_seq (our ack_num), server_ack (our seq_num), ack, syn, fin.
        ( server_seq_num, server_ack_num, ack, syn, fin ) = header

        # If the server's message matches our seq_num and has the syncronize bit set, set up our communication.
        if ( ack == b'Y' and syn == b'N' and server_ack_num == seq_num ):
            ack_num = server_seq_num + size
            break

    # Logging the response and gracefully ending.
    logging.info( 'Received message: "{}"'.format( payload ) )

    return ( seq_num, ack_num ) # Returning the nums for further use.

# Main implementation for the client:
if ( __name__ == '__main__' ):
    # Parser to get the server, port, and logfile.
    parser = argparse.ArgumentParser( description='Parser for the client of the light-server program.' )
    parser.add_argument( '--server', '-s', type=str, required=True, help='Server IP address' )
    parser.add_argument( '--port', '-p', type=int, required=True, help='Server port address' )
    parser.add_argument( '--log_file', '-l', type=str, required=True, help='The file the client logs to' )

    # Acquiring the data from the parser in a tuple that can be broken later.
    args = parser.parse_args()

    addr = ( args.server, args.port )
    
    # Configure logging settings
    logging.basicConfig( filename=args.log_file, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d-%H-%M-%S', filemode='a' )

    # Opening a socket for the client using with so it will auto close.
    with socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP ) as client:

        # Putting the whole thing in a try so we can catch and handle exceptions that break the flow at the end.
        try:
            print("attempting handshake")
            ## We start by sending a handshake to the server:
            nums = client_handshake( client, addr )

            ## After that handshake we are good to work with the sensor.
            logging.info( 'Client connected to server at {}:{} and completed the handshake.'.format( args.server, args.port ) )
            # print( 'Press any key to exit the program' )

            # Prepping the blink info.
            num_blinks = input( "Input the number of blinks: " )
            duration = input( "Input the duration of each blink: " )
            command = "blinks: {}, duration: {}".format( num_blinks, duration )

            nums = communicate( client, addr, False, command, *nums )

            # Opening a thread to keep track of a keyboard input to end the client
            # exit_call = Thread( keyboard_wait )
            # exit_call.start()

            prev_sensed = True # Initial value set
            try:
                while ( True ): # As long as we have not had an interrupt
                    sensed = input("T/F: ")

                    if sensed == "T":
                        sensed = True
                    elif sensed == "F":
                        sensed = False
                    else:
                        continue

                    # If our sensor state did not change, go to the next iteration
                    if prev_sensed == sensed:
                        continue

                    # Otherwise, we can check to see if we got a True value
                    else:
                        if sensed == True: # If we sensed something new, send the communication.
                            print (nums)
                            nums = communicate( client, addr, False, ':Motion Detected', *nums )

                        prev_sensed = sensed # Set this for the next iteration
            except KeyboardInterrupt:
                # Once a keyboard interrupt is found, exit
                print( 'Ending program due to an interupt...' )
                nums = communicate( client, addr, True, ':Closing Connection', *nums)

        # Catching all our errors.
        except socket.error as exc:
            logging.error( 'There appears to have been an error with network communications:' )
            logging.error( exc )
        except ValueError as exc:
            logging.error( 'There seems to have been an issue with a function value:' )
            logging.error( exc )
        except Exception as exc:
            logging.error( 'An unknown error occured:' )
            logging.error( exc )
        # If no errors occured, log success of communication.
        else:
            logging.info( 'Successful server communication, closing the socket.' )
        # Finally, logging the closing of the communication.
        finally:
            logging.info( 'Closing client connection to the server.' )

