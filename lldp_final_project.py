from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import RpcError
from jnpr.junos.exception import CommitError
from lxml import etree as et
from jnpr.junos.utils.config import Config
from graphviz import Graph


#Initializing the devices array with the ip addresses of the routers that need to be configured
devices= ['192.168.1.7','192.168.1.8','192.168.1.9','192.168.1.10','192.168.1.11','192.168.1.12']

#Interface configuration of all the interfaces needed to be configured for a given router with their respective ip addresses
if_config_R1 = { 'ge-0/0/1': '72.114.96.1/24', 'ge-0/0/2':'72.114.97.1/24' , 'lo0':'72.114.103.1/24' }
if_config_R2 = { 'ge-0/0/1': '72.114.97.2/24', 'ge-0/0/2': '72.114.98.1/24' , 'lo0': '72.114.104.1/24' }
if_config_R3 = { 'ge-0/0/1': '72.114.99.1/24', 'ge-0/0/2': '72.114.96.2/24' ,'ge-0/0/3': '72.114.98.2/24', 'ge-0/0/4':'72.114.100.1/24', 'lo0':'72.114.105.1/24'}
if_config_R4 = { 'ge-0/0/1': '72.114.101.1/24' , 'ge-0/0/3': '72.114.100.2/24' , 'lo0':'72.114.106.1/24' }
if_config_R5 = { 'ge-0/0/1': '72.114.101.2/24' , 'ge-0/0/2':'72.114.99.2/24' ,'ge-0/0/3':'72.114.102.1/24', 'lo0': '72.114.107.1/24' }
if_config_R6 = { 'ge-0/0/2': '72.114.102.2/24' , 'lo0':'72.114.108.1/24' }

#Initializing the interface array with interface configuration of the 6 routers
if_config= [if_config_R1, if_config_R2, if_config_R3, if_config_R4, if_config_R5, if_config_R6 ]

#Defining the routers array with names of the 6 routers along with their IP addresses
router_names= { 'router007' : ['Router R1\n192.168.1.7',0], 'router008' : ['Router R2\n192.168.1.8',1], 'router009' : ['Router R3\n192.168.1.9',2], 'router010' : ['Router R4\n192.168.1.10',3] , 'router011' : ['Router R5\n192.168.1.11',4], 'router012' : ['Router R6\n192.168.1.12',5] }

#Dictionary to store the lldp information we learn from neighboring routers
result={}

#Main for loop for the configuration of the interfaces and their respective ip addresses for the 6 routers and enable LLDP on all interfaces of the routers 
for i in range(0,6): 
	#Creating a device instance for each of our routers with correct username and password
	device = Device(host = devices[i], user='labuser', password='Labuser')
	device.bind(conf=Config)
	try:
		#Starting the NETCONF session after user has been authenticated 
		device.open()
		#A dcitionary to hold the values for the template variables for the different interfaces
		var_dict = { 'if_config': if_config[i]}
		#Using load method to load the right variables onto the right template file and merge with the existing configuration 
		device.conf.load(template_path = 'router_configuration.conf', template_vars= var_dict, merge=True )
		#We commit our changes to configuration and record its succes
		success= device.conf.commit()
		print('success = {0}'.format(success))	
		
		#Catch errors while trying to connect to the router using NETCONF
	except ConnectError as err:
		print('\nConnection error: ' + repr(err))

		#Catch error while trying to commit changes to the configuration of the routers
	except CommitError as err:
		print('\nCommit error: ' + repr(err))

		#Close the NETCONF session with the router after we are done with the changes to the configuration 
	finally:
		device.close()

#Loop to use an rpc call to find out lldp connectivity information for each router
for i in range(0,6): 
	device = Device(host = devices[i], user='labuser', password='Labuser')
	try:
		device.open()
		#Rpc call to get lldp information about the local router
		response_local=device.rpc.get_lldp_local_info()
		
		#Accesing the name of the local router
		local_rname = response_local[1].text
		
		#Rpc call to get lldp information about the other routers and their interfaces to which the local router is connected
		response=device.rpc.get_lldp_neighbors_information()
		result[local_rname] = []
		for j in response:
			interface_info_list=[]
			#Accessing the local interface
			interface_info_list.append(j[0].text)
			#Accessing the remote interface the local interface is connected to 
			interface_info_list.append(j[4].text)
			#Accessing the name of the remoter router
			interface_info_list.append(j[5].text)
			result[local_rname].append(interface_info_list)

	#Catch errors while trying to connect to the router using NETCONF
	except ConnectError as err:
		print('\nConnection error: ' + repr(err))

	#Catch errors encountered while performing the lldp rpc calls
	except RpcError as err:
		print('\Rpc error: ' + repr(err))

	#Close the NETCONF session with the router after we are done with the lldp rpc  
	finally:
		device.close()



#Using Digraph in graphviz to construct a graph representing the network topology we have learned from the lldp rpc calls
dot = Graph(format = 'png')

#Describing attributes of the graph like background color, node color, font color and style
dot.attr( rankdir = 'LR', ranksep='2',nodesep='2.3',bgcolor='lightcoral:lemonchiffon', label='NETWORK GRAPH', fontstyle='bold', lblstyle='above', fontsize='16')


#Loop for looping over the result dictionary and constructing the different nodes and edges
for key in result:

	#Adding the 6 different routers as nodes to the graph and describing the shape, color and font of the nodes
	dot.node(key,router_names[key][0], shape='circle',style='filled', fillcolor ='firebrick',fontcolor='white')

	#Loop for each interface of each node which is displayed as an edge for a particular node
	for interface_list in result[key]:
		#Check to see if the interface belongs to the switch in which case we ignore it since we do not want to include that connection in our network topology
		if (interface_list[2] == 'switch207' or key > interface_list[2]):
			continue
		#fetching connected routers name
		connected_router_key = interface_list[2]
		#adding interfaces name with ip addresses
		interface_list[0]=interface_list[0][:len(interface_list[0])-2]
		interface_list[1]=interface_list[1][:len(interface_list[1])-2]
		interface_tail = interface_list[0] + ' (' + if_config[router_names[key][1]][interface_list[0]] + ')'
		interface_head = interface_list[1] + ' (' + if_config[router_names[connected_router_key][1]][interface_list[1]] + ')'
		#Adding an edge to the particular node in our graph which represents the different interfaces of each router
		dot.edge(key,interface_list[2], lblstyle='above', headlabel='       '+interface_head+'     ', fontsize='13',minlen='2.3', taillabel='           '+interface_tail+'    ', arrowhead = 'None')

#Using function to render our constructed graph to a viewable graph and saving it in a test file
dot.render('network-output/routers_configuration', view=True)


