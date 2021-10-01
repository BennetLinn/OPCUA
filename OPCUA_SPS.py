from opcua import Server, Client, ua, uamethod
import datetime
import time
from random import randint
from opcua.ua import NodeId, NodeIdType

# Define the functions
def calculate_time(i_itemNo):
    itemNo = i_itemNo
    spare = int(itemNo % 10)
    height = int(itemNo % 100)
    diameter = int(itemNo % 1000)
    colour = int((itemNo - diameter) / 1000)
    diameter = int((diameter - spare) / 100)
    height = int((height - spare) / 10)
    Time = 15
    if spare == 2:
        Time += 5
    if colour == 3:
        Time += 10
    if height == 2:
        Time += 20
    return Time

# simulation whether the item is in good quality
def quality_control():
    quality = randint(1, 10)
    if quality == 1:
        return False
    else:
        return True

# production-simulation of the item
def do_item(i_itemNo):
    b_free.set_value(False)
    timepassed = 0
    itemNo = i_itemNo
    Time = calculate_time(itemNo)
    while timepassed < Time:
        pause = b_pause.get_value()
        abort = b_abort.get_value()
        if pause == False:
            time.sleep(1)
            timepassed = timepassed + 1
            print("Item: ", itemNo, "Time passed: ", timepassed, " / ", Time, "Pause: ", pause)
        if abort == True:
            break
    abort = b_abort.get_value()
    if abort == False:
        itemIO = quality_control()
        b_itemIO.set_value(itemIO)
        b_free.set_value(True)
        print("Item is finished; IO: ", itemIO)
    else:
        while abort == True:
            time.sleep(1)

# get new production number from pps
def get_productionNo():
    client.connect()
    productionNo = i_productionNo.get_value()
    itemNo = i_itemNo.get_value()
    itemIO = b_itemIO.get_value()
    root = client.get_root_node()
    print("Root node is: ", root)
    idx = client.get_namespace_index("SPS_Bridge")
    print("0:Objects", "{}:Methods".format(idx))
    obj = root.get_child(["0:Objects", "{}:Methods".format(idx)])
    res = obj.call_method("{}:get_nextItem".format(idx), productionNo, itemNo, itemIO)
    print(res)
    i_productionNo.set_value(res[0])
    i_itemNo.set_value(res[1])
    client.disconnect()

"""
Define Server
"""
opcua_sps = Server()

url_s = "opc.tcp://192.168.1.194:4841"
opcua_sps.set_endpoint(url_s)

name = "OPCUA_SPS_Server"
addspace = opcua_sps.register_namespace(name)

# Define node Parameters to addspace
node = opcua_sps.get_objects_node()
param = node.add_object(addspace, "Parameters")

# Define variables in param
i_productionNo = param.add_variable(addspace, "Production number", 0)
i_itemNo = param.add_variable(addspace, "Item number", 0)
b_itemIO = param.add_variable(addspace, "Item IO", True)
b_free = param.add_variable(addspace, "Plant is free", True)
b_pause = param.add_variable(addspace, "Pause", False)
b_abort = param.add_variable(addspace, "Abort", False)
i_productionNo.set_writable()
i_itemNo.set_writable()
b_itemIO.set_writable()
b_free.set_writable()
b_pause.set_writable()
b_abort.set_writable()

# Start Server
opcua_sps.start()
print("Server started at {}".format(url_s))
print(" At ", datetime.datetime.now())

"""
Define Client
"""
time.sleep(10)
url_c = "opc.tcp://192.168.1.194:4844"
client = Client(url_c, timeout=10000)

while True:
    itemNo = i_itemNo.get_value()
    pause = b_pause.get_value()
    productionNo = i_productionNo.get_value()
    print(itemNo)
    get_productionNo()
    if itemNo > 0:
        do_item(itemNo)
    else:
        print(i_itemNo.get_value())
        time.sleep(30)
    time.sleep(1)
