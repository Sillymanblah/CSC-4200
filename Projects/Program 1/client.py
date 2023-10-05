import socket

# Creating the socket object
client_socket = socket.socket()

# Defining the server's address and port
server_port = 9000

# Getting the server address from the user:
server_address = '127.0.0.1'

print("*" + server_address + "*")

# Variable to store the number of connection attempts:
connect_attempts = 0

# If we try 5 times and fail, exit with a fail
while (connect_attempts < 5):
    try:
        # Connecting to the server
        client_socket.connect((server_address, server_port))
        break
    except:
        connect_attempts += 1
        print("ATTEMPT " + str(connect_attempts) + ": Failed to connect to server...")

# If we actually connected to the server, do our data passing
if (connect_attempts != 5):
    while True:
        # Getting user input
        message = input("Enter a message to send to the server (or \"exit\" to quit): ")
        
        # If the user types nothing, make sure they type something
        while (message == ""):
            message = input("Please, either type a message, or type \"exit\" to quit: ")

        # Exiting if the user said "exit":
        if (message == "exit"):
            break

        try:
            # Encrpyting the data
            encrypted_data = message.encode()
        except:
            print("Data encrpytion failed...\nPlease try again:")
            continue # Using a continue so the user can type another message

        # Variable to count the number of attempts to send the message
        send_attempts = 0

        while True:
            try:
                # Sending the message
                client_socket.send(encrypted_data)
                break
            except:
                if (send_attempts == 3):
                    print("The server appears to be unable to recieve data at this time.")
                    break
                else:
                    print("Data send failed...\nRetrying...")

        # If we fail to send the data, exit the loop and close the port
        # There might be better options, but this is what I decided on
        if (send_attempts == 3):
            break
        
        try:
            # Recieving the response
            encoded_response = client_socket.recv(1000)
            
            # Decoding and printing
            response = encoded_response.decode()
            print(response)
        except:
            print("Server response failed...")

    # Closing the client down
    client_socket.close()

else:
    print("Connections failed; make sure the server is online and you have internet access before trying again.")