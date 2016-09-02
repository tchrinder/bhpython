#!/usr/bin/python
import sys
import socket
import getopt
import threading
import subprocess

#global vars
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
	print "bhpython network tool"
	print
	print "Usage: primitivenet.py -t target_host -p port"
	print "-l --listen - listen on [host]:[port] for incoming connections"
	print "-e --execute=file_to_run - execute the given file upon receiving a connection"
	print "-c --command - initialize a command shell"
	print "-u --upload=destination - upon receiving connection upload a file and write to [destination]"
	print
	sys.exit(0)

def client_sender(buffer):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)
        
        while True:
            
            recv_len = 1
            response = ""
            
            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data
                
                if recv_len < 4096:
                    break

            print response
        
            #wait for more input
            buffer = raw_input("")
            buffer += "\n"

            #send input
            client.send(buffer)

    except:
        print sys.exc_info()
        print "[*] Exception! Exiting."

        client.close()

def server_loop():
    global target

    #listen on all interfaces if target not specified
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #new thread for client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):

    #remove newline
    command = command.rstrip()

    #run command and grab output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    #check if uploading
    if len(upload_destination):

        #read bytes
        file_buffer = ""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        #write bytes
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #inform user
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)

        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    #check for command execution
    if len(execute):

        #run command
        output = run_command(execute)
        client_socket.send(output)

    #check for command shell request
    if command:

        while True:
            #show prompt
            client_socket.send("<user@unknown:#> ")

            #receive input until linefeed key
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            #return command output to client
            response = run_command(cmd_buffer)
            client_socket.send(response)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    #process commandline args
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
        ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    #if sending data
    if not listen and len(target) and port > 0:
        
        #read buffered input from stdin, CTRL-D to send
        buffer = sys.stdin.read()
        client_sender(buffer)
    
    if listen:
        server_loop()

main()
