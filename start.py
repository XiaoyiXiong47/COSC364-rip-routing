import json
import socket
import sys
import threading
import select

ROUTERS = {}
ROUTING_TABLES = {} #a dictionary for storing routing tables
SOCKETS = {} #a dictionary for storing sockets for each router
BUFFERS = bytearray() # buffer to contain the routing table and msg packet

IP_ADDRESS = "127.0.0.1"



class Router:
    def __init__(self, router_id, input_no, output_no, timer):
        self.router_id = router_id
        self.table = {}
        self.input_no = input_no
        self.output_no = output_no
        self.neighbor = []
        self.timer = timer
        self.status = 1
        self.sockets = {}
    
    def create_sockets(self, output_no, ip_address):
        """a function that creates socket for each output port number and bind
        them, then return it as a dictionary, whose keys are number and values
        are sockets"""
        result = {}
        for output in output_no:
            comb = output.split('-')
            port_no = comb[0]
            dest = comb[2]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ip_address, port_no))
            s.listen() 
            result[dest] = s
        return result
        
        
        
    def add_route(self, dest_router, metric, next_router):
        """adds a new route to the routing table"""
        self.table[dest_router] = [dest_router, metric, next_router]
    
    def update_route(self, dest_router, metric, next_router):
        """updates a new route to the routing table, replace the old one"""
        self.table[dest_router] = [dest_router, metric, next_router]    
    
    #def get_output_port(output_comb):
        #"""takes a output_port as format in config file ("6012-1-2"),
        #return just a output number itself as integer (6012)"""
        #a = output_comb.split("-")
        #return int(a[0])
    
    
    
    #def get_metric(output_comb):
        #"""takes a output_pot as format in config file, return the metric as int"""    
        #a = output_comb.split("-")
        #return int(a[1])    
    
    
    
    #def get_dest_router(output_comb):
        #"""takes a output_pot as format in config file, return just the destination
        #router's id as string"""
        #a = output_comb.split("-")
        #return a[2]  
        
    
    
    def close(self):
        """turn off the router, set status to 0 (inactive), and close the sockets
        for corrosponding output port number"""
        self.status = 0
        #close sockets here
        for dest in self.sockets.keys():
            self.sockets[dest].close()
        
    def print_table(self):
        """print the routing table"""
        temp = "   {0}          {1}         {2}           {3}"
        print("======================================================")
        print("routing table for router{}".format("router " + str(self.router_id)))
        print("Destination     Metric     Next-hop      Interface") 
        for route in self.table.keys():            
            print(temp.format(self.table[route][0], self.table[route][1], self.table[route][2], self.table[route][3]))
        print("======================================================")
            
            
    def sendMessage(self, destID, IPaddr, data, SOCKETS):
        """send packet to other router"""
        for socket in SOCKETS:  # what is the key and value of  this SOCKETS dict ?
            if socket == SOCKETS[0]:
                socket.sendto(data,(IPaddr,destID) ## need to fill in dest_port
            

    def recvMessage(self,theSystem,port_no,IPaddr,destID):
        """receive message"""
        addr = (IPaddr(IPaddr),port_no)
        server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server.bind(addr)

        while True:  
            #receive data
            data,addr = server.recefrom(port_no)
            t_data = data.split("-")
            BUFFERS.write(t_data,utf8())
            #self.textout.insert(END,t
            for route in ROUTING_TABLES:
                if t_data[4] == route[0] and t_data[5] < 16:
                    dest_port = route[2]
                    break
            self.sendMessage(destID,IPaddr,data,SOCKETS)

        


def read_config_file(filename):
    """read configuration file and returns infomation about routers,
    including route-id, input-port, output-prot, and so on"""
    file = open(filename, 'r')
    data = file.read()
    routers = json.loads(data)
    #return info about routers as a dic
    return routers



#def create_routing_table (config_data):
    #"""takes a config data for a router, creates a routing table for it, and 
    #stores it in ROUTING_TABLES"""
    #table_name = "router" + str(config_data["router_id"])
    ##create an empty table and store it
    #ROUTING_TABLES[table_name] = {"router_id" : config_data["router_id"]}



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



#def print_single_table(table):
    #"""print a single routing table"""
    #temp = "   {0}          {1}         {2}           {3}"
    #for route in table.keys():
        #if route == "router_id":
            #print("======================================================")
            #print("routing table for router{}".format(str(table["router_id"])))
            #print("Destination     Metric     Next-hop      Interface") 
    #for route in table.keys():
        #if route != "router_id":              
            #print(temp.format(table[route][0], table[route][1], table[route][2], table[route][3]))
    #print("======================================================")
            


def print_routing_tables():
    """print all of the tables by calling subfunction in a loop"""
    #for table in ROUTING_TABLES.keys():
        #print_single_table(ROUTING_TABLES[table])
    for router in ROUTERS.keys():
        ROUTERS[router].print_table()



def close_sockets():
    """given by a list contains several sockets, close all"""
    for router in ROUTERS.keys():
        ROUTERS[router].close()



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
    
    
def main2():
    #read configuration file
    try:
        routers = read_config_file(filename)
    except:
        print("error occurs at read_config_file")
        sys.exit()
    
    
    #test configuration data here
    
    
    #create a Router class for each router in config file, add to ROUTERS
    for router in routers.keys():
        new_router = Router(routers[router]["router_id"], routers[router]["input_ports"], routers[router]["outputs"], routers[router]["timer"])
        new_router.create_sockets(routers[router]["outputs"], IP_ADDRESS)
        ROUTERS[routers[router]["router_id"]] = new_router
    
    
    #converge routing tables
    
    
    
    
    
    
    
    
    
    #close sockets
    close_sockets()
    
    
main2("config.json")




