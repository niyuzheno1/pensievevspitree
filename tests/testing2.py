from mininet.net import Mininet
from mininet.node import Controller
from mininet.log import setLogLevel, info, warn
from mininet.cli import CLI


def topology():
    net = Mininet( controller=Controller )

    info("*** Adding controller\n'")
    net.addController( 'c0' )

    info("*** Creating nodes\n")
    h1 = net.addHost( 'h1', ip='10.0.0.1' )


   

    info("*** Starting network\n")
    net.start()
    h1.cmd('cd /home/wifi/Desktop/tests')
    h1.cmd('python testing.py')
    

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()