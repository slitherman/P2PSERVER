import os
import os.path
import socket
import threading
import requests
import pdb; pdb.set_trace()
from os import listdir
from os.path import isfile, join


SIZE = 1024
DISCONNECT_MSG = "!DISCONNECTED"
PORT = 9060
DIRECTORY = "C:\\testfiles"
IP = socket.gethostbyname(socket.gethostname())
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDRESS = (IP, PORT)
URL = "https://peertopeerrestfiletransfer.azurewebsites.net/api/FileEndPoints/all"

def list_files():
    myfiles = [f for f in listdir(DIRECTORY) if isfile(join(DIRECTORY, f))]
    return myfiles

def register_files(file_list, server_URL):
    response = requests.post(server_URL, json={'file_list': file_list})
    if response.status_code == 200:
        print(f"[Files registered successfully] FILE: {file_list} URL: {server_URL}")
    else:
        print("Error registering files.")

def deregister_files(file_list, server_URL):
    response = requests.delete(server_URL + f'?file_list={file_list}&server_URL={SERVER}')
    if response.status_code == 200:
        print(f"[Files successfully deregistered] FILE: {file_list} URL: {server_URL}")
    else:
        print("Error deregistering files.")

def handle_client(conn, addr, directory):
    print(f"[NEW CONNECTION] {addr} connected")
    while True:
        data = conn.recv(SIZE).decode()
        if not data:
            break
        if data.startswith("GET "):
            filename = data[4:].strip()
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    filedata = f.read()
                    # socket.sendall is a high-level Python-only method that sends the entire buffer you pass or throws an exception.
                    # It does that by calling socket.send until everything has been sent or an error occurs.
                    #If you're using TCP with blocking sockets and don't want to be bothered by internals (this is the case for most simple network applications), use sendall.
                    #Unlike send(), this method continues to send data from string until either all data has been sent or an error occurs.
                    #None is returned on success. On error, an exception is raised, and there is no way to determine how much data, if any, was successfully sent

                conn.sendall(filedata)
                # indexing tuple where the port and ip is
                print(f"Sent file '{filename}' to {addr[0]}:{addr[1]}")
            else:
                # \r\n\r\n is used to separate the HTTP header from the HTTP body.
                # o (\r\n\r\n) indicates the end of the header and the beginning of the body
                conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                print(f"File '{filename}' not found for {addr[0]}:{addr[1]}")
        else:
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            print(f"Invalid request from {addr[0]}:{addr[1]}")
    conn.close()

def main():
    print(" [STARTING] The server is starting... ")
    SERVER.bind(ADDRESS)
    SERVER.listen()
    print(f" [LISTENING] the server is listening on {IP}:{PORT}")

    # register files on server startup
    files = list_files()
    register_files(files, f"http://{IP}:{PORT}")

    # deregister files on server shutdown
    deregister_files(files, f"http://{IP}:{PORT}")

    while True:
        conn, addr = SERVER.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, DIRECTORY))
        thread.start()
        print(f"[ACTIVE CONNECTIONS]  {threading.active_count()} -1")




