from pyvis.network import Network
import gzip
import json


# for debug
def test_show_edges(context_graph, *labels):
    # try:
    #     FormalArgNameEdges = node['ContextGraph']['Edges']['FormalArgName']
    # except:
    #     print('no formalArgName')
    nodes = context_graph['nodes']
    child_edges = context_graph['Edges']['Child']
    node_nums = len(nodes)

    nt = Network('1000px', '1000px', directed=True)

    color = ['#00ffff']  # 为第一个结点赋予特殊颜色
    for x in range(node_nums - 1):
        CurrentOfColor = int(x / node_nums * 255 * 2)
        if (CurrentOfColor > 255):
            color.append('#%02x%02x%02x' % (255, CurrentOfColor - 255, CurrentOfColor - 255))
        else:
            color.append('#%02x%02x%02x' % (CurrentOfColor, 0, 0))

    nt.add_nodes(range(node_nums),
                 title=[str(x) + ' ' + str(nodes[x].text) for x in range(node_nums)],
                 label=[nodes[x].type for x in range(node_nums)],
                 color=color
                 )
    nt.add_edges(child_edges)
    for idx, (label) in enumerate(labels):
        try:
            extra_edges = context_graph['Edges'][label]
            for edge in extra_edges:
                nt.add_edge(edge[0], edge[1],
                            value=4,
                            label=label)
        except:
            print('no ' + label + ' edge')

    nt.show('test.html')


def load_graph(path):
    with gzip.open(path, 'r') as f:
        content = f.read().decode('utf-8')
        context_graph = []
        items = content.split('\n')
        for item in items:
            try:
                context_graph.append(json.loads(item))
            except:
                print(item)
        return context_graph


def show_graph(path, index, *labels):
    graph = load_graph(path)
    one_data = graph[index]
    child_edges = one_data['ContextGraph']['Edges']['Child']
    node_nums = len(one_data['ContextGraph']['NodeLabels'])

    nt = Network('1000px', '1000px', directed=True)
    color = ['#00ffff']  # 为第一个结点赋予特殊颜色
    for x in range(node_nums - 1):
        current_of_color = int(x / node_nums * 255 * 2)
        if current_of_color > 255:
            color.append('#%02x%02x%02x' % (255, current_of_color - 255, current_of_color - 255))
        else:
            color.append('#%02x%02x%02x' % (current_of_color, 0, 0))

    nt.add_nodes(range(node_nums),
                 title=[str(x) for x in range(node_nums)],
                 label=[one_data['ContextGraph']['NodeLabels'][str(x)] for x in range(node_nums)],
                 color=color
                 )
    nt.add_edges(child_edges)
    for idx, (label) in enumerate(labels):
        try:
            to_show_edges = one_data['ContextGraph']['Edges'][label]
            for edge in to_show_edges:
                nt.add_edge(edge[0], edge[1],
                            value=4,
                            label=label)
        except:
            print('no ' + label + ' edges')
            return

    nt.show(path.split('/')[-1].split('.')[0] + str(index) + '.html')
