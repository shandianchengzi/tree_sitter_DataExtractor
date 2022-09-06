from content_parser import content_parser
from context_graph_edges import AstTraverse
from show_data import show_graph, test_show_edges


def read_content(p):
    """
    Usage:
        根据文件路径读取文件内容
    Args:
        p: 输入的代码文本路径
    Returns:
        输入的代码文本内容
    """
    fp = open(p, 'rb')
    fc = fp.read().decode('utf-8')
    fp.close()
    return fc


if __name__ == "__main__":
    """
    Usage：
        项目入口。输入代码文本，输出数据集，并可视化显示数据集中的某一条数据。
    Params：
        输入：
            path: 输入的代码文本的路径。(测试代码在data_test目录下，可任意选取其中的文件。)
            lang: 输入的代码文本对应的语言。(目前只支持c_sharp、python，其他的尚未测试，需要做适配。)
            示例：
            path = 'data_test/test.cs'
            path = 'data_test/TestProject/Program.cs'
            path = 'data_test/main.py'
        输出：
            output_path: 输出的数据集的路径。(默认为output_dataset目录下，文件名为test.jsonl.gz)
        可视化：
            index: 输出的数据集的第<index>条会被可视化显示。(不得超过数据集条数)
            edges_shown: 可视化结果中会显示的边。(如果为空，则结果中也会显示AST边。)
    """
    path = 'data_test/o.cs'  # 输入路径
    lang = 'c_sharp'  # 输入文件的语言

    output_path = 'output_dataset/test.jsonl.gz'  # 输出路径

    index = 1  # 显示第<index>条数据集
    edges_shown = ["ComputedFrom", "LastLexicalUse"]# "ReturnsTo", "ForExec", "ForNext", "CondTrue",
                   #"CondFalse", "WhileExec", "WhileNext", "NextStmt", "ComesFrom"]  # 图上会显示的边

    # 1. 读取文件内容
    file_content = read_content(path)
    # 2. 使用语法解析器得到语法树
    tree = content_parser(lang, file_content)
    # 3. 遍历AST，添加各种边，记录slot和candidate结点
    # for debug: 可以通过test_show_edges(traverse.context_graph, 'ReturnsTo')显示尚未选取SLOT结点时的上下文图的边
    traverse = AstTraverse(lang, tree.root_node, 0)
    # 4. 建立SLOT结点的上下文图，并写入数据集
    traverse.construct_slot_context(path, output_path)
    # 5. 读取并显示数据集的指定条目内容
    dataset = show_graph(output_path, index, *edges_shown)
