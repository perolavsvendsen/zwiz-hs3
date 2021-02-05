"""
    Integration tests. Deactivated by default to avoid
    putting real data into this module.

    You are encouraged to reactivate and insert your own
    values to ensure package is behaving as expected.

"""

import pytest
import zwiz

#IP = "000.000.000.000"
#PORT = 12345
#
#network = zwiz.Network(ip=IP, port=PORT)
#
#def test_network():
#    """
#    Assert that the attributes of the network 
#    are represented as expected.
#    """
#
#    # check that the central node has the expected value
#    # usually this is 1
#    assert network.node_id == 1
#
#    # check that total number of nodes is as expected
#    # this number can be found on the top of the z-wave page
#    assert network.number_of_nodes == 41
#
#def test_nodes():
#    """
#    Assert that the nodes look as expected
#    """
#
#    node = network.nodes[5]
#    assert node.node_id == 5
#    assert node.neighbors == [16, 18, 22, 24, 26, 27, 38, 44, 47, 55, 60, 62, 64, 65, 72, 73]
#    assert node.last_working_route == [72]
#
#    node = network.nodes[29]
#    assert node.node_id == 29
#    assert node.neighbors == []
#    assert node.last_working_route == [22,13,11]
