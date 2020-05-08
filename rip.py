""" Xiaoyi Xiong - 44539786"""
""" Haobo Li - 22906859"""

import json
import socket
import sys
import select
import time
import queue
import threading
from threading import *

IP_ADDRESS = "127.0.0.1"
ROUTER_ID = 0  # 1
INPUT_PORTS = []  # [6021, 6061, 6071]
OUTPUTS = []  # ['6012-1-2', '6016-5-6', '6017-8-7']
TIMER = []  # [peirodic_timer, timeout, garbage-collection]
ROUTING_TABLE = {}  # {2:[2, 1, 2]; 4:[4, 8, 2]; dest_id:[dest_id, metrix, next_router]}
SOCKETS = []
MESSAGE_QUEUE = []  # outgoing message queue
TIMER_DIC = {}  # key is timer id==router id //value is sec (180,120)
UPDATE_TIMER = None
PRINT_TIMER = None


class repeating_timer(Timer):

    def __init__(self, interval, function, args=[], kwargs={}):
        Timer.__init__(self, interval, function, args=[], kwargs={})

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                self.finished.set()
                break

            self.function(*self.args,**self.kwargs)


# result = return of def create_sockets(input_no):
def event_loop():
    while True:
        #try:
        readable, _, _ = select.select(SOCKETS, [], []) # all conne list contain the input port sockets
        for s in readable:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if data:
                process_received_data(data)
            else:
                continue 
            conn.close()
        #except:
            #print("error occured in event_loop")
            #quit()



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
            # convert to integer
            for i in range(len(input_ports)):
                if (1024 <= int(input_ports[i])) and (int(input_ports[i]) <= 64000):
                    input_ports[i] = int(input_ports[i])
                else:
                    print("input pot numbers have to be between 1024 and 64000")
                    sys.exit()
        elif line[0] == "outputs":
            outputs = line[1].split(',')
        elif line[0] == "timer":
            # timer value for period updates and timeout
            timer = line[1].split(',')
            if len(timer) == 3:
                # there are two timer values, one for periodic updates and one for timeout
                timer[0] = int(timer[0])  # periodic updates time inteval
                timer[1] = int(timer[1])  # timeout value
                timer[2] = int(timer[2])  # garbage-collection timer
            else:
                print("there is missing timer values")
                sys.exit()
    # return configuration info
    return router_id, input_ports, outputs, timer


def create_sockets():
    """a function that creates socket for each input port number and bind
    them, then return it as a list"""
    # try:
    result = []
    try:
        for port in INPUT_PORTS:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((IP_ADDRESS, port))
            s.listen(5)
            result.append(s)
        print("create_sockets() completed")
        return result
    except:
        print("create_sockets() failed")
        sys.exit()


def create_table():
    """initialise ROUTING_TABLE, create routes for thoes in the configuration file"""
    global ROUTING_TABLE
    global TIMER_DIC
    for i in OUTPUTS: #OUTPUTS = []  # ['6012-1-2', '6016-5-6', '6017-8-7']
        info = i.split('-')  # [port, metric, router_id]
        neighbor_id = int(info[2])
        metric = int(info[1])
        output_port = int(info[0])
        ROUTING_TABLE[neighbor_id] = [neighbor_id, metric, neighbor_id]
        set_timer(TIMER[1], neighbor_id)


def print_table():
    """print the routing table"""
    temp = "   {0}          {1}         {2} "
    print("======================================================")
    print("Destination     Metric     Next-hop")
    for route in ROUTING_TABLE.keys():
        print(temp.format(ROUTING_TABLE[route][0], ROUTING_TABLE[route][1], ROUTING_TABLE[route][2]))
    print("======================================================")


def create_update(dest_router_id, command, first_time=0):
    """create a update message which will be sent to a neighbor(destID)"""
    data = bytearray()
    # adds command to indicate request packet(1) or response packet(2)
    data.append(command & 0xFF)
    # version field = 2
    data.append(2 & 0xFF)
    # router id which generated the packet
    data.append(ROUTER_ID & 0xFFFF)
    # RIP entries
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
        # when the next hop is not the destination of this packet
        if route[2] != dest_router_id:
            data.append(route[1] & 0xFFFFFFFF)
        else:
            # next hop is the destination of this packet
            if first_time == 0:
                # according to split horizon, set the metric field to infinite
                data.append(16 & 0xFFFFFFFF)
            else:
                data.append(route[1] & 0xFFFFFFFF)
    return data


def send_periodic_updates(first_timer=0):
    """sends periodic updates to all its neighbors"""
    for neighbor in OUTPUTS:
        neighbor = neighbor.split('-')
        output_port = int(neighbor[0])
        metric = int(neighbor[1])
        neighbor_id = int(neighbor[2])
        # create update message
        if first_timer == 0:
            data = create_update(neighbor_id, 2)
        else:
            data = create_update(neighbor_id, 2, 1)
        # send message to corresponding port
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((IP_ADDRESS, output_port))
            s.send(data)
            s.close()
            #print("data : ", data)
            print("successfully sent data to", str(output_port))
        except ConnectionRefusedError:
            print("Connection Refused for {}, check the status of corresponding socket".format(output_port))


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


# already received a packet successfully
def process_received_data(data):
    """process received data, and update routing table"""
    global ROUTING_TABLE
    command = data[0]
    version = data[1]
    sender_id = data[2]
    set_timer(TIMER[1], sender_id)
    print("processing received data from {} ........".format(sender_id))

    
    #restart timeout timer for sender router
    if command == 1:  # packet is request, send routing table to neighbor
        print("received a request packet, send triggered update")
        send_triggered_updates(sender_id)
    else:
        for i in OUTPUTS:  # response packet,#calculate the cost for itself to get to the sender of the packet,#check the routing table contained in the packet, and update own routing table
            i = i.split('-')
            if int(i[2]) == sender_id:
                cost_to_sender = int(i[1])  # process each RIP entry
        #print("cost to router {} is {}".format(sender_id, cost_to_sender))
        packet_length = len(data)
        i = 3
        change_flag = False  # a flag indicates invalid route
        while i < packet_length:
            # Address Family Identifier
            afi = data[i]
            # must be zero field
            zero1 = data[i + 1]
            # destination router id of this route
            dest = data[i + 2]
            # must be zero field
            zero2 = data[i + 3]
            zero3 = data[i + 4]
            # metric
            metric = data[i + 5]

            change_flag = False
            if (zero1 == 0) and (zero2 == 0) and (zero3 == 0):  # check the validaty of packet
                if afi == 0:
                    total_cost = metric + cost_to_sender
                    if dest in ROUTING_TABLE.keys():
                        if total_cost < ROUTING_TABLE[dest][1]:
                            ROUTING_TABLE[dest] = [dest, total_cost, sender_id]
                            set_timer(TIMER[1], dest)
                        else:
                            # check if the sender is actually the next hop of this route
                            if sender_id == ROUTING_TABLE[dest][2]:
                                # update the metric
                                # 如果是同一更新源，无论如何都更新
                                if total_cost <= 15:
                                    ROUTING_TABLE[dest] = [dest, total_cost, sender_id]
                                    set_timer(TIMER[1],dest)
                                else:
                                    if ROUTING_TABLE[dest][1] == 16:
                                        #if the current table has this route with metric 16, do not reset the timeout
                                        print("route to dest {} through {} is still invalid".format(dest, sender_id))
                                    else:
                                        #the route has become invalid for the first time
                                        ROUTING_TABLE[dest] = [dest, 16, sender_id]
                                        set_timer(TIMER[2],dest)
                                        change_flag = True
                                        print("route to dest {} through {} has become invalid".format(dest, sender_id))
                            else:
                                # 不是同一更新源，丢弃
                                pass
                    else:
                        # this is a new route
                        if (total_cost <= 15) and (dest != ROUTER_ID):
                            ROUTING_TABLE[dest] = [dest, total_cost, sender_id]
                            set_timer(TIMER[1], dest)
                        elif (dest == ROUTER_ID) and (metric <= 15) and (sender_id not in ROUTING_TABLE.keys()):
                            ROUTING_TABLE[sender_id] = [sender_id, metric, sender_id]
                            set_timer(TIMER[1], sender_id)
                            
                            
                else:
                    print("the Address Family Identifier field dose not match")
            else:
                print("the Must Be Zero field is not zero!")
            i += 6
        if change_flag:
            # there is at least one route has become invalid
            # triggered updates
            send_periodic_updates()
    print("process of received data from {} has completed".format(sender_id))
    print_table()



def set_timer(interval, router_id):  #TIMER = []  # [peirodic_timer, timeout, garbage-collection]
    """create threading timer for a neighbor router, and store it in timer_dist"""
    global TIMER_DIC
    if interval == TIMER[1]:  # timeout interval
        if router_id not in TIMER_DIC.keys():
            # this is a new connected router, set a new timer for it
            t = threading.Timer(interval, metric_16, (router_id,))
            t.start()
            TIMER_DIC[router_id] = t
        else:
            # restart the timeout timer
            t = TIMER_DIC[router_id]
            t.cancel()
            del TIMER_DIC[router_id]
            new_t = threading.Timer(interval, metric_16, (router_id,))
            new_t.start()
            TIMER_DIC[router_id] = new_t
    elif interval == TIMER[2]:  # garbage collection
        # cancle timeout timer, and create a garbage collection timer
        t = TIMER_DIC[router_id]
        t.cancel()
        del TIMER_DIC[router_id]
        new_t = threading.Timer(interval, del_route, (router_id,))
        new_t.start()
        TIMER_DIC[router_id] = new_t
    else:
        print("invaild timer value")
        quit()

# after 120sec ,delete the router didn't send packet
def metric_16(timeout_router):
    """when timeout for a neighbor, set all routes through that router with metric 16"""
    global ROUTING_TABLE
    try:
        print("timeout occured, start garbage-collection timer for {} and set metic 16".format(timeout_router))
        for dest in ROUTING_TABLE.keys():
            if dest == timeout_router:
                ROUTING_TABLE[dest][1] = 16  # set metric to 16, keep the other parts remain the same
        #start garbage-collection timer
        set_timer(TIMER[2],timeout_router)
        # send trigged update
        send_periodic_updates()
    except:
        print("error occured in metric_16()")
        sys.exit()


def del_route(dead_router):
    """delete all routes in the table whose next_router is the dead_router"""
    global ROUTING_TABLE
    #try:
    del ROUTING_TABLE[dead_router]  # delete the route from table
    print("del_route for {} successfully".format(dead_router))
    #except:
        #print("error occured in del_route()")
        #sys.exit()



def del_timer():
    """cancle all timer in TIMER_DIC"""
    global TIMER_DIC
    for router_id in TIMER_DIC.keys():
        t = TIMER_DIC[router_id]
        t.cancel()
        del TIMER_DIC[router_id]


def close_sockets():
    """close all sockets"""
    try:
        for s in SOCKETS:
            s.close()
        print("sockets successfully closed")
    except:
        print("sockets closure failed")
        sys.exit()


def quit():
    """when error happens, quit the program, reset all global variables,
    close all sockets, and cancel all the timers"""
    global ROUTER_ID
    global INPUT_PORTS
    global OUTPUTS
    global TIMER
    global SOCKETS
    global UPDATE_TIMER
    global PRINT_TIMER
    ROUTER_ID = 0
    INPUT_PORTS = []
    OUTPUTS = []
    TIMER = []
    if len(SOCKETS) > 0:
        close_sockets()
    if len(TIMER_DIC) > 0:
        del_timers()
    UPDATE_TIMER.cancel()
    PRINT_TIMER.cancel()
    sys.exit()


def main():
    """the main function of the program"""
    global ROUTER_ID
    global INPUT_PORTS
    global OUTPUTS
    global TIMER
    global SOCKETS
    global UPDATE_TIMER
    global PRINT_TIMER
    filename = sys.argv[1]
    ROUTER_ID, INPUT_PORTS, OUTPUTS, TIMER = read_config_file(filename)
    print("ROUTER_ID :  ", str(ROUTER_ID))
    print("INPUT_PORTS :  ")
    print(INPUT_PORTS)
    print("OUTPUTS :  ")
    print(OUTPUTS)
    print("TIMER :  ")
    print(TIMER)

    # a list to store sockets, for later closure
    SOCKETS = create_sockets()
    create_table()
    print_table()
    send_periodic_updates(1) # 1 means first_time is True
    UPDATE_TIMER = repeating_timer(TIMER[0], send_periodic_updates)
    UPDATE_TIMER.start()
    PRINT_TIMER = repeating_timer(TIMER[0], print_table)
    PRINT_TIMER.start()
    event_loop()


main()