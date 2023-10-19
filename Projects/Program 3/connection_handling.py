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

def unpack_packet(conn: socket, header_format):
    # TODO: Implement header unpacking based on received bytes
    header_size = struct.calcsize(header_format)
    header_data = conn.recv(header_size)
    unpacked_header = struct.unpack(header_format, header_data)

    # TODO: Create a string from the header fields
    packet_header_as_string = f"Received Data: {unpacked_header}"
    
    # return the string - this will be the payload
    return unpacked_header, packet_header_as_string

def receive_packet(conn, header_format):
    # receive packet header and message
    version, header_length, message_type, message_length = unpack_packet(conn, header_format)[0]
    client_message = conn.recv(message_length)
    message_decoded = client_message.decode()

    # Print Header
    print("Received Data: version: {}, message_type: {}, length: {}\n".format(version, message_type, message_length))

    return version, header_length, message_type, message_length, message_decoded
