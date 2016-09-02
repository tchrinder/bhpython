import socket

target_host = "www.google.com"
target_port = 80

#create client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to target
client.connect((target_host, target_port))

#send data
client.send("GET / HTTP/1.1\r\nHOST: google.com\r\n\r\n")

#receive data
response = client.recv(4096)

print response

