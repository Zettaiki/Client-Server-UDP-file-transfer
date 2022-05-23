from socket import *
import os

BUFFER_SIZE = 1024

ip = "127.0.0.1"
port = 4444

server_socket = socket(AF_INET, SOCK_DGRAM)
server_address = (ip, port)
server_socket.bind(server_address)

print(">> Server online.")

# Method that send the file requested to the client.
def sendToClient(filename, client_address):
    print(">> Querying server filenames")
    dirFiles = os.listdir('./Server')

    if len(dirFiles) <= 1:
        message = '1'
        server_socket.sendto(message.encode('utf-8'), client_address)
        return
    
    for dirFileName in dirFiles:
        if filename == dirFileName:
            print(">> File found! ->", filename)
            message = '0'
            server_socket.sendto(message.encode('utf-8'), client_address)
            data = open("./Server/" + filename, 'rb')
            print(">> Sending filename...")
            server_socket.sendto(filename.encode('utf-8'), client_address)
            packet = data.read(BUFFER_SIZE)
            print(">> Sending data...")
            while (packet):
                if(server_socket.sendto(packet, client_address)):
                    print(">> Sending...")
                    packet = data.read(BUFFER_SIZE)
            data.close()
            print(">> Sending successful!")
            return
    message = '2'
    server_socket.sendto(message.encode('utf-8'), client_address)
    return

# Method that gets a file and store it in the server
def getFromClient(filename):
    status, client_address = server_socket.recvfrom(BUFFER_SIZE)
    if int(status.decode('utf-8')) == 1:
        print(">> Aborting request: the user directory is empty.")
        return
    if int(status.decode('utf-8')) == 2:
        print(">> Aborting request: the user don't have files to upload.")
        return
    
    filename, client_address = server_socket.recvfrom(BUFFER_SIZE)
    download_data = open("./Server/" + filename.decode('utf-8'), 'wb')
    packet, client_address = server_socket.recvfrom(BUFFER_SIZE)
    try:
        while(packet):
            download_data.write(packet)
            server_socket.settimeout(2)
            packet, server_address = server_socket.recvfrom(BUFFER_SIZE)
    except timeout:
        download_data.close()
        print(">> File Downloaded!")

        # TODO: set timeout to default

        return

# Main loop to get the order from the client.
while True:
    print("\n>> Waiting for client...")
    client_message, client_address = server_socket.recvfrom(BUFFER_SIZE)
    print("\n>> Client message: ", client_message.decode('utf-8'))

    client_request = client_message.decode('utf-8').split()
    
    if client_request[0] == 'list':
        print(">> Getting list of files")
        file_list = os.listdir('./Server')
        print(">> Sending list to ", client_address)
        server_socket.sendto(str(file_list).encode('utf-8'), client_address)
        print(">> Completed!")
        continue
    
    if client_request[0] == 'get':
        sendToClient(client_request[1], client_address)
        continue

    if client_request[0] == 'put':
        getFromClient(client_request[1])
        continue
