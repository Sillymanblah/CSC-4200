# connection_handling.py
# Madison Kellione

import struct
import socket
import logging

def receive_header(conn: socket.socket, header_format: str = '!2Ix3cI'):
    # TODO: Implement header unpacking based on received bytes
    header_size = struct.calcsize(header_format)
    header_data, addr = conn.recvfrom(header_size)
    unpacked_header = struct.unpack(header_format, header_data)

    *header, size = unpacked_header
    log_header("RECV", *header)
    
    # return the header tuple - this will be the payload
    return *unpacked_header, addr

def receive_packet(conn: socket.socket, header_format: str = '!2Ix3cI'):
    # receive packet header from the function and break the tuple and message
    (*header, size, addr) = receive_header(conn, header_format)
    print(size)

    # receive payload from a packet and decode
    client_payload, addr2 = conn.recvfrom(size - struct.calcsize(header_format))
    if addr != addr2:
        raise BufferError( "Received invalid connection" )
    
    payload_decoded = client_payload.decode()

    return *header, size, payload_decoded, addr

def log_header(*args):
    # Logging the header information on client
    logging.info("{}, <Sequence Number: {}> <Acknowledgment Number: {}> [ACK: {}] [SYN: {}] [FIN:{}]".format(*args))
