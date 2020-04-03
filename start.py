import json
import socket
import sys


def read_config_file(filename):
    """read configuration file and returns infomation about routers,
    including route-id, input-port, output-prot, and so on"""
    file = open(filename, 'r')
    data = file.read()
    routers = json.loads(data)
    #return info about routers as a dic
    return routers
    


    
    
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
        sockets = [] #a list contains created sockets
        ip_addr = "127.0.0.1"
        for router in routers.keys():
            for input_port in routers[router]["input_ports"]:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((ip_addr, input_port))
                s.listen()
                sockets.append(s)
        for i in sockets:
            print(i)                
        print("sockets successfully created and binded to a port number")
    except socket.error as err: 
        print ("socket creation failed with error {}".format(err))
        sys.exit()


    
    
    
    
    
main("config.json")