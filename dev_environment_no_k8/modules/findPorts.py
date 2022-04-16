from socket import socket, AF_INET, SOCK_STREAM

def findPort1():
    #finds an open port on the host for the new network
    port = 80
    while True:
        a_socket = socket(AF_INET, SOCK_STREAM)
        location = ("127.0.0.1", port)
        result_of_check = a_socket.connect_ex(location)
        if result_of_check == a_socket.connect_ex(location):
            print(f"using {port} on host for this cluster")
            return str(port)
        else: 
            port += 1
            print(f"trying port {port}")
            a_socket.close()
    port1 = findPort1()
    return port1

def findPort2():
    #finds an open port on the host for the new network
    port = 443
    while True:
        a_socket = socket(AF_INET, SOCK_STREAM)
        location = ("127.0.0.1", port)
        result_of_check = a_socket.connect_ex(location)
        if result_of_check == a_socket.connect_ex(location):
            print(f"using {port} on host for this cluster")
            return str(port)
        else: 
            port += 1
            print(f"trying port {port}")
            a_socket.close()
    port2 = findPort2()
    return port2

