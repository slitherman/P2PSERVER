import socket

SIZE = 1024
DISCONNECT_MSG = "!DISCONNECTED"
PORT = 9060
SERVER = socket.gethostbyname(socket.gethostname())

def download_file(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((SERVER, PORT))
        client.sendall(f"GET {filename}".encode())
        data = client.recv(SIZE)
        if data.startswith(b"HTTP/1.1 404 Not Found"):
            print(f"File '{filename}' not found on server")
        else:
            with open(filename, "wb") as f:
                f.write(data)
            print(f"File '{filename}' downloaded successfully")

if __name__ == "__main__":
    filename = input("Enter filename to download: ")
    download_file(filename)
