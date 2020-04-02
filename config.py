#configuration file for 7 routers


{
    "router1":{
        "router-id" : 1,
        "input-ports" : [6012, 6016, 6017],
        "outputs" : ['6121-1-2', '6161-5-6'，'6171-8-7'],
        'timer' : 100
    },
    "router2":{
        "router-id" : 2,
        "input-ports" : [6021, 6023],
        "outputs" : ['6112-1-1'，'6132-3-3'],
        'timer' : 100        

    },
    "router3" : {
        "router-id" : 3,
        "input-ports" : [6032, 6034],
        "outputs" : ['6123-3-2', '6143-4-4'],
        'timer' : 100        

    },
    "router4" : {
        "router-id" : 4,
        "input-ports" : [6043, 6045, 6047],
        "outputs" : ['6134-3-3', '6154-2-5', '6174-6-7'],
        'timer' : 100        

    },
    "router5" : {
        "router-id" : 5,
        "input-ports" : [6054, 6056],
        "outputs" : ['6145-2-4', '6165-1-6'],
        'timer' : 100        

    },
    "router6" : {
        "router-id" : 6,
        "input-ports" : [6061, 6065],
        "outputs" : ['6116-5-1', '6156-1-5'],
        'timer' : 100        

    },
    "router7" : {
        "router-id" : 7,
        "input-ports" : [6071, 6074],
        "outputs" : ['6117-8-1', '6147-6-4'],
        'timer' : 100        

    } 
}