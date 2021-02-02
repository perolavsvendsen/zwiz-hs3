"""
Scrape the HS3 Z-wave website and collect nodes and edges.
Initialize a Dash app for visualising the Z-wave network.

"""
import argparse
import dash
import visdcc
import dash_html_components as html
import zwiz

# pylint: disable=C0103    # non-snake variable names

def main():
    """Main program"""

    args = parse_args()
    ip = args.ip
    port = args.port

    # data loading
    # initialize network object and scrape the HS3 website
    network = zwiz.Network(ip=ip, port=port)
    df = network.edges_df.copy()
    df = df[df['type'] == 'neighbor']

    # set temporary visual settings on the nodes
    # separate loop now, plan to do this elsewhere later
    for node_id, node in network.nodes.items():
        if node_id == 1:
            node.marker_size = '10'
            node.marker_shape = 'dot'
        else:
            node.marker_size = '7'
            node.marker_shape = 'dot'

    # create visdcc-friendly nodes and edges
    nodes = []
    for node_id, node in network.nodes.items():
        if node_id not in [n['id'] for n in nodes]:
            nodes.append({'id': node.node_id,
                          'label': node.name[0:10]+'...',
                          'shape': node.marker_shape,
                          'size': node.marker_size})

    edges = []
    for _, edge in network.edges.items():
        if edge.id not in [e['id'] for e in edges]:
            if edge.type == 'route':
                edges.append({'id': edge.id,
                              'from': edge.source.node_id,
                              'to': edge.target.node_id,
                              'width': 2})

    # create app
    app = dash.Dash()

    # define layout
    app.layout = html.Div([
        visdcc.Network(id='net',  # pylint: disable=E1101
                        data={'nodes': nodes, 'edges': edges},
                        options=dict(height='800px',
                                     width='100%',
                                     nodes=dict(color='Grey'))),
        ])


    # main call
    if __name__ == '__main__':
        app.run_server(debug=True)


def parse_args():
    """Parse arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('ip')
    parser.add_argument('port')
    return parser.parse_args()

if __name__ == '__main__':
    main()
