import os


from mininet.node import RemoteController,Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, mesh, physicalMesh
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference

def topology():
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    h1 = net.addHost('h1',  ip='10.0.0.3/8')
    h2 = net.addHost('h2',  ip='10.0.0.4/8')
    sta1 = net.addStation('sta1', ip='10.0.0.1/8',  min_x=55, max_x=60, min_y=55, max_y=60, min_v=5, max_v=5 )
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', min_x=20, max_x=30, min_y=20, max_y=30, min_v=5, max_v=5 )
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', model='DI524',
                             mode='g', channel='1', position='50,50,0')
    c1 = net.addController('c1', controller=lambda name: RemoteController( name, ip='127.0.0.1' ) )

    

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.addLink(ap1, h1)
    net.addLink(ap1, h2)


    net.plotGraph(max_x=100, max_y=100)

    net.setMobilityModel(time=0,  model='RandomDirection',  max_x=100, max_y=100)

    info("*** Starting network\n")
    net.build()
    c1.start()
    sta1.cmd('cd /var/www/html')
    sta1.cmd('python -m SimpleHTTPServer & ')
    sta2.cmd('cd /home/wifi/video/pensieve/real_exp')


    ap1.start([c1])

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
