# Proxy-Server
A project for CSU34031 Advanced Telecommunications.

 ## A Web Proxy Server 
 ### The Brief 
The objective of the exercise is to implement a Web Proxy Server. A Web proxy is a local server, which fetches items from the Web on behalf of a Web client instead of the client fetching them directly. This allows for caching of pages and access control. 
 The program should be able to: 
 1. Respond to HTTP & HTTPS requests, and should display each request on a management console. It should forward the request to the Web server and relay the response to the browser. 
 2. Handle Websocket connections. 
 3. Dynamically block selected URLs via the management console.
 4. Efficiently cache requests locally and thus save bandwidth. You must gather timing and bandwidth data to prove the efficiency of your proxy.
 5. Handle multiple requests simultaneously by implementing a threaded server. 

 The program can be written in a programming language of your choice. However, you must ensure that you do not overuse any API or Library functionality that implements the majority of the work for you. 
 
 ### My Implementation 


#### Globals
I initialised some global constants at the start of the program. Backlog is the maximum number of queued connections and I used the value 5 as this is the usual system maximum value. 
BUFF is the maximum buffer size of data we can actually receive from a socket. The value 16000 used here is somewhat arbitrary, and came about from some googling and testing different figures. 
USERPORT is the localhost user port used by the proxy server.
The BLOCKED_URLS_FILE points to the persisting text file containing the blocked URLS. The urls_blocked list acts as a storage mechanism for blocked urls during runtime of the server,
cache is the hash map for key value pairs. cache_entry is a temporary way of storing a request to enter into the cache.

#### Server
The main has a bit of setup where the program takes the stored blocked URLs from their text file into the urls list. I chose to put blocked URLs into a text file as it was a simple way to ensure they weren't volatile. The urls_blocked list is used during run time of the program to keep track of blocked URLs. 
A simple user menu allows the user to choose between running the server, blocking or unblocking URLs or exiting the program.
If the user selects to run the server the run function sets up a tcp connection and waits for the user to type something in a browser.
The server accepts a connection and gets request data from this connection. It then starts threads running the request_parser function on the request data. 
The request parser extracts the port and server number from the URL, and passes it along to the relayer function along with the connection and the request.
The relayer function checks that the URL isn’t blocked and if it isn’t checks first to see if the request is cached. If it is cached the data is sent straight to the browser connection. 
If the request is not cached, a new socket is set up. The socket receives data after sending its request. This data is cached and sent to the browser. 

#### Blocking
If the user chooses to block or unblock from the main menu, a second menu is displayed where a user chooses to block a URL, unblock a URL or return to the main menu. 
If they choose to block, they are prompted for the URL and this is added to the blocked URLs list and added to the URLs file.
If they choose to unblock, they are also prompted for the URL. The URL is removed from the URLs list and the URLs file is overwritten. 









