# connection_handling.py
# Madison Kellione

import struct
import socket
import logging

def receive_header(conn: socket.socket, ack_num: int, header_format: str = '!2Ix3c'):
    # TODO: Implement header unpacking based on received bytes
    header_size = struct.calcsize(header_format)
    header_data = conn.recv(header_size)
    unpacked_header = struct.unpack(header_format, header_data)
    
    # return the header tuple - this will be the payload
    return unpacked_header

def receive_packet(conn: socket.socket, header_format: str = '!3I'):
    # receive packet header from the function and break the tuple and message
    (seq_num, ack_num, ack, syn, fin) = receive_header(conn, header_format) # Could also just do: header and *header later to decouple.

    # receive payload from a packet and decode
    client_payload = conn.recv(4)        #4 bytes = 32 bits
    payload_decoded = client_payload.decode()

    return seq_num, ack_num, ack, syn, fin, payload_decoded

def log_packet(action, seq_num, ack_num, ack, syn, fin):
    # need an "IF" statement to differentiate
    if (action == "RECV"): # These are identical logs:
        # Logging the header information on server
        logging.info("action, <Sequence Number: {}> <Acknowledgment Number: {}> [ACK: {}] [SYN: {}] [FIN:{}]".format(seq_num, ack_num, ack, syn, fin))

    else:
        # Logging the header information on client
        logging.info("action, <Sequence Number: {}> <Acknowledgment Number: {}> [ACK: {}] [SYN: {}] [FIN:{}]".format(seq_num, ack_num, ack, syn, fin))
