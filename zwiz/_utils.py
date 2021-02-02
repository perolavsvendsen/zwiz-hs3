"""This module contains utility classes related to scraping HS3 website"""

import re

class Scrapers:
    """This is a utility class containing functions that scrape HTML"""

    # pylint: disable=C0103   # allow short non-snake variables

    @staticmethod
    def _get_main_tables(soup):
        """
        Identify the header_table and the node_table from the scraped
        HTML. Identify the header table by looking for "Current Z-Wave Networks"
        and the nodes table by looking for "Node Information".

        Arguments:
            soup (bs4.BeautifulSoup): Parsed HTML as a bs4 object.
        Returns:
            header_table, nodes_table (tuple of str): HTML a string for the
            identified tables.

        """
        tables = soup.find_all('table')

        header_table = None
        nodes_table = None

        for table in tables:
            first_td = str(table.find_all('td')[0])
            if "Current Z-Wave Networks" in first_td:
                header_table = table
            if "Node Information" in first_td:
                nodes_table = table

        if not header_table:
            raise ValueError('Header table not found on HS3 page')
        if not nodes_table:
            raise ValueError('Nodes table not found on HS3 page')

        return header_table, nodes_table

    @staticmethod
    def _get_header(header_table):
        """
            Scrape the header table, and return the header attributes.

            Arguments:
                header_table (str): The HTML containing the header table.

            Returns:
                header (dict): Dictionary containing the header attributes.

        """

        tds = header_table.find_all('tr')[2].find_all('td')
        header = {
            'Network Friendly Name': tds[0].contents[0].strip(),
            'HomeID': tds[1].contents[0].strip(),
            'Number of Nodes': int(tds[2].contents[0].strip()),
            'Interface Name': tds[3].contents[0].strip(),
            'Interface Model': tds[4].contents[0].strip(),
            'Node ID': int(tds[5].contents[0].strip()),
        }

        return header


    @staticmethod
    def _get_nodes(nodes_table):
        """
            Scrape the nodes table, and return the individual nodes.
            Identify key trs in the table by looking for identifying strings.
            Implicitly, this means that this will fail if key strings occur multiple times.

            Arguments:
                nodes_table (str): The piece of HMTL containing the nodes table

            Returns:
                nodes (dict of node_id:Node): Dictionary with node_id as key, Node object as value
                    representing the nodes found in the Z-wave network.

        """

        from zwiz._hs3data import Node   # pylint: disable=C0415  # Import outside top-level

        node_trs = nodes_table.find_all('tr')

        nodes = {}

        for tr in node_trs:

            # Identify the first tr by looking for "Full Name".
            # Get the node_id and other info.
            # Keep node_id until next time.
            if "<b>Full Name" in str(tr):
                # this is first tr in a node. This is where the NodeID should be
                # so using this to initialize a new Node.
                node_id = Scrapers.find_node_id(str(tr))
                nodes[node_id] = Node(node_id=node_id)
                nodes[node_id].name = Scrapers.find_pair_value(tr, "Full Name")

            # Find the second TR in a node, which contains various key:value pairs
            # Technically not necessary for the specific use case (edges), but
            # in the nice-to-have bucket... This approach can be used for other
            # contents of the node later as well.
            if "<b>Manufacturer" in str(tr):
                nodes[node_id].manufacturer = Scrapers.find_pair_value(tr, "Manufacturer")
                nodes[node_id].type = Scrapers.find_pair_value(tr, "Type")
                nodes[node_id].listens = Scrapers.find_pair_value(tr, "Listens")
                nodes[node_id].version = Scrapers.find_pair_value(tr, "Version")
                nodes[node_id].firmware = Scrapers.find_pair_value(tr, "Firmware")
                nodes[node_id].speed = Scrapers.find_pair_value(tr, "Speed")


            # Find the tr in the html containing neighbors
            if "<b>Neighbors" in str(tr):
                neighbors = Scrapers.find_pair_value(tr, "Neighbors")
                if neighbors is None:
                    neighbors = []
                else:
                    neighbors = [int(n.strip()) for n in neighbors.split()]

                nodes[node_id].neighbors = neighbors

            # Find the tr in the node html containing the last working route
            if "<b>Last Working Route" in str(tr):
                last_working_route = Scrapers.get_last_working_route(str(tr))
                nodes[node_id].last_working_route = last_working_route

        return nodes


    @staticmethod
    def get_last_working_route(tr):
        """
            Parse the Last Working Route from the tr.
            This assumes that the tr has been pre-identified.

            The Last Working Route is the list of node_id's representing
            the route last used by the device to reach the central node.
            It is formatted like this: <node_id> -> <node_id>, where the
            ">" is represented as "&gt;".

        """

        # first find the correct pair from the html
        last_working_route = Scrapers.find_pair_value(tr, "Last Working Route")

        if last_working_route.startswith('None'):
            # This means that there was no last working route
            # Retuning empty list
            return []

        if last_working_route.startswith('Direct'):
            # This means that the last working route was directly to the central_node
            return [1]

        last_working_route = last_working_route.split()[0]

        sep = '-&gt;'
        if sep in last_working_route:
            # The route has more than one node, so split it and return the list
            return [int(l) for l in last_working_route.split(sep)]

        # the route has only one node, so return a list containing that only
        return [int(last_working_route)]


    @staticmethod
    def find_node_id(html):
        """
            Extract the node_id from the html. It will be the only integer between
            two html tags, so it can be identified by regexing for that.

            Arguments:
                html (str): The html containing the node_id
            Returns:
                node_id (int): The node_id

        """
        node_id = int(re.findall(r'>\d+<', html)[0].replace('<','').replace('>', ''))
        return node_id

    @staticmethod
    def find_pair_value(html, key):   # pylint: disable=R1710  # inconsistent return statements

        """
        Search the html, find the contents, assume that the resulting
        matches are key/values from pairs. Search for the key, then
        return the next - which then will be the value.

        Arguments:
            html (str): The HTML string
            key (str): The key to search for

        Returns:
            value (str): The value corresponding to the given key
        """

        # clean the html
        html = str(html).replace('\n', '')

        # regex to find all text content
        # The challenge is to find only text, not any html-tags
        # Supposedly, BeautifulSoup can do this, but I could not figure out how...
        matches = re.findall(r">.[^<>]+<", str(html))

        # Remove known noise
        removings = ['>', '<', ':', '&nbsp;', ',']
        for r in removings:
            matches = [m.replace(r, '') for m in matches]
        matches = [m.strip() for m in matches]
        matches = [m for m in matches if m]

        # This feels like something for iter and next(), but...
        for m, match in enumerate(matches):
            if match == key:
                try:
                    return matches[m+1]
                except IndexError:
                    return None
