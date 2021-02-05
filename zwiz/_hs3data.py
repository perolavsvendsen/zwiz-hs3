"""

    This module contains classes that handles data from HS3

    Key concepts:
        Network: This is the z-wave network. It consists of metadata describing
                 the network, a set of nodes and a set of edges. One of the nodes
                 in the network is the central node.
        Node:    A Node is a single z-wave node, physically represented by a device.
        Edge:    An Edge is a relationship between two Nodes. A relationship can be
                 'neighbor' or 'route'.
                 neighbor: This means that the two nodes are neighbors in the z-wave
                           network. Routes can be established between neighbors
                 route:    A route means that the two nodes are communicating with
                           each other.
"""

import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
from zwiz._utils import Scrapers

# pylint: disable=C0103   # Non-snake variable names
# pylint: disable=R0902   # Many instances
# pylint: disable=R0903   # Few public methods

logging.basicConfig(level=logging.INFO)

class Network:
    """
    Class for objectifying the Z-wave network overview page served by HS3

    Methods:
        None
    Attributes:
        nodes (list of zwiz.Nodes): A list of the collected Node objects
        edges (pandas.DataFrame): A dataframe with collected edges

    """

    def __init__(
        self,
        ip: str = None,
        port: int = None,
        html: str = None,
        page: str = "ZWaveWho"
    ):

        """
        Initialization of the Network class.

        If html is given directly, this will be used (testing purposes).
        If html is not given ip/port must be given, and the html will be
        fetched from the HS3 website.

        Arguments:
            ip (str): IP address to the HS3 web administration page
            port (int): Port used by HS3
            page (str): The subpage on the HS3 admin site for the Z-wave network
            html (str): Raw HTML as a string

        """

        # When testing, html is passed as a string to create a controlled environment
        if html is None:
            url = f"http://{ip}:{port}/{page}"
            response = requests.get(url)
            if not response.ok:
                raise IOError("Could not grab the page from HS3.")
            html = response.text

        # Initialize the BeautifulSoup from the html
        soup = BeautifulSoup(html, "html5lib")

        # find the tables containing the z-wave network information
        header_table, nodes_table = Scrapers._get_main_tables(soup)

        # get header info from header_table
        self.header = Scrapers._get_header(header_table)

        # get nodes from the nodes_table
        self.nodes = Scrapers._get_nodes(nodes_table)

        # Set selected attributes from the header
        self.name = self.header["Network Friendly Name"]
        self.home_id = self.header["HomeID"]
        self.number_of_nodes = self.header["Number of Nodes"]
        self.interface_name = self.header["Interface Name"]
        self.interface_model = self.header["Interface Model"]
        self.node_id = self.header["NodeID"]

        # The network itself has a node
        self.node = self.nodes[self.node_id]

        # Get the edges from the nodes
        self.edges = self._get_edges(self.nodes)
        self._edges_df = None

    @property
    def edges_df(self):
        """
        Return the edges a a dataframe.

        Returns:
            edges_df (pandas.DataFrame): Pandas dataframe containing edges.

        """
        if self._edges_df is None:
            dfs = []
            for _, edge in self.edges.items():
                df = pd.DataFrame(
                    {
                        "_id": [edge.id],
                        "source": [edge.source.node_id],
                        "target": [edge.target.node_id],
                        "weight": [edge.weight],
                        "type": [edge.type],
                    }
                )
                dfs.append(df)

            self._edges_df = pd.concat(dfs).set_index("_id", drop=True)

        return self._edges_df

    def _get_edges(self, nodes):
        """
        From the nodes, extract the edges.
        For each node_id in neighbours, make one edge of type neighbor.
        For each node_id in last_working_route, make one edge of type route.
            Source: The node_id
            Target: Other node_id
            Type: The type
            Weight: Just put 1 for now

        Returns:
            edges (dict): Dictionary with edge.id as key

        """
        edges = {}

        for node_id in nodes:
            if node_id == self.node_id:
                # this is the central_node, skipping that
                continue

            node = nodes[node_id]

            # get edges from neighbors
            for neighbor in node.neighbors:
                # sometimes, old nodes can claim neighbors that no longer exists
                if neighbor not in nodes:
                    logging.warning(
                        f"Node {node.node_id} claims " \
                        "non-existing node {neighbor} as neighbor"
                    )
                    continue
                edge = Edge(
                    source=node, target=nodes[neighbor], edgetype="neighbor", weight=1
                )
                edges[edge.id] = edge

            # get edges from last working route
            if not node.last_working_route:
                logging.warning(f"Non-valid route for node {node.node_id}")
                continue

            # sometimes working route can include non-existing nodes
            faulty_route = False
            for n in node.last_working_route:
                if n not in self.nodes:
                    logging.warning(
                        f"Node {node.node_id} includes " \
                        "non-existant node {n} in last working route"
                    )
                    faulty_route = True
            if faulty_route:
                continue

            if node.last_working_route == [self.node.node_id]:
                route = [node, self.node]
            else:
                route = [node] + [nodes[r] for r in node.last_working_route] + [self.node]
            pairs = [(route[r], route[r + 1]) for r in range(len(route) - 1)]

            for source, target in pairs:
                edge = Edge(source=source, target=target, edgetype="route", weight=1)
                edges[edge.id] = edge

        return edges


class Node:
    """
    This is a conveniance class holding the z-wave node object.
    The purpose is to objectify the z-wave node, so that we can
    put methods and attributes on it and easy working with the
    node in various settings.
    """

    def __init__(self, node_id):
        """
        Initialize the Node object.

        Other attributes are set directly to this object from scraper
        functions. They are not pre-defined here. If the Node objects
        becomes more important, pre-setting attributes and handling this
        a bit more structurally migth be a good idea. For now, it does
        its job.

        Arguments:
            node_id (int): The ID of the node corresponding to the ID
                           in the z-wave network.
        """

        self.node_id = node_id


class Edge:
    """
    This is a convencience class holding the z-wave edge (the relationship
    between two nodes). The purpose of objectifying this is to make it easier
    to work with the edges later.

    """

    def __init__(self, source: Node, target: Node, edgetype, weight):
        """Initialize the Edge by passing the source and target node objects"""

        self.source = source
        self.target = target
        self.type = edgetype
        self.weight = weight
        self.id = f"{source.node_id}__{target.node_id}"
