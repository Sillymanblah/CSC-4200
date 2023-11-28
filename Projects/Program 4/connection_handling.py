# connection_handling.py
# Madison Kellione

import struct
import socket
import logging

def receive_header(conn: socket.socket, header_format: str = '!2Ix3cI'):
    # TODO: Implement header unpacking based on received bytes
    header_size = struct.calcsize(header_format)
    header_data = conn.recv(header_size)
    unpacked_header = struct.unpack(header_format, header_data)
    
    # return the header tuple - this will be the payload
    return unpacked_header

def receive_packet(conn: socket.socket, header_format: str = '!2Ix3cI'):
    # receive packet header from the function and break the tuple and message
    (*header, size) = receive_header(conn, header_format) # Could also just do: header and *header later to decouple.

    # receive payload from a packet and decode
    client_payload = conn.recv(size - 16)
    payload_decoded = client_payload.decode()

    return *header, size, payload_decoded

def log_header(*args):
    # Logging the header information on client
    logging.info("{}, <Sequence Number: {}> <Acknowledgment Number: {}> [ACK: {}] [SYN: {}] [FIN:{}]".format(args=args))
