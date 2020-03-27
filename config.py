#configuration file for 7 routers


{
    "router1":{
        "router-id" : 1,
        "input-ports" : [6110, 6201, 7345],
        "outputs" : ['5000-1-1', '5002-5-4'],
        'timer' : 100
    },
    "router2":{
        "router-id" : 1,
        "input-ports" : [6110, 6201, 7345],
        "outputs" : ['5000-1-1', '5002-5-4'],
        'timer' : 100        

    },
    "router3" : {
        "router-id" : 1,
        "input-ports" : [6110, 6201, 7345],
        "outputs" : ['5000-1-1', '5002-5-4'],
        'timer' : 100        

    }
}