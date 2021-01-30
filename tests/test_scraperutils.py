import pytest
from zwiz._utils import ScraperUtils

def test_find_pair():

    html = """

        <tr >
        <td class='tableheader'  colspan='15' >
        Node Information for Network E8A8462A</td>
        </tr>
        <tr >
        <td class='tablecell' align='center'  colspan='1'  rowspan='5' ><b><font size='4'>1</font></b></td>
        <td class='tablecell' align='left'  colspan='10' >
        <font color='#000080'><b>Full Name: </b></font><a href="/deviceutility?ref=116&edit=1" target="_blank" >Node 1 Z-Wave UZB1</a>
        </td>
        <td class='tablecell' align='left'  colspan='4' >
        <font color='#000080'><b>Polling: </b></font>Polling Disabled</td>
        </tr>
    """

    value = ScraperUtils.find_pair_value(html, "Full Name")
    assert value == "Node 1 Z-Wave UZB1"


    html = """

        <tr >
        <td class='tablecell' align='left'  colspan='2' >
        <font color='#000080'><b>Manufacturer: </b></font><br>
        PowerLynx</td>
        <td class='tablecell' align='left'  colspan='1' >
        <font color='#000080'><b>Type:</b></font>
        <br>
         0x0</td>
        <td class='tablecell' align='left'  colspan='1' >
        <font color='#000080'><b>ID:</b></font>
        <br>
         0x0</td>
        <td class='tablecell' align='left'  colspan='1' >
        <font color='#000080'><b>Listens:</b></font><br>

        Yes</td>
        <td class='tablecell' align='left'  colspan='3' >
        <font color='#000080'><b>Version: </b></font>4.05 (ZDK 6.51.6)</td>
        <td class='tablecell' align='left'  colspan='5'  style=' white-space: nowrap;' >
        <b><font color='#000080'><b>Neighbor Count:</b></font></b><br>
        3</td>
        <td class='tablecell'  colspan='1' >
        <font color='#000080'><b>Speed:</b></font><br>
        100Kbps</td>
        </tr>
    """

    assert ScraperUtils.find_pair_value(html, "Manufacturer") == "PowerLynx"
    assert ScraperUtils.find_pair_value(html, "Type") == "0x0"
    assert ScraperUtils.find_pair_value(html, "ID") == "0x0"
    assert ScraperUtils.find_pair_value(html, "Listens") == "Yes"
    assert ScraperUtils.find_pair_value(html, "Version") == "4.05 (ZDK 6.51.6)"
    assert ScraperUtils.find_pair_value(html, "Neighbor Count") == "3"
    assert ScraperUtils.find_pair_value(html, "Speed") == "100Kbps"


    html = """

            <tr ><td class='tablecell' align='left'  colspan='2' >
            <font color='#000080'><b>Uses Interface: </b></font>UZB1 (1)</td>
            <td class='tablecell' align='left'  colspan='12' >
            <font color='#000080'><b>Basic Type: </b></font>ROUTING SLAVE, &nbsp;&nbsp;&nbsp;&nbsp;<font color='#000080'><b>Generic Type: </b></font>SWITCH BINARY, &nbsp;&nbsp;&nbsp;&nbsp;<font color='#000080'><b>Specific Type: </b></font>NOT USED</td>
            </tr>

    """

    assert ScraperUtils.find_pair_value(html, "Uses Interface") == "UZB1 (1)"
    assert ScraperUtils.find_pair_value(html, "Basic Type") == "ROUTING SLAVE"