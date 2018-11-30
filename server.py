#!/usr/bin/python3.6
#Deepa and Shweta - IRC server code

import socket
import sys
import threading
import ast

#Thread for each client
def clienthandling(client, uname, grpnames):    
    #try:
    clientconnected = True
    keys = clients.keys()  
    print("clients connected...") 
    print(keys)
   
    while clientconnected: 
        msg = client.recv(1024).decode().strip()
        print(uname + " >>%s" % (msg))

        #List of online clients
        if '**online_clients' in msg:  #use of ** is for consistancy to make all commands equal. 
            clientNo = 0
            response = ''
            for name in clients.keys():
                clientNo += 1
                response += str(clientNo) + "::" + name + '\n' 
            client.send((str("\nNumber of people online:\n" + response)).encode())       
        
        #Create Room
        elif '**create_room' in msg:
            msg = msg.replace('**create_room ', '').strip()
            print(msg)
            if msg in grpnames.keys():
                client.send('group name already exists'.encode())
            else:
                grpnames[msg] = set()
                grpnames[msg].add(uname) 
                print(grpnames)
                client.send("Group Created".encode())


        #List room with their clients
        elif '**list_rooms' in msg:
                print("\ndisplayed list of clients to client")
                c = ''
                b = ''
                #if(key in grpnames.keys()):
                for key in grpnames:
                    for name in grpnames[key]:
                        c += str(name) + ' '
                    b += str(key) + ': ' + c + '\n'
                    c = ''
                print(b)
                if (b != ''):
                    client.sendall(b.encode())
                else:
                    client.send('No Rooms Exist'.encode())

        #Broadcast message to all online clients
        elif '**broadcast' in msg:
            msg = uname + '>>' + msg
            msg = msg.replace('**broadcast','')
            msg = msg.split(">>")
            for k in clients.keys():
                if msg[0] == k:
                    print("skipping broadcast to sender %s" % (k))
                    continue
                clients[k].send(str(msg[0] + " >> " +msg[1]).encode())
                print("sent broadcast message to %s" % (k))

        #Join Room
        elif '**join_room' in msg:
            msg = msg.replace('**join_room ', '').strip()
            if msg in grpnames.keys():
                if uname in grpnames[msg]:
                    client.send('You are already in the group'.encode())
                else:
                    grpnames[msg].add(uname)
                    client.send(str('You have been added in the group' + msg).encode())
            else:
                client.send('This group does not exists'.encode())

        #Leave Room
        elif '**leave_room' in msg:
            msg = msg.replace('**leave_room ', '').strip()
            print(msg)
            print(uname)
            if msg in grpnames.keys():
                if uname in grpnames[msg]:
                    grpnames[msg].remove(uname)  
                    client.send(str('You have been removed from the group' + msg).encode())        
                else:
                    client.send("Sorry you are not in that group..Please enter valid group name.".encode())
            else:
                client.send('This group does not exists'.encode())
            for name in grpnames[msg]:
                    clients.get(name).send(str(uname + ' has left the group' + msg).encode())

        #Quit IRC
        elif '**quit' in msg:
            response = "stopping session..."
            clients.pop(uname)
            for k in grpnames:
                if uname in grpnames[k]:
                    grpnames[k].remove(uname)
            print(uname + " has been logged out")
            clientconnected = False 
            print("Updated groups: ")
            print(grpnames)
            print("Updated client list: ")
            print(clients.keys())

        #Privat and Group chat
        else:
            found = False

            #Private chat
            for name in clients.keys():
                if ('**' + name) in msg:
                    msg = msg.replace('**'+name, ' ')
                    clients.get(name).send(str(uname + '>>' + msg).encode())
                    found = True
                    break

            #Group chat
            if not found and msg and msg.strip() != '':
                msg = msg.strip().split("**")
                gname = msg[-1]
                msg = ''.join(msg[:-1])
                if gname in grpnames.keys():
                    if uname in grpnames[gname]:
                        for uname in grpnames[gname]:
                            clients.get(uname).send(str(uname + '>>' + msg).encode())
                            found = True
                    else:
                        client.send("You don't belong to this group".encode())

            #invalid command
            if not found:
                client.send("Sorry invalid command or message..".encode())

    # except: #--> exception occurred in client! Disconnect it from self and all groups
    #     clients.pop(uname)
    #     for k in grpnames:
    #         if uname in grpnames[k]:
    #             grpnames[k].remove(uname)
    #     print(uname + " has been logged out")
    #     print(clients.keys())
    #     clientconnected = False #close the created tread for client


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #server socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #Reusable socket
    ServerRunning = True
    clients = {}
    grpnames = {}  
    s.bind(('localhost', 50021))    #Bind ip with port number
    print("Server is listening")
    s.listen(10)
    
    #Main Thread that accepts incoming clients
    while ServerRunning:
        client, addr = s.accept()
        while (True):
            uname = client.recv(1024).decode().lower()
            if(uname in clients):
                client.send("username exists".encode())
            else:
                print(""+ uname+ " is connected to server")
                client.send("welcome".encode())
                clients[uname] = client
                threading.Thread(target = clienthandling, args = (client,uname,grpnames )).start() #create thread to add new client
                break


except (KeyboardInterrupt) as e:
    print("Server shut down! gracefully exiting")
    for uname,client in clients.items():
        client.send("Terminate".encode()) #--> request each client to quit, the client replies with **quit, control flows to quit module, client thread closes
    print('inside except, clients closed, now closing server')
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    print("server closed")
    sys.exit(1)



