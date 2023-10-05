# Importing the socket API
import socket

# Creating the socket object
server_socket = socket.socket()

# Creating the host and server port
HOST = "127.0.0.1"
PORT = 8080 # **NOTE: ALWAYS keep this number above 1024**

# Varaible to track bind attempts
bind_attempts = 0

while (bind_attempts < 5):
    try:
        # Binding to the address
        server_socket.bind((HOST, PORT))
        break
    except:
        bind_attempts += 1
        if (bind_attempts < 5):
            print("Failed to bind to port", PORT, "\nRetrying...")
        else:
            print("Timed out...\nPlease try again later.")

# If we did not time out
if (bind_attempts != 5):
    while True:
        try:
            # Listening on for connections on the port
            server_socket.listen(5)
        except:
            print("Two moons.") # Really don't think this is necessary, the words in print came from a friend.

        # Logging the server start up
        print("Server is listening on: " + HOST + ":" + str(PORT))

        try:
            # Accepting any connection requests
            conn, client_address = server_socket.accept()
        except:
            print("Client connection failed.")
            continue

        # Logging the connection
        print("Server connected to ", client_address)

        # Recieving any data from the client
        while True:
            receive_attempts = 0
            while (receive_attempts < 3):
                try:
                    # Receiving data from the connection
                    data = conn.recv(1000)
                    break
                except:
                    receive_attempts += 1
                    if (receive_attempts < 3):
                        print("Data recieve failed.\nRetrying...")
                    else:
                        print("Failed to receive any data from the client.")
            
            if (receive_attempts == 3):
                print("Client is not responding, returning to listen.")
                break

            try:
                # Decoding the data sent
                decoded_data = data.decode()
                print(decoded_data)
            except:
                print("Data decode and print failed.")

            try:
                # Minecraft achievement: RETURN TO SENDER
                conn.send(data)
            except:
                print("Failed to send data back to client.")

            # NOTE that this just means, if an empty message is sent, close.
            if not data:
                break

        # Closing the connection so we can return to listening.
        conn.close()
