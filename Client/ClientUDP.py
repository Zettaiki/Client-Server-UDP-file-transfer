from socket import *
import os

BUFFER_SIZE = 1024

ip = "127.0.0.1"
port = 4444

client_socket = socket(AF_INET, SOCK_DGRAM)
server_address = (ip, port)

print(">> Client online.")

# Method that gets a file from the server and store it in the client directory.
def getFromServer():
    status, server_address = client_socket.recvfrom(BUFFER_SIZE)
    if int(status.decode('utf-8')) == 1:
        print(">> The server database is empty!")
        return
    if int(status.decode('utf-8')) == 2:
        print(">> File not found in the server")
        return
    
    filename, server_address = client_socket.recvfrom(BUFFER_SIZE)
    download_data = open("./Client/" + filename.decode('utf-8'), 'wb')
    packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
    try:
        while(packet):
            download_data.write(packet)
            client_socket.settimeout(2)
            packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
    except timeout:
        download_data.close()
        print(">> File Downloaded!")
        return

# Method that send the file requested to the server.
def sendToServer(filename):
    print(">> Querying client filenames")
    dirFiles = os.listdir('./Client')

    if len(dirFiles) <= 1:
        message = '1'
        client_socket.sendto(message.encode('utf-8'), server_address)
        return

    for dirFileName in dirFiles:
        if filename == dirFileName:
            print(">> File found! ->", filename)
            message = '0'
            client_socket.sendto(message.encode('utf-8'), server_address)
            data = open("./Client/" + filename, 'rb')
            print(">> Sending filename...")
            client_socket.sendto(filename.encode('utf-8'), server_address)
            packet = data.read(BUFFER_SIZE)
            print(">> Sending data...")
            while (packet):
                if(client_socket.sendto(packet, server_address)):
                    print(">> Sending...")
                    packet = data.read(BUFFER_SIZE)
            data.close()
            print(">> Sending successful!")
            return
    message = '2'
    client_socket.sendto(message.encode('utf-8'), server_address)
    return

# Main loop to send the order to the server.
while True:
    client_message = input("\n>> To server => ")
    client_socket.sendto(client_message.encode('utf-8'), server_address)

    client_request = client_message.split()

    if client_request[0] == 'list':
        print(">> Getting list from server")
        list, server_address = client_socket.recvfrom(BUFFER_SIZE)
        print(">> List of files in server: " , list.decode('utf-8'))
        continue
    
    if client_request[0] == 'get':
        print(">> Querying file...")
        getFromServer()
        continue
    
    if client_request[0] == 'put':
        print(">> Sending file to server...")
        sendToServer(client_request[1])
