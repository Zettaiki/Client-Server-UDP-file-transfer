#Programmazione di reti 
#Elaborato 2 
#Componenti del gruppo: 
#Pablo Sebastian Vargas Grateron Mat: 0000970487 Email: pablo.vargasgrateron@studio.unibo.it
#Babboni Luca Mat: 0000971126 Email: luca.babboni2@studio.unibo.it

#SERVER


from socket import *
import os
import time
import hashlib

BUFFER_SIZE = 1024
FILE_LIST_NAME = "list.txt"

ip = "127.0.0.1"
port = 4444
server_socket = socket(AF_INET, SOCK_DGRAM)
server_address = (ip, port)
server_socket.bind(server_address)
print(">> Server online.")

#Function that calculate hash 
def calculateHash(filename): 
    md5_hash = hashlib.md5() 
    with open(filename,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

def createFileList():
    f = open(FILE_LIST_NAME, 'w')
    for line in os.listdir(os.getcwd()):
       f.write(line)
       f.write('\n')
    f.close
    return

#Method that send the choosen file to the client.
def sendToClient(filename, client_address):
    server_hash = calculateHash(filename)
    data = open(filename, 'rb')
    print(">> Sending filename...")
    server_socket.sendto(filename.encode('utf-8'), client_address)
    packet = data.read(BUFFER_SIZE)
    print(">> Sending data...")
    while (packet):
        (server_socket.sendto(packet, client_address))
        print(">> Sending...")
        packet = data.read(BUFFER_SIZE)
    data.close()
    time.sleep(3)
    server_socket.sendto(str(server_hash).encode('utf-8'), client_address)
    print(">> Sending complete!")
    return

#Function that gets a file and store it in the server
def getFromClient(filename):
    download_data = open(filename, 'wb')
    packet, client_address = server_socket.recvfrom(BUFFER_SIZE)
    try:
        while(packet):
            download_data.write(packet)
            server_socket.settimeout(2)
            packet, client_address = server_socket.recvfrom(BUFFER_SIZE)
    except TimeoutError:
        download_data.close()
        print(">> Checking file integrity...")
        server_socket.settimeout(5)
        client_hash, client_address = server_socket.recvfrom(BUFFER_SIZE)
        server_hash = calculateHash(filename)
        if server_hash == str(client_hash.decode('utf-8')):
            print(">> File Downloaded!") 
            message = 0
        else: 
            print(">> [Error]: Packet loss, file corrupted. Deleting file and ending process")
            os.remove(filename)
            message = 1
        server_socket.sendto(str(message).encode('utf-8'), client_address)
        return

#Method that check if file exist in directory. If not, send the error code to client.
def checkFileExist(filename, client_address):
    print(">> Querying filenames in directory...")

    if len(os.listdir(os.getcwd())) == 0:
        print(">> [Error]: Empty directory, error code = 1")
        message = 1
        server_socket.sendto(str(message).encode('utf-8'), client_address)
        return False
    
    if os.path.exists(filename):
        print('>> File found! ->', filename)
        message = 0
        server_socket.sendto(str(message).encode('utf-8'), client_address)
        return True

    print(">> [Error]: File not found, error code = 2")
    message = 2
    server_socket.sendto(str(message).encode('utf-8'), client_address)
    return False

#Main loop to get the order from the client.
while True:
    print("\n>> Waiting for client...")
    server_socket.settimeout(30)
    client_message = ""
    try:
        client_message, client_address = server_socket.recvfrom(BUFFER_SIZE)
    except TimeoutError:
        continue
    print("\n>> Client message: ", client_message.decode('utf-8'))

    client_request = client_message.decode('utf-8').split()
    
    if client_request[0] == 'list':
        print(">> Getting list of files")
        createFileList()
        print(">> Sending list to ", client_address)
        checkFileExist(FILE_LIST_NAME, client_address)
        sendToClient(FILE_LIST_NAME, client_address)
        os.remove(FILE_LIST_NAME)
        print(">> Completed!")
        continue
    
    if client_request[0] == 'get':
        if checkFileExist(client_request[1], client_address):
            sendToClient(client_request[1], client_address)
            continue

    if client_request[0] == 'put':
        getFromClient(client_request[1])
        continue
    
    if client_request[0] == 'removeserver':
        print('>> Deleting ', client_request[1])
        try:
            os.remove(client_request[1])
            message = '0'
            server_socket.sendto(message.encode('utf-8'), client_address)
            print('>> ', client_request[1], " deleted.")
            continue
        except FileNotFoundError:
            message = '1'
            server_socket.sendto(message.encode('utf-8'), client_address)
            print(">> [Error] File not found.")
            continue
    
    if client_request[0] == 'exitserver':
        exit()
