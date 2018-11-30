#!/usr/bin/python3.6
#Deepa and Shweta - IRC client code 

import sys
import threading
import socket 

#connect to server
def connect(s):
    s.connect(('localhost', 50021))
    while (True):
        uname = input("enter uname: ")  
        s.send(uname.encode())
        msg=s.recv(1024).decode()
        if(msg != "welcome"):
            print("User already exists, please enter new name\n")
        else:
            print('\nWELCOME IRC APP '+ uname)
            print('''HELP
                1:**online_clients [SYNTAX: **online_clients]
                2:**create_room [SYNTAX: **create_room <name_of_room>]
                3:**list_rooms [SYNTAX: **list_rooms]
                4:**join_room [SYNTAX: **join_room <name_of_room>]
                5:**leave_room [SYNTAX: **leave_room]
                6:**broadcast [SYNTAX: **broadcast]
                7:**help [SYNTAX: **help]
                8:**quit [SYNTAX: **quit]
                To send personal message [SYNTAX: <message> **name_of_client]
                To send room message [SYNTAX: <message> **room_name]\n\n
                ''')
            threading.Thread(target = clientmsgrecv, args = (s,)).start()
            break
    return uname

#parallel thread to receive messages
def clientmsgrecv(s):       
    global clientRunning
    while clientRunning:        
        msg=s.recv(1024).decode()
        print(msg)
        if(msg == "Terminate"):
            print('The Server just broke down, please enter **quit')
            clientRunning = False

#function in Thread-0 to send messages   
def clientmsgsend(uname, s):
    global clientRunning
    while clientRunning:
        help1 ='''MAIN MENU
                1:**online_clients [SYNTAX: **online_clients]
                2:**create_room [SYNTAX: **create_room <name_of_room>]
                3:**list_rooms [SYNTAX: **list_rooms]
                4:**join_room [SYNTAX: **join_room <name_of_room>]
                5:**leave_room [SYNTAX: **leave_room]
                6:**broadcast [SYNTAX: **broadcast]
                8:**quit [SYNTAX: **quit]
                9:To view this Menu again [SYNTAX: **help]
                    To send personal message [SYNTAX: <message> **name_of_client]
                    To send room message [SYNTAX: <message> **room_name]\n\n
                '''
        tempmsg = input()
        msg1 = uname + "<<" + tempmsg
        if  tempmsg == '**quit':
            clientRunning = False
            print ("client logged out. ")
            s.send(tempmsg.encode())

        elif tempmsg == '**help':
            print(help1)
   
        else:
            s.send(tempmsg.encode())

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #client socket
    clientRunning = True
    uname = connect(s)  #connection established, unique name attached to connection
                        #also spawns thread to run fn with while loop to receive messages
    clientmsgsend(uname, s) #fn with while loop to send messages

except KeyboardInterrupt as k:
    print('\nYou have just expressed a wish to leave, sad to see you go! Bye :)')

except BrokenPipeError as b:
    print('Oops! The connection just broke! Sorry!')

except (ConnectionResetError, ConnectionRefusedError, ConnectionError) as c:
    print('Connection terminated')

except:
    print('Got exception')

finally:
    s.send('**quit'.encode())
    clientRunning = False
    s.shutdown(socket.SHUT_RDWR) #shutdown the RDWR of the socket.
    s.close()    #close socket
    sys.exit(1)


