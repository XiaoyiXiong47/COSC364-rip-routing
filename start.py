import json
import socket
import sys
import threading


ROUTING_TABLES = {} #a dictionary for storing routing tables
SOCKETS = {} #a dictionary for storing sockets for each router

IP_ADDRESS = "127.0.0.1"



def read_config_file(filename):
    """read configuration file and returns infomation about routers,
    including route-id, input-port, output-prot, and so on"""
    file = open(filename, 'r')
    data = file.read()
    routers = json.loads(data)
    #return info about routers as a dic
    return routers



def create_routing_table (config_data):
    """takes a config data for a router, creates a routing table for it, and 
    stores it in ROUTING_TABLES"""
    table_name = "router" + str(config_data["router_id"])
    #create an empty table and store it
    ROUTING_TABLES[table_name] = {"router_id" : config_data["router_id"]}



def get_output_port(output_comb):
    """takes a output_port as format in config file ("6012-1-2"),
    return just a output number itself as integer (6012)"""
    a = output_comb.split("-")
    return int(a[0])



def get_metric(output_comb):
    """takes a output_pot as format in config file, return the metric as int"""    
    a = output_comb.split("-")
    return int(a[1])    



def get_dest_router(output_comb):
    """takes a output_pot as format in config file, return just the destination
    router's id as string"""
    a = output_comb.split("-")
    return a[2]  
    
    
    
def get_socket_with_portno (portno):
    """given by a list of sockets and a port number, return a specific socket
    that is binded to that port number"""
    for router in SOCKETS.keys():
        for s in SOCKETS[router]:
            if s.getsockname()[1] == portno:
                return s
    # An error handler here



def print_single_table(table):
    """print a single routing table"""
    temp = "   {0}          {1}         {2}           {3}"
    for route in table.keys():
        if route == "router_id":
            print("======================================================")
            print("routing table for router{}".format(str(table["router_id"])))
            print("Destination     Metric     Next-hop      Interface") 
    for route in table.keys():
        if route != "router_id":              
            print(temp.format(table[route][0], table[route][1], table[route][2], table[route][3]))
    print("======================================================")
            


def print_routing_tables():
    """print all of the tables by calling subfunction in a loop"""
    for table in ROUTING_TABLES.keys():
        print_single_table(ROUTING_TABLES[table])



def close_sockets():
    """given by a list contains several sockets, close all"""
    for router in SOCKETS.keys():
        for s in SOCKETS[router]:
            s.close()



def del_route(table, route):
    """delete certain route from table"""
    del table[route]



def main(filename):
    """main function"""
    
    #read configuration file
    try:
        routers = read_config_file(filename)
    except:
        print("error occurs at read_config_file")
        sys.exit()
    
    
    #test configuration data here
        
    
    
    #create sockets for each input port number
    try:
        for router in routers.keys():
            for input_port in routers[router]["input_ports"]:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((IP_ADDRESS, input_port))
                s.listen()
                if router not in SOCKETS.keys():
                    SOCKETS[router] = [s]
                else:
                    SOCKETS[router].append(s)
        for i in SOCKETS.keys():
            print(SOCKETS[i])
        print("sockets successfully created and binded to a port number")
    except socket.error as err: 
        print ("socket creation failed with error {}".format(err))
        sys.exit()

    
    #create routing tables for each routers
    try:
        for router in routers.keys():
            create_routing_table(routers[router])
        print("routing table creation successfully")
    except:
        print("routing table creation failed")
    
    
    #print out current routing table
    print_routing_tables()
    
    
    
    
    
main("config.json")





