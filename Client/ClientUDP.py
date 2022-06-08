from socket import *
import os
import time

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
    download_data = open(filename.decode('utf-8'), 'wb')
    packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
    packet_received = 0
    try:
        while(packet):
            packet_received = packet_received + 1
            download_data.write(packet)
            client_socket.settimeout(2)
            packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
    except timeout:
        download_data.close()
        print(">> Checking file integrity...")
        client_socket.settimeout(5)
        ack_num, server_address = client_socket.recvfrom(BUFFER_SIZE)
        if packet_received == int(ack_num.decode('utf-8')):
            print(">> File Downloaded!")
            return
        print(">> [Error]: Packet loss, file corrupted. Deleting file and ending process")
        os.remove(filename)
        return

# Method that send the file requested to the server.
def sendToServer(filename):
    data = open(filename, 'rb')
    packet = data.read(BUFFER_SIZE)
    print(">> Sending data...")
    packet_sent = 0
    while packet:
        client_socket.sendto(packet, server_address)
        packet_sent = packet_sent + 1
        print(">> Sending...")
        packet = data.read(BUFFER_SIZE)
    data.close()
    time.sleep(3)
    client_socket.sendto(str(packet_sent).encode('utf-8'), server_address)
    print(">> Sending complete!")
    return

# Method that check if file exist in directory. If not, print the error and end the process.
def checkFileExist(filename):
    print(">> Querying filenames in directory...")

    if len(os.listdir()) == 0:
        print(">> [Error]: There are no files in the directory!")
        return False

    if os.path.exists(filename):
        print('>> File found! ->', filename)
        return True

    print(">> [Error]: File not found!")
    return False

# Main loop to send the order to the server.
while True:
    client_message = input("\n>> To server => ")
    client_request = client_message.split()

    if client_request[0] == 'list':
        client_socket.sendto(client_message.encode('utf-8'), server_address)
        print(">> Getting list from server")
        list, server_address = client_socket.recvfrom(BUFFER_SIZE)
        print(">> List of files in server: " , list.decode('utf-8'))
        continue
    
    if client_request[0] == 'get':
        client_socket.sendto(client_message.encode('utf-8'), server_address)
        print(">> Querying file...")
        getFromServer()
        continue
    
    if client_request[0] == 'put':
        if checkFileExist(client_request[1]):
            print(">> Sending file to server...")
            client_socket.sendto(client_message.encode('utf-8'), server_address)
            sendToServer(client_request[1])

    if client_request[0] == 'removelocal':
        try:
            os.remove(client_request[1])
            print(">> ", client_request[1], " deleted. [local]")
            continue
        except FileNotFoundError:
            print(">> [Error]: File not found. [local]")
            continue

    if client_request[0] == 'removeserver':
        client_socket.sendto(client_message.encode('utf-8'), server_address)
        status, server_address = client_socket.recvfrom(BUFFER_SIZE)
        if int(status.decode('utf-8')) == 0:
            print(">> ", client_request[1], " deleted. [remote]")
        print(">> [Error] File not found. [remote]")

        continue

    if client_request[0] == 'exit':
        exit()

    if client_request[0] == 'exitserver':
        client_socket.sendto(client_message.encode('utf-8'), server_address)
        continue