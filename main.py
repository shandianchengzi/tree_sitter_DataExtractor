from content_parser import content_parser
from context_graph_edges import AstTraverse
from show_data import show_graph, test_show_edges


def read_content(p):
    fp = open(p, 'rb')
    fc = fp.read().decode('utf-8')
    fp.close()
    return fc


if __name__ == "__main__":
    path = 'data_test/test.cs'  # 输入路径
    lang = 'c_sharp'  # 输入文件的语言
    # path = 'data_test/main.py'
    # lang = 'python'
    # path = 'data_test/TestProject/Program.cs'
    # path = 'data_test/TestProject/TinyTest.sln'
    output_path = 'output_dataset/test.jsonl.gz'  # 输出路径
    index = 1  # 显示第<index>条数据集
    edges_shown = ["LastLexicalUse", "ReturnsTo", "ForExec", "ForNext", "CondTrue",
                   "CondFalse", "WhileExec", "WhileNext", "NextStmt"]  # 图上会显示的边

    # 1. 读取文件内容
    file_content = read_content(path)
    # 2. 使用语法解析器得到语法树
    tree = content_parser(lang, file_content)
    # 3. 遍历AST，添加各种边，记录slot和candidate结点
    traverse = AstTraverse(lang, tree.root_node, 0)
    # for debug
    # test_show_edges(traverse.context_graph, 'ReturnsTo')
    # 4. 建立SLOT结点的上下文图，并写入数据集
    traverse.construct_slot_context(path, output_path)
    # 5. 读取并显示数据集的指定条目内容
    dataset = show_graph(output_path, index, *edges_shown)
