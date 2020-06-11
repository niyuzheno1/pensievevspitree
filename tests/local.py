#!/usr/bin/env python
# coding: utf-8

# In[5]:


#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def topology():

    net = Mininet_wifi( controller=Controller, link=TCLink, switch=OVSKernelSwitch )

    print "*** Creating nodes"
    h1 = net.addHost( 'h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8' )
    sta1 = net.addStation( 'sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8', range='20' )
    ap1 = net.addAccessPoint( 'ap1', ssid= 'ap1-ssid', mode= 'g', channel= '1', position='30,50,0', range='30' )
    ap2 = net.addAccessPoint( 'ap2', ssid= 'ap2-ssid', mode= 'g', channel= '1', position='90,50,0', range='30' )
    ap3 = net.addAccessPoint( 'ap3', ssid= 'ap3-ssid', mode= 'g', channel= '1', position='130,50,0', range='30' )
    c1 = net.addController( 'c1', controller=Controller )
    


    print "*** Associating and Creating links"
    net.addLink(ap1, h1)
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)

    print "*** Starting network"
    net.build()
    c1.start()
    ap1.start( [c1] )
    ap2.start( [c1] )
    ap3.start( [c1] )

    

    net.startMobility(startTime=0, AC='ssf')
    net.mobility(sta1, 'start', time=20, position='1,50,0')
    net.mobility(sta1, 'stop', time=79, position='159,50,0')
    net.stopMobility(stopTime=80)

    net.plotGraph(max_x=160, max_y=160)

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()


# In[ ]:




