import requests
from bs4 import BeautifulSoup
import pandas as pd
from zwiz._utils import Scrapers

#from zwiz import Scrapers as sc

"""This module contains classes that handles data from HS3"""

class Network:
    """Class for objectifying the Z-wave network overview page served by HS3"""
    def __init__(self, ip, port, page="ZWaveWho"):

        url = f'http://{ip}:{port}/{page}'
        print(f'Grabbing {url}...')
        soup = self._get_page(url)
        print('Scraping...')
        nodes = self._scrape(soup)
        print('Dataframing...')
        self.edges = self._get_edges(nodes)
        
    def _get_page(self, url):
        """Given the url to the """
        response = requests.get(url)
        if not response.ok:
            raise IOError('Could not grab the page from HS3.')
        soup = BeautifulSoup(response.text, "html5lib")
        return soup

    def _scrape(self, soup):
        """Scrape the site, return as list of Node objects"""

        # find the tables containing the z-wave network information
        header_table, nodes_table = Scrapers._get_main_tables(soup)

        # get nodes from the nodes_table
        nodes = Scrapers._get_nodes(nodes_table)

        return nodes

    def _get_edges(self, nodes):
        """
        From the nodes, extract the edges.
        For each node_id in neighbours, make one edge of type neighbor.
        For each node_id in last_working_route, make one edge of type route.
            Source: The node_id
            Target: Other node_id
            Type: The type
            Weight: Just put 1 for now

        """

        weight = 1

        dfs = []

        for node_id in nodes:
            node = nodes[node_id]
            for neighbor in node.neighbors:
                df = pd.DataFrame(
                    {
                        "source": [node.node_id],
                        "target": [neighbor],
                        "type": ["neighbor"],
                        "weight": [weight],
                 })
                dfs.append(df)

            try:
                last_working_route = node.last_working_route
            except AttributeError:
                continue

            for route in node.last_working_route:
                df = pd.DataFrame(
                    {
                        "source": [node.node_id],
                        "target": [route],
                        "type": ["route"],
                        "weight": [weight],
                    })
                dfs.append(df)

        df = pd.concat(dfs).reset_index(drop=True)

        return df


#from dataclasses import dataclass
#@dataclass
class Node:
    def __init__(self, node_id):
        self.node_id = node_id
