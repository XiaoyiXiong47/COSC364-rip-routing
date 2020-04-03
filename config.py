'{
    "router1":{
        "router-id" : 1,
        "input-ports" : [6021, 6061, 6071],
        "outputs" : ["6012-1-2", "6016-5-6"，"6017-8-7"],
        "timer" : 100
    },
    "router2":{
        "router-id" : 2,
        "input-ports" : [6012, 6032],
        "outputs" : ["6021-1-1"，"6023-3-3"],
        "timer" : 100        
    },
    "router3" : {
        "router-id" : 3,
        "input-ports" : [6023, 6043],
        "outputs" : ["6032-3-2", "6034-4-4"],
        "timer" : 100        
    },
    "router4" : {
        "router-id" : 4,
        "input-ports" : [6034, 6054, 6074],
        "outputs" : ["6043-3-3", "6045-2-5", "6047-6-7"],
        "timer" : 100        
    },
    "router5" : {
        "router-id" : 5,
        "input-ports" : [6045, 6065],
        "outputs" : ["6054-2-4", "6056-1-6"],
        "timer" : 100        
    },
    "router6" : {
        "router-id" : 6,
        "input-ports" : [6016, 6056],
        "outputs" : ["6061-5-1", "6065-1-5"],
        "timer" : 100        
    },
    "router7" : {
        "router-id" : 7,
        "input-ports" : [6017, 6047],
        "outputs" : ["6071-8-1", "6074-6-4"],
        "timer" : 100        
    } 
}'