import json



def read_config_file(filename):
    """read configuration file and returns infomation about routers,
    including route-id, input-port, output-prot, and so on"""
    #with open(filename, 'r') as content_file:
        #data = content_file.read()
    file = open("config.py", 'r')
    data = file.read()
    print(data)
    #routers = json.loads(data)
    #print(data.keys())
    
    

    
    
def main(filename):
    """main function"""
    config_data = read_config_file(filename)
    
    
main("config.py")