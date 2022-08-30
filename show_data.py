from pyvis.network import Network
import gzip
import json


def test_show_edges(context_graph, *labels):
    """
    Usage:
        for debug。
        用于显示上下文图的AST边和某些边。
    Args:
        context_graph: 需要显示的上下文图
        *labels: 需要显示的额外边的名称
    """
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
    """
    Usage:
        根据数据集文件路径读取数据集文件内容
    Args:
        path: 数据集的路径
    Returns:
        数据集内容
    """
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
    """
    Usage:
        将数据集的某条数据可视化
    Args:
        path: 数据集路径
        index: 数据集条目索引
        *labels: 需要显示的额外边的名称
    Returns:
        根目录下生成一个html文件，文件名构成：输入代码文件名+index+.html。
    """
    # 1. 载入数据
    graph = load_graph(path)
    one_data = graph[index]
    child_edges = one_data['ContextGraph']['Edges']['Child']
    node_nums = len(one_data['ContextGraph']['NodeLabels'])
    # 2. 为结点按顺序选取不同的颜色（从深色冷色调到浅色暖色调，并为首个结点赋予特殊颜色，这种方法在结点超过255*2后相邻结点颜色可能重复）
    color = ['#00ffff']  # 为第一个结点赋予特殊颜色
    for x in range(node_nums - 1):
        current_of_color = int(x / node_nums * 255 * 2)
        if current_of_color > 255:
            color.append('#%02x%02x%02x' % (255, current_of_color - 255, current_of_color - 255))
        else:
            color.append('#%02x%02x%02x' % (current_of_color, 0, 0))
    # 3. 初始化画布，并添加结点和Child边
    nt = Network('1000px', '1000px', directed=True)
    nt.add_nodes(range(node_nums),
                 title=[str(x) for x in range(node_nums)],
                 label=[one_data['ContextGraph']['NodeLabels'][str(x)] for x in range(node_nums)],
                 color=color
                 )
    nt.add_edges(child_edges)
    # 4. 依次添加其他需要额外显示的边
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
    # 5. 显示图
    nt.show(path.split('/')[-1].split('.')[0] + str(index) + '.html')
