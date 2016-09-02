import socket

target_host = raw_input("Enter target address: ")
target_port = raw_input("Enter address port: ")

#create client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to target
client.connect((target_host, int(target_port)))

#send data
client.send(raw_input("Enter message: "))

#receive data
response = client.recv(4096)

print response

