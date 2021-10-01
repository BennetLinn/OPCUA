from opcua import Server, Client, ua, uamethod
import time
import datetime
from opcua.ua import NodeId, NodeIdType

productionNo_1 = 0
itemNo_1 = 0

# Get next Item / ProcutionNo from PPS
@uamethod
def get_nextItem(parent, p_productionNo, p_itemNo, p_itemIO):
    itemNo = p_itemNo
    productionNo = p_productionNo
    itemIO = p_itemIO
    """
    HTTP Anfrage an PPS & Rückantwort mit ProductionNo + ItemIO
    """
    productionNo = int(input("Produktion Nummer eingeben: "))
    itemNo = int(input("Artikel Nummer eingeben: "))
    return productionNo, itemNo


"""
Pause, cancel and start production
mit HTTP Verbindungen zur PPS
"""
# setting the production process to pause
def set_pause():
    b_pause.set_value(True)

# abort the production item
def set_abort():
    b_abort.set_value(True)

def start():
    b_pause.set_value(False)
    b_abort.set_value(False)


"""
Define Server
"""
spsbridge = Server()

url_s = "opc.tcp://192.168.1.194:4844"
spsbridge.set_endpoint(url_s)

name = "SPS_Bridge"
addspace = spsbridge.register_namespace(name)

# Define node Parameters to addspace
node = spsbridge.get_objects_node()
param = node.add_object(addspace, "Parameters")
meth = node.add_object(addspace, "Methods")

# Define variables in param
i_test = param.add_variable(addspace, "Test", 0)
i_test.set_writable()

# Define methods in meth
get_nextItem_node = meth.add_method(addspace, "get_nextItem", get_nextItem, [ua.VariantType.Int64, ua.VariantType.Int64, ua.VariantType.Boolean], [ua.VariantType.Int64, ua.VariantType.Int64])

# Start Server
spsbridge.start()
print("Server started at {}".format(url_s))
print(" At ", datetime.datetime.now())

"""
Define Client
"""
time.sleep(10)
url_c = "opc.tcp://192.168.1.194:4841"
client = Client(url_c)
try:
    client.connect()
    print("Client connected at {}".format(url_c))
except:
    print("Client couldn't connect to {}".format(url_c))

while True:
    i_productionNo = client.get_node("ns=2;i=2")
    i_itemNo = client.get_node("ns=2;i=3")
    b_itemIO = client.get_node("ns=2;i=4")
    b_free = client.get_node("ns=2;i=5")
    b_pause = client.get_node("ns=2;i=6")
    b_abort = client.get_node("ns=2;i=7")
    productionNo = i_productionNo.get_value()
    itemNo = i_itemNo.get_value()
    itemIO = b_itemIO.get_value()
    free = b_free.get_value()
    time.sleep(1)