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
# from threading import Thread
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

    try:
        num_blinks = int( blinks )
        duration = float( dur )
    except:
        logging.error("Type cast (str -> num) failure.")

    return ( duration, num_blinks )

def server_handshake(sock: socket.socket):
    try:
        seq_num = random.randint( 1000, 1000000 ) # Max size can be 4,000,000,000

        while True:
            # Client header contains: client_seq (our ack_num), client_ack (our seq_num), ack, syn, fin.
            ( client_seq_num, client_ack_num, ack, syn, fin, size, addr) = receive_header( sock )

            # If the client's message matches our seq_num and has the syncronize bit set, set up our communication.
            if ( ack == b'N' and syn == b'Y' and fin == b'N' ):
                ack_num = client_seq_num + size
                break

        # Create the handshake header and send it
        header = build_header( seq_num, ack_num, b"Y", b"Y", b"N", HEADER_SIZE )
        sock.sendto( header, addr )

        seq_num += HEADER_SIZE # Sending data increments the seq_num

        while True:
            # Client header contains: client_seq (our ack_num), client_ack (our seq_num), ack, syn, fin.
            ( client_seq_num, client_ack_num, ack, syn, fin, size, addr ) = receive_header( sock )

            # If the client's message matches our seq_num and has the syncronize bit set, set up our communication.
            if ( ack == b'Y' and syn == b'N' and fin == b'N' and client_ack_num == seq_num ):
                ack_num = client_seq_num + size
                break

        return ( seq_num, ack_num, addr )
    
    except socket.error:
        raise socket.error( "Failed to do a three way handshake with the client." )

def communicate(conn: socket.socket, seq_num: int, ack_num: int):
    end_connection = False

    # Need to type this (probably can copy code)
    while True:
        # Client header contains: client_seq (our ack_num), client_ack (our seq_num), ack, syn, fin.
        ( *header, size, payload, client ) = receive_packet( conn )

        client_seq_num, client_ack_num, ack, syn, fin = header

        # If the client's message matches our seq_num and has the syncronize bit set, set up our communication.
        if ( ack == b'Y' and syn == b'N' and client_ack_num == seq_num ):
            ack_num = client_seq_num + size
            if ( fin == b"Y" ):
                end_connection = True
            break

    logging.info( "Message recieved: {}".format( payload ) )


    if payload == ":Motion Detected":
        command = ":Successful Light Operation"
    elif end_connection:
        command = ":Closing connection"
    else:
        command = ":Unknown command"

    # Building and sending packet in parts.
    header = build_header( seq_num, ack_num, b"Y", b"N", fin, HEADER_SIZE + len(command) )
    new_payload = command.encode()
    conn.sendto( header, client )
    conn.sendto( new_payload, client )
    seq_num += HEADER_SIZE + len(command)

    return ( seq_num, ack_num, payload, end_connection )

# This will be the function that is used for every communication with a client.
# It is still a mess of stuff that will not be needed (from program 3), so I will continue to prune and clean it.
def client_communicate(conn: socket.socket, seq_num: int, ack_num: int):
    try:
        seq_num, ack_num, blink_payload, end_connection = communicate( conn, seq_num, ack_num )

        blink_data = get_blink_data(blink_payload)

        # Communicate until told to stop.
        while not end_connection:
            seq_num, ack_num, payload, end_connection = communicate( conn, seq_num, ack_num )

            if ( payload == ":Motion Detected" ):
                BlinkLed(*blink_data)

        logging.info( "Completed communication with {}".format( addr ) )
                
    except Exception as exc:
        logging.error(exc)
        raise Exception( "Connection with {} failed.".format( addr ) )

if __name__ == '__main__':
    # Server takes 2 arguments: port & log file location
    parser = argparse.ArgumentParser( description="Light Server Argument Parser" )
    parser.add_argument( '--port', '-p', type=int, required=True, help='Port server listens on' )
    parser.add_argument( '--log_file_location', '-l', type=str, required=True, help='Log File location that stores record of actions' )

    args = parser.parse_args()
    host = socket.gethostbyname("localhost")
    port = args.port
    log_location = args.log_file_location

    # Configure logging settings
    logging.basicConfig( filename=log_location, level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d-%H-%M-%S', filemode='a' )

    with socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP ) as server:
        # Bind the socket to the server address
        try:
            server.bind( (host, port) )
        except OSError:
            print("\nOSError: Socket failed to bind to that address.")
        except ValueError:
            print("\nInvalid Port Number.")

        logging.info('Server has started and is waiting for connections on {}:{}'.format(host,port))
        while True:
            # Wait for a client to connect
            try:
                *nums, addr = server_handshake( server )
                # Noting the opened connection.
                print("Received handshake from (IP, PORT): ", addr )
                logging.info("Received handshake from {}".format(addr))
                
            except KeyboardInterrupt:
                print("\nAccept operation interrupted by keyboard input. Connection ended.")
                continue # If connection fails, we need to not try to use it and instead listen
                        ## NOTE: If the threading line was also in the try with the accept we do not need the continue.

            try: # The attempt to do multithreading seems to not have worked for UDP (I had it working for TCP).
                # Thread(target=client_communicate, args=(server, nums)).start() # This opens a thread to handle the connections, while we still listen in the loop.
                client_communicate(server, *nums)
            except Exception as exc:
                logging.error(exc) # Logging any and all errors.
            
            