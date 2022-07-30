from content_parser import content_parser
from context_graph_edges import AstTraverse
from show_data import show_graph, test_show_edges


def read_content(p):
    fp = open(p, 'rb')
    fc = fp.read().decode('utf-8')
    fp.close()
    return fc


if __name__ == "__main__":
    path = 'data_test/test.cs'
    lang = 'c_sharp'
    # path = 'data_test/main.py'
    # lang = 'python'
    # path = 'data_test/TestProject/Program.cs'
    # path = 'data_test/TestProject/TinyTest.sln'
    output_path = 'output_dataset/test.jsonl.gz'

    # 1. 读取文件内容
    file_content = read_content(path)
    # 2. 使用语法解析器得到语法树
    tree = content_parser(lang, file_content)
    # 3. 遍历AST，添加边Child、NextTokens，记录slot结点
    traverse = AstTraverse(lang, tree.root_node, 0)
    # for debug
    # test_show_edges(traverse.context_graph, 'ReturnsTo')
    # 4. 建立SLOT结点的上下文图，并写入数据集
    traverse.construct_slot_context(path, output_path)
    # 5. 读取并显示数据集的指定条目内容
    index = 1
    dataset = show_graph(output_path, index, "LastLexicalUse", "ReturnsTo", "ForExec", "ForNext",
                         "CondTrue", "CondFalse", "WhileExec", "WhileNext", "NextStmt")
