# Anjie Wang
# node.py

import zmq
import time
import sys
import threading
import config
from treelib import Node,Tree

# lieutenant don't start sending msg until they receive general's cmd (flag=True)
flag=False
# tree for storing received msg
tree=Tree()
cur_sum=0
cur_round=0
list=[]
# identity of actor
identity=""
lock = threading.Lock()

# change the msg of "attack/retreat" if the lieutenant if faulty
def process_msg(msg):
    global identity
    if identity=="lf":
        # faulty lieutenant
        return "retreat "+msg.split(" ",1)[1]
    else:
        return msg

# display current tree structure to console
def show_tree():
    tree.show()

# update information at the end of each round of BFT
def handle_round_end():
    global cur_sum,cur_round,list
    if config.roundInfo[cur_round]==cur_sum:
        print (">> round %d finished" % cur_round)
        show_tree()

        cur_round=cur_round+1
        cur_sum=0
        list=tree.leaves("5000")

# loop for receiving msg at current port
def server_loop(myPort):
    global flag,tree,cur_sum,cur_round
    context = zmq.Context()
    socket= context.socket(zmq.REP)
    socket.bind("tcp://127.0.0.1:"+myPort)
    print("[server %s] start" % myPort)
    while cur_round<=config.lastRoundNo:
        msg= socket.recv()
        with lock:
            msg1="copy"
            socket.send(msg1)
            
            syb,path=msg.split(" ")
            if flag==False:
                # round 0
                flag=True
                tree.create_node(msg,path)  #root node
            else:
                # round >=1
                parent_path=path.rsplit("-",1)[0]
                tree.create_node(msg,path,parent=parent_path)

            # judge round and sum
            cur_sum=cur_sum+1
            handle_round_end()
    
    socket.close()

# loop for sending msg from current port
def client_loop(myPort):
    global flag,list,cur_round
    context = zmq.Context()
    ports=config.ports
    sockets=[]
    for port in ports:
        socket=context.socket(zmq.REQ)
        socket.connect("tcp://localhost:"+port)
        sockets.append(socket)

    while not flag:
        time.sleep(1)
 
    # round 1
    msg=tree["5000"].tag+"-"+myPort
    msg=process_msg(msg)
    print("[client] send: %s"% msg)
    for socket in sockets:
        socket.send(msg)
        msg1=socket.recv()
    
    while cur_round==1:
        time.sleep(1)        
    
    # round 2          
    for node in list:
        msg=node.tag
        last_port=msg.rsplit("-",1)[1]

        # prevent cycle
        if last_port==myPort:
            continue

        # send msg
        msg=msg+"-"+myPort
        msg=process_msg(msg)
        print("[client] send: %s"% msg)
        for socket in sockets:
            socket.send(msg)
            msg1=socket.recv()

    while cur_round==2:
        time.sleep(1)
    
    # close all sockets
    for socket in sockets:
        socket.close()

# get the cmd("attack"/"retreat") from a msg
def getCmd(msg):
    return msg.split(" ")[0]

# majority voting based on resulting msg tree
def vote(root):
    global tree
    
    # base case
    if root.is_leaf():
        return getCmd(root.tag)

    # general case
    list=tree.children(root.identifier)
    num_attack=0
    num_retreat=0
    for node in list:
        if vote(node)=="attack":
            num_attack=num_attack+1
        elif vote(node)=="retreat":
            num_retreat=num_retreat+1
    
    return "attack" if num_attack>num_retreat else "retreat"

# implementation of a general
def general():
    context=zmq.Context()
    ports=config.ports
    sockets=[]
    for port in ports:
        socket=context.socket(zmq.REQ)
        socket.connect("tcp://localhost:"+port)
        sockets.append(socket)

    for socket in sockets:
        msg="attack 5000"
        print("send msg: %s" % msg)
        socket.send(msg)
        socket.recv()

    for socket in sockets:
        socket.close()

# implementation of a lieutenant (id=good/faulty,myPort=port for this lieutenant)
def lieutenant(id,myPort):
    global tree,identity
    identity=id
    t1=threading.Thread(target=server_loop,args=[myPort])
    t2=threading.Thread(target=client_loop,args=[myPort])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
        
    print("Majority voting...")
    print("Result: %s" % vote(tree[config.general_port]))

if __name__ == "__main__":
    if len(sys.argv)<2 or len(sys.argv)>3:
        print "args format: <identity> <port>"
        print "type of identity: g/lg/lf"
        print "ports for l: 5001-5006"
    elif sys.argv[1]=="g":
        general()
    else:
        lieutenant(sys.argv[1],sys.argv[2])
        
