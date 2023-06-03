# Enable-LLDP
The objective of this project is to enable and run LLDP. LLDP is a layer 2 protocol which stands for Link Layer Discovery Protocol. We have to enable LLDP on 6 routers that have been provided to us via a network topology and then gather LLDP connectivity information from the neighboring routers from each router and display the network connectivity information gathered in a graphical form using Python graphical libraries such as graphviz.
1. First we configure interfaces and IP addresses for the different interfaces of the routers provided to us in the network topology
2. Then we need to enable and run LLDP on all the interfaces for all the routers that have been provided to us
3. Third step is then to gather connectivity information from the neighboring routers that also have LLDP enabled and save the information to help us form a picture of the network connectivity
4. Finally, we use that information that we have collected to construct the network topology and we use graphviz, a library in Python, to graphically represent this information


