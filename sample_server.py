# Briefly explaining the socket library
import socket

# Defining constants for server and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# Declaring new web socket (abstraction for n/w connections)
# AF_INET indicates use of IPv4
# SOCK_STREAM indicates use of TCP for the connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setting an option of the socket at the socket level (as indicated by SOL_SOCKET)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the instance to a TCP address and start listening on that address
server.bind((SERVER_HOST, SERVER_PORT))
server.listen(1)
print('Listening on port %s...' % SERVER_PORT)

while True:
    # Accepting a client's connection and printing the request
    client_connection, client_address = server.accept()
    request = client_connection.recv(1024).decode()
    print(request)

    # To serve a web page, the server must parse the client's request
    headers = request.split('\n')
    print(headers)
    filename = headers[0].split()[1]

    # By default, we offer up the index.html - ** like a frenchman ** DINNER IS SERVED
    if(filename == '/'):
        filename = '/index.html'

    # Responding to the client's request for the file
    # with the added bonus of returning a 404 if the file is not found
    try:
        fin = open('html' + filename)
        content = fin.read()
        fin.close()

        response = 'HTTP/1.0 200 OK\n\n' + content
    except FileNotFoundError:
        response = "HTTP/1.0 404 NOT FOUND\n\nFile not found..."

    # Responding to the client
    client_connection.sendall(response.encode())
    client_connection.close()

server.close()
