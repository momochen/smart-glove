# To test it with netcat, start the script and execute:
# 
#    echo "Hello, cat." | ncat.exe 127.0.0.1 12345
#
import socket
import OSC
from OSC import OSCServer,OSCClient,OSCMessage
import sys
import types
import threading
import time

HOST = '127.0.0.1'   # use '' to expose to all networks
RX_PORT = 42003
TX_PORT = 42002

def incoming(host, port):
  """Open specified port and return file-like object"""
  #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  # set SOL_SOCKET.SO_REUSEADDR=1 to reuse the socket if
  # needed later without waiting for timeout (after it is
  # closed, for example)
  #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((host, port))
  while True:
        data,addr = sock.recvfrom(1024)
        print "received message:", data

def handler_func(path,tags,data,source):
    print "path",path
    print "args",args
    print "data",data
    print "source",source

    
def main():
    #incoming(HOST,PORT)
    server = OSCServer(('127.0.0.1',42003))
    client = OSC.OSCClient()
    client.connect(('127.0.0.1',42002))

    server.addDefaultHandlers()
    server.addMsgHandler("/exo/hand/gesture",handler_func)

    st = threading.Thread( target = server.serve_forever )
    st.start()

    try :
        while 1 :
                time.sleep(10)
    except KeyboardInterrupt :
        print "\nClosing OSCServer."
        s.close()
        print "Waiting for Server-thread to finish"
        st.join()
        print "Done"

    server.close()

if __name__=="__main__":
    main()
