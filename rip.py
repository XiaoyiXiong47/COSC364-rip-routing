import json
import socket
import sys
import threading
import select
import time
import queue

IP_ADDRESS = "127.0.0.1"
ROUTER_ID = 0      #1
INPUT_PORTS = []   # [6021, 6061, 6071]
OUTPUTS = []       # ['6012-1-2', '6016-5-6', '6017-8-7']
TIMER = []         # [peirodic_timer, timeout]
ROUTING_TABLE = {} # {2:[2, 1, 2]; 4:[4, 8, 2]; dest_id:[dest_id, metrix, next_router]}
SOCKETS = []
message_queue = [] #outgoing message queue
timer_dist = {}    #key is timer id==router id //value is sec (180,120)


#result = return of def create_sockets(input_no):
def event_loop(result):
    while True:
        readable,sendable,exceptional=select.select(result,OUTPUTS,[])
        for sock in readable:# 判断是否 router 要连接
            #listen to new connection
            if sock == s: # s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                conn, addr = s.accept()  # select 监听 socket
                result.append(conn)     #when there is data been received
                #put the connection in a queue to preserve the data we want send
                message_queue[conn]=Queue.Queue()
            else:
                port_number = s.getpeername()
                data = sock.recv(port_number) #port number is what the socket receive data from
                if data !="":
                    message_queue[s].put(data)
                    if s not in OUTPUTS:
                        OUTPUTS.append(s) # 将新出现的 router 添加到队列中
                    else:
                        pass



def read_config_file(filename):
    """read configuration file and returns infomation about routers,
    including route-id, input-port, output-prot, and so on"""
    file = open(filename, 'r')
    data = file.readlines()
    for line in data:
        line = line.split()
        if line[0] == "router_id":
            if (1 <= int(line[1])) and (int(line[1]) <= 64000):
                router_id = int(line[1])
            else:
                print("router id has to be between 1 and 64000")
                sys.exit()
        elif line[0] == "input-ports":
            input_ports = line[1].split(',')
            #convert to integer
            for i in range(len(input_ports)):
                if (1024 <= int(input_ports[i])) and (int(input_ports[i]) <= 64000):
                    input_ports[i] = int(input_ports[i])
                else:
                    print("input pot numbers have to be between 1024 and 64000")
                    sys.exit()
        elif line[0] == "outputs":
            outputs = line[1].split(',')
        elif line[0] == "timer":
            #timer value for period updates and timeout
            timer = line[1].split(',')
            if len(timer) == 2:
                #there are two timer values, one for periodic updates and one for timeout
                timer[0] = int(timer[0]) # periodic updates time inteval
                timer[1] = int(timer[1]) # timeout value
            else:
                print("there is missing timer values")
                sys.exit()
            
    #return configuration info
    return router_id, input_ports, outputs, timer


def create_sockets(input_no):
    """a function that creates socket for each input port number and bind
    them, then return it as a list"""
    try:
        result = []
        for port in input_no:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.bind((IP_ADDRESS, port))
            s.listen(5) 
            result.append(s)
        print("create_sockets() completed")
        return result
    except:
        print("create_sockets() failed")
        sys.exit()

def close_sockets():
    """close all sockets"""
    try:
        for s in SOCKETS:
            s.close()
        print("sockets successfully closed")
    except:
        print("sockets closure failed")
        sys.exit()


def print_table():
    """print the routing table"""
    temp = "   {0}          {1}         {2}           {3}"
    print("======================================================")
    print("Destination     Metric     Next-hop") 
    for route in ROUTING_TABLE.keys():            
        print(temp.format(ROUTING_TABLE[route][0], ROUTING_TABLE[route][1], ROUTING_TABLE[route][2]))
    print("======================================================")


def create_update(dest_router_id, command):
    """create a update message which will be sent to a neighbor(destID)"""
    data = bytearray()
    #adds command to indicate request packet(1) or response packet(2)
    data.append(command & 0xFF)
    #version field = 2
    data.append(2 & 0xFF)
    #router id which generated the packet
    data.append(ROUTER_ID & 0xFFFF)
    #RIP entries
    for key in ROUTING_TABLE.keys():
        route = ROUTING_TABLE[key]
        # Address Family Identifier = 0 as reserved
        data.append(0 & 0xFFFF)
        # must be zero field
        data.append(0 & 0xFFFF)
        # destination router id of this route
        data.append(route[0] & 0xFFFFFFFF)
        # must be zero field
        data.append(0 & 0xFFFFFFFF)
        data.append(0 & 0xFFFFFFFF)
        #when the next hop is not the destination of this packet
        if route[2] != dest_router_id:
            data.append(route[1] & 0xFFFFFFFF)
        else:
            #next hop is the destination of this packet
            #according to split horizon, set the metric field to infinite
            data.append(16 & 0xFFFFFFFF)
    return data


def send_periodic_updates():
    """sends periodic updates to all its neighbors"""
    for neighbor in OUTPUTS:
        neighbor = neighbor.split('-')
        output_port = int(neighbor[0])
        metric = int(neighbor[1])
        neighbor_id = int(neighbor[2])
        #create update message
        data = create_update(neighbor_id, 2)
        #send message to corresponding port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP_ADDRESS, output_port))        
        s.send(data)
        s.close()


def send_triggered_updates(destination):
    """send triggered update to the destination router"""
    data = create_update(destination, 2)
    for neighbor in OUTPUTS:
        neighbor = neighbor.split('-')
        neighbor_id = int(neighbor[2])
        if neighbor_id == destination:
            port = int(neighbor[0])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_ADDRESS, port))        
    s.send(data)
    s.close()    


#already received a packet successfully
def process_received_data(data):
    """process received data, and update routing table"""
    if data:
        global ROUTING_TABLE

        command = data[0]
        version = data[1]
        sender_id = data[2]
        if command == 1:        #packet is request, send routing table to neighbor
            print("received a request packet, send triggered update")
            send_triggered_updates(sender_id)
        else:
            for i in OUTPUTS:#response packet,#calculate the cost for itself to get to the sender of the packet,#check the routing table contained in the packet, and update own routing table
                i = i.split('-')
                if int(i[2]) == sender_id:
                    cost_to_sender = int(i[2])#process each RIP entry
            packet_length = len(data)
            i = 3
            change_flag = False # a flag indicates invalid route
            while i < packet_length:
                # Address Family Identifier
                afi = data[i]
                # must be zero field
                zero1 = data[i+1]
                # destination router id of this route
                dest = data[i+2]
                # must be zero field
                zero2 = data[i+3]
                zero3 = data[i+4]
                #metric
                metric = data[i+5]

                if zero1 == 0 and zero2 == 0 and zero3 == 0: #check the validaty of packet
                    if afi == 0:
                        total_cost = metric + cost_to_sender
                        if dest in ROUTING_TABLE:
                            if total_cost < ROUTING_TABLE[dest][1]:
                                ROUTING_TABLE[dest] = [dest, total_cost, sender_id]
                            else:
                                #check if the sender is actually the next hop of this route
                                if sender_id == ROUTING_TABLE[dest][2]:
                                    #update the metric
                                    #如果是同一更新源，无论如何都更新
                                    if total_cost <= 15:
                                        ROUTING_TABLE[dest] = [dest, total_cost, sender_id]
                                    else:
                                        ROUTING_TABLE[dest] = [dest, 16, sender_id]
                                        change_flag = True
                                else:
                                    #不是同一更新源，丢弃
                                    pass
                        else:
                            #this is a new route
                            if total_cost <= 15:
                                ROUTING_TABLE[dest] = [dest, total_cost, sender_id]
                i += 6
            if change_flag:
                # there is at least one route has become invalid
                # triggered updates
                send_periodic_updates()
    else:
        timer_periodically()
        if data:
            process_received_data(data)
            timer_1.cancel()
        else:
            garbage_collection_timer()
            #send_triggered_updates()
            if data:
                process_received_data(data)
                timer_2.cancel()
            else:
                metric_16(ROUTING_TABLE)
                send_triggered_updates()
                timer_2.cancel()




#an 180 sec timer
def timer_periodically():
    global timer_1 # set timer global to
    timer_1 = threading.Timer(180,)
    timer_1.start()  #start to init the timer  timer.cancel() to stop timer


#after 180sec ,call garbage_collection timer 120s
def garbage_collection_timer():
    global timer_2
    #function check nb alive
    timer_2 = threading.Timer(120) #120s 后，从routing table中删除 该 router 和 routing path


#after 120sec ,delete the router didn't send packet
def metric_16(timeout_router):
    """when timeout for a neighbor, set all routes through that router with metric 16""" 
    global ROUTING_TABLE
    try:
        for dest in ROUTING_TABLE.keys():
            if timeout_router == ROUTING_TABLE[dest][2]:
                ROUTING_TABLE[dest][1] = 16 #set metric to 16, keep the other parts remain the same
    except:
        print("error occured in metric_16()")
        sys.exit()
            

def del_route(dead_router):
    """delete all routes in the table whose next_router is the dead_router"""
    global ROUTING_TABLE
    try:
        for dest in ROUTING_TABLE.keys():
            if dead_router == ROUTING_TABLE[dest][2]:
                del ROUTING_TABLE[dest] # delete the route from table
    except:
        print("error occured in del_route()")
        sys.exit()
            




def main(filename):
    """the main function of the program"""
    global ROUTER_ID
    global INPUT_PORTS
    global OUTPUTS
    global TIMER
    global SOCKETS
    #filename = sys.argv[1]
    ROUTER_ID, INPUT_PORTS, OUTPUTS, TIMER = read_config_file(filename)
    #a list to store sockets, for later closure
    SOCKETS = create_sockets(INPUT_PORTS)
    send_periodic_updates()



main("config1.txt")
                    
    