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
    
    
    #create sockets for each input port number
    #try:
    d_sockets = {} #a dictionary for created sockets
    ip_addr = socket.gethostname()
    for router in routers.keys():
        for input_port in routers[router]["input_ports"]:
            s_name = "s" + str(input_port)[2] + str(input_port)[3]
            d_sockets[s_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#.connect((ip_addr, input_port))
    print(d_sockets.keys())        
    #except:
        #print("sockets creation failed")
    
    
    
    
    
main("config.json")