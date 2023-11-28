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

HEADER_SIZE = 16

def get_blink_data(payload: str):
    pair = payload.split(",")

    blinks = ""
    for char in pair[0]:
        if ( char.isdigit() ):
            blinks += char
    
    dur = ""
    for char in pair[1]:
        if ( char.isdecimal() or char.isdigit() ):
            dur += char

    num_blinks = int( blinks )
    duration = float( dur )

    return ( num_blinks, duration )

def server_handshake(conn: socket.socket):

    try:
        seq_num = random.randint( 1000, 1000000 ) # Max size can be 4,000,000,000

        while True:
            # Client header contains: client_seq (our ack_num), client_ack (our seq_num), ack, syn, fin.
            ( client_seq_num, client_ack_num, ack, syn, fin ) = receive_header( conn )

            # If the client's message matches our seq_num and has the syncronize bit set, set up our communication.
            if ( ack == 'N' and syn == 'Y' and fin == 'N' ):
                ack_num = client_seq_num + HEADER_SIZE
                break

        # Create the handshake header and send it
        header = build_header( seq_num=seq_num, ack_num=ack_num, ack="Y", syn="Y", fin="N" )
        conn.send(header)

        seq_num += HEADER_SIZE # Sending data increments the seq_num

        while True:
            # Client header contains: client_seq (our ack_num), client_ack (our seq_num), ack, syn, fin.
            ( client_seq_num, client_ack_num, ack, syn, fin ) = receive_header( conn )

            # If the client's message matches our seq_num and has the syncronize bit set, set up our communication.
            if ( ack == 'Y' and syn == 'N' and fin == 'N' and client_ack_num == seq_num ):
                ack_num = client_seq_num + HEADER_SIZE
                break

        return ( seq_num, ack_num )
    
    except socket.error:
        raise socket.error( "Failed to do a three way handshake with the client." )

def communicate(conn: socket.socket, seq_num: int, ack_num: int):
    end_connection = False

    # Need to type this (probably can copy code)
    while True:
        # Client header contains: client_seq (our ack_num), client_ack (our seq_num), ack, syn, fin.
        ( client_seq_num, client_ack_num, ack, syn, fin, payload ) = receive_packet( conn )

        # If the client's message matches our seq_num and has the syncronize bit set, set up our communication.
        if ( ack == 'Y' and syn == 'N' and client_ack_num == seq_num ):
            ack_num = client_seq_num + HEADER_SIZE + len( payload )
            if ( fin == "Y" ):
                end_connection = True
            break

    # Building and sending packet.
    packet = create_packet( seq_num=seq_num, ack_num=ack_num, ack="Y", syn="N", fin=fin, payload=payload )
    conn.send( packet )
    seq_num += len( packet )

    return ( seq_num, ack_num, payload, end_connection )

# This will be the function that is used for every communication with a client.
# It is still a mess of stuff that will not be needed (from program 3), so I will continue to prune and clean it.
def client_communicate(conn: socket.socket, addr):
    try:
        # Noting the opened connection.
        print("Received connection from (IP, PORT): ", addr )
        logging.info("Received connection from {}".format(addr))

        with conn:
            # Perform a 3-way handshake.
            server_handshake( conn )

            logging.info( "Completed handshake with {}".format( addr ) )

            *nums, blink_payload, end_connection = communicate( conn, *nums )

            blink_data = get_blink_data(blink_payload)
                
            # Communicate until told to stop.
            while not end_connection:
                *nums, payload, end_connection = communicate( conn, *nums )

                if ( payload == ":Motion Detected" ):
                    BlinkLed(*blink_data)

            logging.info( "Completed communication with {}".format( addr ) )
                
    except Exception as exc:
        raise Exception( "Connection with {} failed:".format( addr ) ) from exc



if __name__ == '__main__':
    # Server takes 2 arguments: port & log file location
    parser = argparse.ArgumentParser( description="Light Server Argument Parser" )
    parser.add_argument( '--port', '-p', type=int, required=True, help='Port server listens on' )
    parser.add_argument( '--log_file_location', '-l', type=str, required=True, help='Log File location that stores record of actions' )

    args = parser.parse_args()

    host = "10.128.0.3" # There might be a way to set this up so the computer finds its own port.
    port = args.port
    log_location = args.log_file_location

    # Configure logging settings
    logging.basicConfig( filename=log_location, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d-%H-M-%S', filemode='a' )

    with socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP ) as server:
        # Bind the socket to the server address
        try:
            server.bind( (host, port) )
        except OSError:
            print("\nOSError: Socket failed to bind to that address.")
        except ValueError:
            print("\nInvalid Port Number.")

        # Listen for incoming connections
        try: # Will probably move this to 
            server.listen(5) # Setting a backlog of 5 connections, so that we can handle multiple connections.
            print("\nServer is listening on {}:{}\n".format(host,port))
        except OSError:
            print("\nOSError: Socket listen failed.") # NOTE: With this how it is, a socket listen failure will still send us into the loop forever.
        
        logging.info('Server has started and is listening for connections on {}:{}'.format(host,port))
        while True:
            # Wait for a client to connect
            try:
                conn_info = server.accept()
            except KeyboardInterrupt:
                print("\nAccept operation interrupted by keyboard input. Connection ended.")
                continue # If connection fails, we need to not try to use it and instead listen
                        ## NOTE: If the threading line was also in the try with the accept we do not need the continue.

            try:
                Thread(target=client_communicate, args=conn_info).start() # This opens a thread to handle the connections, while we still listen in the loop.
            except Exception as exc:
                logging.error(exc) # Logging any and all errors.
            
            