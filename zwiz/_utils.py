import re



"""This module contains utility classes"""

class Scrapers:
    """This is a utility class containing functions related to scraping"""

    @staticmethod
    def _get_main_tables(soup):
        """Find the table containing the Z-wave network information"""
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
    def _get_nodes(nodes_table):

        from zwiz._hs3data import Node

        def find_pairs(tr):
            pairs = {}
            for td in tr.find_all('td'):
                matches = re.sub("<[^>]*>", "", str(td)).strip().split(':')
                if len(matches) == 2:
                    pairs[matches[0]] = matches[1].strip()
            return pairs

        node_trs = nodes_table.find_all('tr')

        nodes = {}

        for tr in node_trs:

            # when Full Name present, this is first TR, so get the node_id and other info. Keep node_id until next time
            if "<b>Full Name" in str(tr):
                # this is first tr in a node. This is where the NodeID should be
                # so using this to initialize a new Node.

                node_id = ScraperUtils.find_node_id(str(tr))
                nodes[node_id] = Node(node_id=node_id)
                nodes[node_id].name = ScraperUtils.find_pair_value(tr, "Full Name")
                nodes[node_id].polling = ScraperUtils.find_pair_value(tr, "Polling")

            if "<b>Manufacturer" in str(tr):
                # this is the second tr in a node
                nodes[node_id].manufacturer = ScraperUtils.find_pair_value(tr, "Manufacturer")
                nodes[node_id].type = ScraperUtils.find_pair_value(tr, "Type")
                nodes[node_id].listens = ScraperUtils.find_pair_value(tr, "Listens")
                nodes[node_id].version = ScraperUtils.find_pair_value(tr, "Version")
                nodes[node_id].firmware = ScraperUtils.find_pair_value(tr, "Firmware")
                nodes[node_id].speed = ScraperUtils.find_pair_value(tr, "Speed")

            if "<b>Neighbors" in str(tr):
                # this is the third tr in a node
                neighbors = ScraperUtils.find_pair_value(tr, "Neighbors")
                if neighbors is None:
                    neighbors = []
                else:
                    neighbors = [int(n.strip()) for n in neighbors.split()]

                nodes[node_id].neighbors = neighbors

            if "<b>Last Working Route" in str(tr):
                # this is the fourth tr in a node
                last_working_route = ScraperUtils.get_last_working_route(str(tr))
                nodes[node_id].last_working_route = last_working_route

            if "<b>Uses Interface" in str(tr):
                nodes[node_id].uses_interface = ScraperUtils.find_pair_value(tr, "Uses Interface")
                nodes[node_id].basic_type = ScraperUtils.find_pair_value(tr, "Basic Type")
            
            if "<b>Command Classes" in str(tr):
                # this is the sixt tr in a node
                tds = iter(tr.find_all('td')[0].find_all('table')[0].find_all('td'))
                for td in tds:
                    if 'Supported:' in str(td):
                        supported_td = next(tds)
                    if 'Controlled:' in str(td):
                        controlled_td = next(tds)

                nodes[node_id].command_classes = {}
                nodes[node_id].command_classes['Supported'] = [x.strip() for x in supported_td.contents]
                nodes[node_id].command_classes['Controlled'] = [x.strip() for x in controlled_td.contents]
                
            if '<b>Child Device:' in str(tr):
                # this is one of the child device classes
                # later.....
                pass

        return nodes


class ScraperUtils:

    @staticmethod
    def get_last_working_route(tr):
        last_working_route = ScraperUtils.find_pair_value(tr, "Last Working Route")
        if last_working_route.startswith('None'):
            return []
        if last_working_route.startswith('Direct'):
            return [1]
        sep = '-&gt;'            
        last_working_route = last_working_route.split()[0]
        if sep in last_working_route:
            return [int(l) for l in last_working_route.split(sep)]
        return [int(last_working_route)]


    @staticmethod
    def find_node_id(txt):
        if not isinstance(txt, str):
            raise ValueError('Must be string')
        node_id = int(re.findall(r'>\d+<', txt)[0].replace('<','').replace('>', ''))
        return node_id

    @staticmethod
    def find_pair_value(html, key):
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
        html = str(html).replace('\n', '')
        matches = re.findall(r">[a-zA-Z0-9:.,_;!%&=? \-\+()]+<", str(html))
        removings = ['>', '<', ':', '&nbsp;', ',']
        for r in removings:
            matches = [m.replace(r, '') for m in matches]
        matches = [m.strip() for m in matches]
        matches = [m for m in matches if m]
        matches = [m.replace('>', '').replace('<', '').replace(':', '').strip() for m in matches]

        for m, match in enumerate(matches):
            if match == key:
                try:
                    return matches[m+1]
                except IndexError:
                    return None
                raise