import struct

# Function returns a tuple of the header and either the string, or a string that is a comma separated list of ints/floats.
def handle_packet(packet: bytes, header_format: struct = struct.Struct('!3BH')):
    
    packet_size = len(packet) # Grabbing the packet size for a check later

    # Declaring the tuple we will return that holds the header data, and
    # unpacking the header specifically, so that we can then unpack the payload.
    header_data: tuple[int, int, int, int] = header_format.unpack_from(packet)
    # NOTE: Order is version, header length, type, and payload length.


    try: # Collecting the information from the tuple for ease of readability:
        header_size = header_data[1]
        service_type = header_data[2]
        payload_size = header_data[3]
    
    except:
        header_error = 'Expected a data set of type tuple[int, int, int, int], but got:\ntuple['
        for header_value in header_data: # For each of the values the header contained:
            header_error += str(type(header_value)) + ', ' # Add it to the string.
        
        header_error = header_error.strip(', ') # Remove the extra comma
        header_error += ']' # Close the end of the tuple

        raise ValueError(header_error) # Throw the error


    # Calculation of expected size of the packet based on the payload and header sizes in header.
    expected_size = header_size + payload_size

    if (expected_size != packet_size): # If our packet size is not what the data says it should be:
        raise ValueError('Packet size is not what was expected.\nExpected {}, got {}'.format(expected_size, packet_size))
        # Throw an error for the unexpected value.

    
    if (service_type == 1): # If we have an integer
        # We are using payload_size / 4 because each int takes 4 bytes.
        num_ints = int(payload_size / 4)
        # Starting an unpack of the number of integers after the header.
        payload_data = struct.unpack_from('!%si' % num_ints, packet, header_size)

    elif (service_type == 2): # If we have a float:
        # Same here, using payload_size / 4 because each float takes 4 bytes.
        num_floats = int(payload_size / 4)
        # Starting an unpack of the number of floats after the header.
        payload_data = struct.unpack_from('!%sf' % num_floats, packet, header_size)


    elif (service_type == 3): # If we have a string:
        # Performing a read off after the header of the string payload.
        payload_data = struct.unpack_from('!%ss' % payload_size, packet, header_size)
    
    else: # If none of the above, there was a mistake:
        raise ValueError('Data type unknown, it appears the packet was corrupted.')
        # Again, we are throwing an error due to a error in a data value.
    
    # Storing all the data from the header and payload in a tuple to return.
    packet_data = (header_data, payload_data)

    return packet_data

def payload_to_string(payload_data: tuple[bytes], service_type: int):
    
    payload: str = '' # Prepping the payload to be filled

    if (service_type == 1): # If we have an integer

        for number in payload_data: # For each integer in the tuple:
            payload += str(int(number)) + ', ' # Add the number and a comma separation.
            
        payload = payload.strip(', ') # Remove the trailing comma and space.

    elif (service_type == 2): # If we have a float:
        for rational in payload_data: # For each float in the tuple:
            payload += str(rational) + ', ' # Add the float and a comma separation.
        
        payload = payload.strip(', ') # Remove the trailing comma and space.

    elif (service_type == 3): # If we have a string:
        for string in payload_data: # For each byte string in the payload (should only be one):
            payload += string.decode() # Decoding the bytes into a string.
    
    else:
        raise ValueError('Conversion failed due to invalid service type, expected 1-3 but got ', service_type)

    return payload

# Required helper of encode_payload()
# This would be more effective if I had to functions, but I save coding time this way.
def cleanup(string: str, data_type: type):
    if (data_type != float and data_type != int):
        print('Wrong type')
        raise ValueError('Expected data_type to hold a value of int or float but got %s' % data_type)

    for character in string: # For each character in the string:
        if (not character.isdigit() and character != '.'): # If have a digit or decimal:
            string = string.replace(character, '') # Remove the non-number, non-decimal character.

    broken_number: list[str] = string.split('.')
    # NOTE: This line handles the removal of the decimals for the int type and can be used to reduce floats to one decimal.

    # Declaring the empty string that will end up holding the final data:
    cleaned = ''

    if (data_type == float): # If our final value should be a float:
        decimal_needed = True # Make note that we need a decimal.
    else: # If we have an int, no decimal is needed:
        decimal_needed = False

    for fragment in broken_number: # for each fragment of the number.
        cleaned += fragment # Add it to the final string.
        
        if (decimal_needed): # If we noted we needed a decimal:
            cleaned += '.' # Add the decimal in.
            # NOTE: That because this happens after the first add, even if our float only had one part
            # That decimal does not fundimentally change the value of the float.

            decimal_needed = False # Now that we added a decimal, we do not need another.

    return cleaned # Returned the cleaned-up data's string

# Function to handle the encoding of only the payload. Fails if the service type is not 1-3
def encode_payload(payload: str, service_type: int):

    # Checking service type to determine how to encode data.
    # For the number types we are assuming it is a comma separated list.
    if (service_type == 1): # Specifying if we have int handle:
        data_list = payload.split(',') # Breaking up the payload into a list of strings containing the numbers.

        int_list: list[int] = [] # Declaration and specification of empty list of int type.

        for integer in data_list: # For each integer in the data list:

            try: # Try casting from string to integer and storing in the list of integers.
                int_list.append(int(integer))
            except ValueError:

                try: # Clean up and retry the conversion:
                    cleaned_int = cleanup(integer, int)
                    int_list.append(int(cleaned_int))
                except ValueError as exc: # If that fails, let the user know something is wrong with the data:
                    raise ValueError('It appears that the following int could not be cleaned up:\n%s' % integer) from exc
                    # Reraising the error with an another argument to specify our issue.

        # Handling the encoding of the payload, if we managed to get the data out.
        encoded_payload = struct.pack('!%si' % len(int_list), *int_list)
        # NOTE: This works by using the %s character to replace it with the number of integers to convert
        # and then sending in the whole list via dereferencing it.

    elif (service_type == 2):
        data_list = payload.split(',') # Breaking up the payload into a list of strings containing the numbers.
        float_list: list[float] = [] # Declaration and specification of an empty float list.
        for rational in data_list: # For each rational (aka float) in the data list:
            try: # Try converting from string to float and storing in the list of floats.
                float_list.append(float(rational))
            except ValueError:
                
                try: # Try a cleanup and retry the append:
                    cleaned_rat = cleanup(rational, float)
                    float_list.append(float(cleaned_rat))
                except ValueError as exc: # If that fails we have some errors.
                    raise ValueError('It appears that the following float could not be cleaned up:\n%s' % rational) from exc
                    # Reraising the error with an additional argument so that we know our specific issue.
    
        # Handling the encoding of the payload.
        encoded_payload = struct.pack('!%sf' % len(float_list), *float_list)
        # NOTE: This works as it calls the number floating point values using the '!%sf' % len(float_list)
        # and gives the whole float list as a list of values by dereferencing it.

    elif (service_type == 3): # The handle for the strings:
        # We have to use payload.encode() because struct pack requires a byte string.
        encoded_payload = struct.pack('!%ss' % len(payload), payload.encode())
        # NOTE: We can also just do: encoded_payload = payload.encode() and get the same result

    else: # Handling the wrong values of service_type
        invalid_service_type = 'Invalid argument for --service_type (consider an integer 1-3).'
        invalid_service_type += '\nYour value was: {}'.format(service_type)
        raise ValueError(invalid_service_type)
    
    return encoded_payload