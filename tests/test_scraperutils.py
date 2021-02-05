""" 
Unit tests of the utils

HTML-snippets used are designed to look similar to those being produced by the Z-wave
plugin in HS3. If you want to use this module, you are encouraged to replicate these
tests with data from your own HS3 instance.

Integration tests are also available, but deactivated by default to avoid having to
put real code owned by HS into this module. You are encouraged to activate the
integration tests and replicate with your own data.

"""

import pytest
from bs4 import BeautifulSoup
from zwiz._utils import Scrapers

def test_get_main_tables():

    html = """
    <table id=headertable>
    <tr><td><some><tag>Current Z-Wave Networks</tag></some></td>
    <td>Another td</td></tr></table><table id=nodestable><tr>
    <td><some><tag>Node Information</tag></some></td>
    <td>Another td</td></tr>
    </table>

    """

    soup = BeautifulSoup(html, "html5lib")

    headertable, nodestable = Scrapers._get_main_tables(soup)
    assert 'headertable' in str(headertable)
    assert 'nodestable' in str(nodestable)

def test_get_header():
    html = """
    <table><tr><td>Current Z-Wave Networks</td></tr><tr>
    <td>Network Friendly Name</td><td>HomeID</td><td>Number of Nodes</td>
    <td>Interface Name</td><td>Interface Model</td><td>Node ID</td></tr>
    <tr><td>Network E8A1234A</td><td>E8A1234A</td><td>41</td><td>UZB1</td>
    <td>Sigma Designs UZB</td><td>1</td></tr><tr><td>&nbsp;</td></tr></table>
    """

    soup = BeautifulSoup(html, "html5lib")
    header = Scrapers._get_header(soup)
    assert header.get('NodeID') == 1
    assert header.get('Number of Nodes') == 41

def test_get_nodes():
    html = """
    <table>
    <tr><td><b><font size='4'>60</font></b></td><td class='tablecell' align='left'  colspan='10' >
    <b>Full Name: </b></font><a href="/dedfvdfvf" target="_blank" >The full name of the node</a>
    </td><td><b>Polling: </b></font>Polling Disabled</td></tr><tr><td>
    <b>Manufacturer: </b></font><br>Some manufacturer</td><td>
    <b>Type:</b></font><br> 0x203</td><td><b>ID:</b></font>
    <br> 0x1000</td><td><b>Listens:</b></font><br>Yes</td>
    <td><b>Version: </b></font>abcd1234 <b>Firmware: </b></font>3.2<b> Hardware: </b>
    </font>3</td><td><b><b>Neighbor Count:</b></font></b><br>16</td><td><b>
    Speed:</b></font><br>100Kbps</td></tr><tr ><td><b><b>Neighbors: </b></font></b>
    5, 16, 18, 22, 24, 26, 27, 38, 44, 47, 55, 62, 64, 65, 72, 73</td></tr><tr><td><b>'
    <b>Last Working Route: </b></font></b>22->13 (40K)</td><td class='tablecell' align='left'  colspan='9' >
    Set Route: <script>removed script</script><div id='set_dfvdfvdfv' title='Edit Value'>
    <input/></div><span title='dfvfvfd'><input /></span></td></tr><tr ><td><b>Uses Interface: 
    </b></font>UZB1 (1)</td><td class='tablecell' align='left'  colspan='12' ><b>Basic Type: 
    </b></font>ROUTING SLAVE, &nbsp;&nbsp;&nbsp;&nbsp;<b>Generic Type: </b></font>
    SWITCH BINARY, &nbsp;&nbsp;&nbsp;&nbsp;<b>Specific Type: </b></font>POWER SWITCH BINARY
    </td></tr><tr ><td class='tablecell' ><b>Command Classes:</b></font><br>
    <table ><tr ><td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td><font color='#0066FF'><b>Supported:</b></font></td>
    <td align='left'  colspan='8' >vdfvf</td><tr ><td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td>
    <font color='#9933FF'><b>Controlled:</b></font></td><td align='left'  colspan='8' >Switch Multilevel</td>
    <tr ><td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td><font color='#0066FF'><b>Supported </b></font>
    <font color='#E99B00'><b>Secure:</b></font></td><td align='left'  colspan='8' ></td><tr><td>
    &nbsp;&nbsp;&nbsp;&nbsp;</td><td><font color='#9933FF'><b>Controlled </b></font><font color='#FF33CC'>
    <b>Secure:</b></font></td><td align='left'  colspan='8' >xvdfvd</td></table></td></tr><tr ><td>
    <b>Child Device: </b></font><a href="/deviceutility?ref=868&edit=1" target="_blank" >Switch Binary 1</a>
    </td><td><b>CC:</b></font>&nbsp;Switch Binary <b>EP:</b></font>&nbsp;1</td>
    <td><b>Polling: </b></font>Polling Disabled</td>
    </tr><tr ><td><b>Child Device: </b></font><a href="/devicedfvdfvf" target="_blank" >Switch Binary 2</a>
    </td><td><b>CC:</b></font>&nbsp;Switch Binary <b>EP:</b></font>&nbsp;2</td><td>
    <b>Polling: </b></font>Polling Disabled</td></tr><tr ><td><b>Child Device: </b>
    </font><a href="/devicdfdfvdf" target="_blank" >Heat Notification</a></td><td><b>CC:</b></font>
    &nbsp;Notification <b>Ver:</b></font>&nbsp;5</td><td><b>Polling: </b></font>
    Polling Disabled</td></tr><tr ><td><b>Child Device: </b></font><a href="/devicedfvdfvf" target="_blank" >
    Application Status</a></td><td><b>CC:</b></font>&nbsp;Application Status</td><td>
    <b>Polling: </b></font>Polling Disabled</td></tr><tr ><td >&nbsp;&nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td></tr>
    </table>

    """
    soup = BeautifulSoup(html, "html5lib")
    nodes = Scrapers._get_nodes(soup)
    assert len(nodes) == 1
    node = nodes[60]
    assert node.name == "The full name of the node"
    assert node.neighbors == [5, 16, 18, 22, 24, 26, 27, 38, 44, 47, 55, 62, 64, 65, 72, 73]
    assert node.last_working_route == [22,13]
    assert node.node_id == 60

def test_find_pair():
    html = """
        <some><html>key:</some></html><some>value</close>
        """
    assert Scrapers.find_pair_value(html, "key") == "value"

    html = """
        <tr ><td class='tableheader'  colspan='15' >
        Node Information for Network E8A8462A</td></tr><tr >
        <td class='tablecell' align='center'  colspan='1'  rowspan='5' >
        <b><font size='4'>1</font></b></td><td class='tablecell' align='left'  colspan='10' >
        <font color='#000080'><b>Full Name: </b></font><a href="/dev..." target="_blank" >Node 1 Z-Wave UZB1</a>
        </td><td><font color='#000080'><b>Polling: </b></font>Polling Disabled</td>
        </tr>

    """

    value = Scrapers.find_pair_value(html, "Full Name")
    assert value == "Node 1 Z-Wave UZB1"


    html = """
        <tr ><td>
        <font color='#000080'><b>Manufacturer: </b></font><br>
        ManufacturerName</td><td><font color='#000080'><b>Type:</b></font><br>
         0x0</td><td><font color='#000080'><b>ID:</b></font><br>
         0x0</td><td><font color='#000080'><b>Listens:</b></font><br>

        Yes</td><td><font color='#000080'><b>Version: </b></font>abcd1234</td>
        <td><b><font color='#000080'><b>Neighbor Count:</b></font></b><br>
        3</td><td><font color='#000080'><b>Speed:</b></font><br>100Kbps</td></tr>
    """

    assert Scrapers.find_pair_value(html, "Manufacturer") == "ManufacturerName"
    assert Scrapers.find_pair_value(html, "Type") == "0x0"
    assert Scrapers.find_pair_value(html, "ID") == "0x0"
    assert Scrapers.find_pair_value(html, "Listens") == "Yes"
    assert Scrapers.find_pair_value(html, "Version") == "abcd1234"
    assert Scrapers.find_pair_value(html, "Neighbor Count") == "3"
    assert Scrapers.find_pair_value(html, "Speed") == "100Kbps"


    html = """

            <tr ><td class='tablecell' align='left'  colspan='2' >
            <font color='#000080'><b>Uses Interface: </b></font>UZB1 (1)</td>
            <td class='tablecell' align='left'  colspan='12' >
            <font color='#000080'><b>Basic Type: </b></font>ROUTING SLAVE, &nbsp;
            &nbsp;&nbsp;&nbsp;<font color='#000080'><b>Generic Type: </b></font>
            SWITCH BINARY, &nbsp;&nbsp;&nbsp;&nbsp;<font color='#000080'><b>Specific Type: </b>
            </font>NOT USED</td>
            </tr>

    """

    assert Scrapers.find_pair_value(html, "Uses Interface") == "UZB1 (1)"
    assert Scrapers.find_pair_value(html, "Basic Type") == "ROUTING SLAVE"

    html = """

            <tr >
            <td class='tablecell' align='center'  colspan='1'  rowspan='11' ><b><font size='4'>14</font></b></td>
            <td class='tablecell' align='left'  colspan='10' >
            <font color='#000080'><b>Full Name: </b></font>
            <a href="/devi...." target="_blank" >sensorName12345 with space -.|</a></td><td>
            <font color='#000080'><b>Polling: </b></font>Polling Disabled</td>
            </tr>

    """

    assert Scrapers.find_pair_value(html, "Full Name") == "sensorName12345 with space -.|"