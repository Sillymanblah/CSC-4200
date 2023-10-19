def create_packet(version, message_type, message_length, message):
    # Encode message
    message_encoded = encode(message)
        
    # Use the python struct module to create a fixed length header
    header = build_header(version, message_type, message_length)
    
    #Combine header and message
    packet = header + message_encoded
        
    return packet
