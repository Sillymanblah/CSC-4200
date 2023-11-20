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
from threading import Thread
import termios, sys, tty
# Collecting all the shared functions from our extra files.
from connection_handling import *
from packet_handling import *
from PIR_Sensor import PollPIR

# Fun extra work
def keyboard_wait():
    fd = sys.stdin.fileno()
    try:
        old_settings = tty.setraw( fd )
        ch = sys.stdin.read( 1 ) # Get the next character typed.
    finally:
        termios.tcsetattr( fd, termios.TCSADRAIN, old_settings )

# This will be a 3-way handshake, client sends 2, server sends 1.
# Client sends the initial message with a syn number.
# Server sends it's own syn number and an ack back.
# Client acks the last syn and ends the handshake, beginning communications.
def client_handshake( conn: socket.socket ):
    try:
        # Create a sequence number for the communication.
        seq_num = random.randint(1000, 10000) # Max size of seq_num is 4,000,000,000

        # Create header
        header = build_header( seq_num=seq_num, ack_num=0, ack='N', syn='Y', fin='N' )

        # Send client header
        conn.send( header )

        # Increment by bytes sent
        seq_num += 12

        # The loop is so that we keep trying to recieve a header until the correct one makes it to us.
        while True:
            # Receive server header, validating incoming data with
            server_header = receive_header( conn, seq_num )

            # Server header contains: server_seq (our ack_num), server_ack (our seq_num), ack, syn, fin.
            ( server_seq_num, server_ack_num, ack, syn, fin ) = server_header

            # If the server's message matches our seq_num and has the syncronize bit set, set up our communication.
            if ( ack == 'Y' and syn == 'Y' and fin == 'N' ):
                ack_num = server_seq_num + 12
                break

        # Create new header
        header = build_header( seq_num=seq_num, ack_num=ack_num, ack='Y', syn='N', fin='N' )

        # Send header
        conn.send( header )
        
        # Increment by bytes sent
        seq_num += 12

        # Returning our sequence and acknowledgement numbers for further communications.
        return [ seq_num, ack_num ] # Using a list because it is mutable and therefore can continue to be modified.

    except socket.error:
        raise socket.error( 'Failed the 3 way handshake with the server.' )
    
def communicate( conn: socket.socket, nums: list, command: str, *bits ):
    if nums[0] is not int or nums[1] is not int:
        raise ValueError( 'Bad call to the communicate function, list items are not numbers.' )
    # Create the packet with our command.
    packet = create_packet( nums[0], nums[1], *bits, command )
    nums[0] += len( packet ) # Increments seq_num

    # Send the packet.
    try:
        conn.send( packet )
    except socket.error as exc:
        send_exc = socket.error( 'Packet send to server failed...\n' )
        raise send_exc from exc

    while ( True ):
        try:
            server_packet = receive_packet( conn, nums[0] )
            break
        except socket.error as exc:
            receive_exc = socket.error( 'Packet recieve from server failed...\n' )
            raise receive_exc from exc
        except ValueError as exc:
            logging.info( 'Ignoring invalid packet.', exc )
        

    # Break the tuple apart.
    *header, payload = server_packet

    # Logging the response and gracefully ending.
    logging.info( 'Received message: "{}"'.format( payload ) )

# Main implementation for the client:
if ( __name__ == '__main__' ):
    # Parser to get the server, port, and logfile.
    parser = argparse.ArgumentParser( description='Parser for the client of the light-server program.' )
    parser.add_argument( '--server', '-s', type=str, required=True, help='Server IP address' )
    parser.add_argument( '--port', '-p', type=int, required=True, help='Server port address' )
    parser.add_argument( '--log_file', '-l', type=str, required=True, help='The file the client logs to' )

    # Acquiring the data from the parser in a tuple that can be broken later.
    args = parser.parse_args()
    
    # Configure logging settings
    logging.basicConfig( filename=args.log_file, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d-%H-M-%S', filemode='a' )

    # Opening a socket for the client using with so it will auto close.
    with socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP ) as client:

        # Putting the whole thing in a try so we can catch and handle exceptions that break the flow at the end.
        try:
            # Trying to connect the server 5 times:
            for tries in range( 1, 6 ):
                try:
                    # Using the parser arguments to do so.
                    client.connect( ( args.server, args.port ) )
                    break
                except socket.error as exc:
                    logging.error( 'Server connection attempt #%s failed...', tries )
                    logging.error( exc )
                    
                    # If we are on our 5th failure:
                    if ( tries == 5 ):
                        raise socket.error( 'Server failed to respond 5 times, make sure it is online and reachable and try agian.' )

            ## We start by sending a handshake to the server:
            nums = client_handshake()

            ## After that handshake we are good to work with the sensor.
            logging.info( 'Client connected to server at {}:{} and completed the handshake.\nWaiting for sensor...'.format( args.server, args.port ) )
            print( 'Press any key to exit the program' )

            # Opening a thread to keep track of a keyboard input to end the client
            exit_call = Thread( keyboard_wait )
            exit_call.run()

            prev_sensed = PollPIR() # Initial value set

            while ( exit_call.is_alive() ): # As long as we have not had an interrupt
                sensed = PollPIR()

                # If our sensor state did not change, go to the next iteration
                if prev_sensed == sensed:
                    continue

                # Otherwise, we can check to see if we got a True value
                else:
                    if sensed == True: # If we sensed something new, send the communication.
                        communicate( conn=client, nums=nums, bits=('N', 'N', 'N'), command=':Motion Detected')

                    prev_sensed = sensed # Set this for the next iteration
                
            # Once a keyboard interrupt is found, exit
            print( 'Ending program due to an interupt...' )
            communicate( conn=client, nums=nums, bits=('N', 'N', 'Y') , command=':Closing Connection')

        # Catching all our errors.
        except socket.error as exc:
            logging.error( 'There appears to have been an error with network communications:' )
            logging.error( exc )
        except ValueError as exc:
            logging.error( 'There seems to have been an issue with a function value:' )
            logging.error( exc )
        except exc:
            logging.error( 'An unknown error occured:' )
            logging.error( exc )
        # If no errors occured, log success of communication.
        else:
            logging.info( 'Successful server communication, closing the socket.' )
        # Finally, logging the closing of the communication.
        finally:
            logging.info( 'Closing client connection to the server.' )

