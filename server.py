
import socket
import sys
import threading
import os
import zlib

##some globals 
BACKLOG = 50                  #arbitrary tcp backlog number
BUFF = 16000                  #google suggested to use this size 
USERPORT = "3000"             #always 8080 on this machine - change in system proxy settings
#blocking globals 
BLOCKED_URLS_FILE = "blocked.txt"      #Name of blocked lists file used to fetch later
urls_blocked = []               #list of blocked urls
#cache globals
cache ={}                       #hash map 
cache_entry =[]                 #cache entry temp list

#function sets up and handles user interactions
def Main(): 2

    #read in blocked URLS from file
    block_temp = open(BLOCKED_URLS_FILE, "r")
    for i in block_temp:
        urls_blocked.append(i)
    block_temp.close()
    try:
        while True:
            #user menu 
            user_option = raw_input("Main Menu: \n 1. Use Proxy \n 2. Block or Unblock  \n 3. Quit \n")
            #user wants connection
            if(user_option == "1"):
                while True:
                    try:
                        run()
                    except socket.error :
                        print("Error- in use")
                        pass
                    except ValueError:
                        print("Invalid input")
                        pass
            
            #user wants to block some urls
            elif(user_option == "2"):
                block_print()
                while True:
                    #secondary blocking menu 
                    user_option2 = raw_input("Blocking Menu: \n 1. Block URL \n 2. Un-block URL \n 3. Go Back \n")
                    if(user_option2 == '1'):
                        user_url = raw_input("What would you like to block?\n")
                        blocker(user_url, True)
                        block_print()
                        break
                    elif(user_option2 == '2'):
                        user_url = raw_input("What would you like to unblock?\n")
                        blocker(user_url, False)
                        block_print()
                        break
                    elif(user_option2 == '3'):
                        print("Heading back to base. \n")
                        break
                    else:
                        print("Inalid input\n")
            #user wants to leave :(
            elif(user_option == "3"):
                print("Adios Amigo")
                sys.exit()
            #user is confused about what they want 
            else:
                print("You okay hun?\n")

    except Exception:
        pass

#fucntion to print blocked urls 
def block_print():
    print("URLS BLOCKED:")
    #print all da blocked URLs 
    for url in urls_blocked:
        print(url.strip()) #take off first and last 

#Function to block and unblock urls
def blocker(user_url, blockBool): #:)
    #blocked
    if(blockBool):
        block(user_url)
        return
    #unblocked
    elif not blockBool:
        unblock(user_url)
        return  

#function to block
def block(user_url):
    #add to blocked list 
        urls_blocked.append(user_url)
        #add to blocked file
        temp_file = open(BLOCKED_URLS_FILE, "a+")
        temp_file.write(user_url +"\n")
        temp_file.close()
        return

#function to unblock
def unblock(user_url): 
    try:
            #remove from list 
            urls_blocked.remove(user_url+"\n")
            #overwrite file with lines except blocked url 
            temp_file = open(BLOCKED_URLS_FILE,"r")
            temp_lines = temp_file.readlines()
            temp_file.close()
            #reopen file in write mode
            temp_file= open(BLOCKED_URLS_FILE,"w")
            for line in temp_lines:
                if line!=user_url+"\n":
                    temp_file.write(line)
            temp_file.close()

                    
    except ValueError:
            return

#function to check block   
def block_check(server):
    for i in urls_blocked:
            if(i.lower().strip() == server.lower().strip()):
                print("That's a blocked URL")
                return True
    return False

#creates and manages server and threads lol
def run(): #
    #let's make connections
    try:
        #create socket object with address family and socket type
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #associate socket with local address 
        server.bind(('', int(USERPORT)))
        server.listen(BACKLOG) 
        print("Proxy Server Started on Port: " + str(USERPORT))
    except Exception:
        pass

    while True:
        try:
            conn, addr = server.accept() #accept connection conn=new socket to send and rcv from, addr is port num of other end of connection
            request = conn.recv(BUFF) #get data from socket with max size of buffer
            #thread calls request_handler function invoked with conn and request as args
            pyThread = threading.Thread(target = request_parser, args=(conn, request))
            pyThread.daemon = True #threads are daemon so we can quit program without explicitly telling them to quit 
            pyThread.start() #lets go thread 
        except KeyboardInterrupt:
            server.close() #stop socket running
            print("Byeeee")
            sys.exit()

    server.close() #That'll do socket, that'll do.



#takes socket of connection and request data from socket and parses it
def request_parser(conn, request):
    try:
         
        #parse url
        line_1 = request.split('\n')[0] #split into list and get first item 
        url = line_1.split(' ')[1] #url is second item in first line list 
        if((url.find("://"))== -1):
            temp_url = url #if no http
        else:
            temp_url = url[((url.find("://"))+3):] #if http
        #parse port
        port_index = temp_url.find(":")
        server_index= temp_url.find("/")
        if( server_index== -1):
            server_index = len(temp_url)
     

        if (port_index==-1 or server_index <port_index):
            port = 80 #default
            server = temp_url[:server_index]
        else:
            port = int((temp_url[(port_index+1):])[:server_index-port_index-1])
            server = temp_url[:port_index]
        #call relayer 
        relayer(server, port, conn, request, line_1)
    except Exception, e:
        pass

#function for request in cache
def cache_case(request, conn):
    try:
            while True:
                if cache[request]:
                    reply = cache[request]
                    for data in reply:
                        conn.send(data)
                        print("Cached Request sent to browser")

            conn.close()
            return
    except KeyError:
            pass
    return   

#function for request not in cache
def uncached_case(request,conn, server,port):
    #create new sockets 
    #open new socket and send data to browser and also cache it 
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((server, port))
    new_socket.send(request)

    while True:
        #sends data to browser and caches response
        response = new_socket.recv(BUFF)
        if(len(response)>0): #if succesful response 
            cache_entry.append(response)
            conn.send(response)
            print("Response sent to browser and added to cache  : " + server)
            cache[request]=cache_entry
        else:
            break

    s.close()
    conn.close()
    return 

#sends data to browser
def relayer(server, port, conn, request, line_1):
    try:
        #url block check 
        if(block_check(server)):
            conn.close()
            return 

        # case for cached data 
        if(cache[request]):
            cache_case(request,conn)
        uncached_case(request,conn,server,port)
        
    except socket.error:
        s.close()
        conn.close()
        print("error")
        sys.exit()

    except KeyboardInterrupt:
        s.close()
        conn.close()
        print("Byee")
        sys.exit()



if __name__ == '__main__':
	Main()

