# Title: connection_handling.py
# Authors: John Grzegorczyk (Creator/editor of the file)
#          Madison Kellione (Author of the code)
# Date: 10/18/2023
# Description: Connections helper file for Program 3 of CSC-4200 (Networks)
# Purpose: Use a connection to a client/server to send and recieve built packets.
# Required files:
#       connection_handling.py  packet_handling.py 

import struct
import socket
import logging

def unpack_packet(conn: socket, header_format: str):
    # TODO: Implement header unpacking based on received bytes
    header_size = struct.calcsize(header_format)
    header_data = conn.recv(header_size)
    unpacked_header = struct.unpack(header_format, header_data)
    
    # return the header tuple - this will be the payload
    return unpacked_header

# Could not decide whether I wanted to do this as a default value or
def receive_packet(conn: socket, header_format: str = '!3I'):
    # receive packet header from the function and break the tuple and message
    (version, message_type, message_length) = unpack_packet(conn, header_format)
    client_message = conn.recv(message_length)
    message_decoded = client_message.decode()

    # Logging the header information
    logging.info("Received Data: version: {}, message_type: {}, length: {}\n".format(version, message_type, message_length))

    if (version != 17):
        raise ValueError('VERSION MISMATCH')

    return version, message_type, message_length, message_decoded
