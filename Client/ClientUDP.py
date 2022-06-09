#Programmazione di reti 
#Elaborato 2 
#Componenti del gruppo: 
#Pablo Sebastian Vargas Grateron Mat: 0000970487 Email: pablo.vargasgrateron@studio.unibo.it
#Babboni Luca Mat: 0000971126 Email: luca.babboni2@studio.unibo.it

#CLIENT

from pickle import TRUE
from socket import *
import os
import time
import hashlib

BUFFER_SIZE = 1024
FILE_LIST_NAME = "list.txt"

ip = "127.0.0.1"
port = 4444
client_socket = socket(AF_INET, SOCK_DGRAM)
server_address = (ip, port)
print(">> Client online.")

#Function that calculate hash 
def calculateHash(filename): 
    md5_hash = hashlib.md5() 
    with open(filename,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

# Function that gets a file from the server and store it in the client directory.
def getFromServer():
    status, server_address = client_socket.recvfrom(BUFFER_SIZE)
    if int(status.decode('utf-8')) == 1:
        print(">> The server database is empty!")
        return
    if int(status.decode('utf-8')) == 2:
        print(">> File not found in the server")
        return
    
    #Recive package from server
    filename, server_address = client_socket.recvfrom(BUFFER_SIZE)
    download_data = open(filename.decode('utf-8'), 'wb')
    packet, server_address = client_socket.recvfrom(BUFFER_SIZE) 
    try:
        while(packet):
            download_data.write(packet) 
            client_socket.settimeout(2)
            packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
    except timeout:
        download_data.close()

        #Check downloaded file integrity
        print(">> Checking file integrity...")
        try:
            client_socket.settimeout(5)
            hash_server, server_address = client_socket.recvfrom(BUFFER_SIZE)
            hash_client = calculateHash(filename)
            if hash_client == str(hash_server.decode('utf-8')):
                print(">> File Downloaded!")
            else:
                print(">> [Error]: Packet loss, file corrupted. Deleting file and ending process")
                os.remove(filename)
            return
        except TimeoutError:
            print(">> [Error]: Server timeout. Deleting file.")
            os.remove(filename)

# Function that send the file requested to the server.
def sendToServer(filename):
    client_hash = calculateHash(filename)
    data = open(filename, 'rb')
    packet = data.read(BUFFER_SIZE)
    print(">> Sending data...")
    while packet:
        client_socket.sendto(packet, server_address)
        print(">> Sending...")
        packet = data.read(BUFFER_SIZE)
    data.close()
    time.sleep(3)
    #ast packet send contains the client hash_code for integrity check
    client_socket.sendto(str(client_hash).encode('utf-8'), server_address)
    print(">> Sending complete!")

    #Check if the file was send correctly
    try:
        client_socket.settimeout(5)
        error_status, client_address = client_socket.recvfrom(BUFFER_SIZE)
        message = int(error_status.decode())
        if message == 0: 
            print(">> File send correctly")
        else:
            print(">> [Error] Failed file send")
        return
    except TimeoutError:
        print(">> [Error]: Server timeout")

# Function that check if file exist in directory. If not, print the error and end the process.
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
        getFromServer()
        print(">> List of files in server directory: ")
        with open(FILE_LIST_NAME) as f:
            for line in f:
                print(line)
        f.close
        os.remove(FILE_LIST_NAME)
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
