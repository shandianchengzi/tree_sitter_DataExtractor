# coding=utf-8
from dfg import DFG_python, DFG_java, DFG_ruby, DFG_go, DFG_php, DFG_javascript, DFG_csharp
import random
import json
import gzip


def add_edge(context_graph, label, ori, des):
    """
    Usage:
        在上下文图中添加从ori指向des的边，并标记为label
    Args:
        context_graph: 上下文图
        label: 标签名称
        ori: 起始结点
        des: 指向结点
    """
    if (ori is None) or (des is None) or ori < 0 or des < 0:
        return
    context_graph['Edges'][label].append([ori, des])


dfg_func_dict = {
    'python': DFG_python,
    'java': DFG_java,
    'ruby': DFG_ruby,
    'go': DFG_go,
    'php': DFG_php,
    'javascript': DFG_javascript,
    'c_sharp': DFG_csharp
}


class AstTraverse:
    def __init__(self, lang, root_node, cnt):
        """
        Usage:
            初始化一些参数或全局变量，并执行遍历功能
        Args:
            lang: 代码语言
            root_node: tree_sitter解析的对象的根结点
            cnt: 结点数量(为了设置数据集的起始结点号)
        """
        self.lang = lang
        self._root_node = root_node  # 根节点
        self.node_cnt = cnt  # 结点计数器
        self.last_token = -1  # 上一个token结点的序号
        self.context_graph = {  # 初始化上下文图
            'Edges': {
                'Child': [],
                'NextToken': [],
                'ComputedFrom': [],
                'LastLexicalUse': [],
                'ReturnsTo': [],
                'ComesFrom': [],
                'NCS': [],
                # 以下是第二篇论文的CFG边
                'CondTrue': [],
                'CondFalse': [],
                'WhileExec': [],
                'WhileNext': [],
                'ForExec': [],
                'ForNext': [],
                'NextStmt': []
            },
            'nodes': [0] * self.node_cnt,
            'NodeLabels': {},
            'NodeTypes': {}
        }
        self.slot_nodes = []  # 可供替换的变量结点
        self.slot_methods = []  # 变量结点所在的方法or函数
        self.candidates_node = []  # 可供作为候选词的变量结点
        self._text_seen = set()  # 见过的变量结点名称
        self._text_not_allow = set()  # 不是变量的结点名称
        # 执行遍历的函数
        self.ast_traverse()
        self.extract_data_flow()
        self.extract_ncs_flow()

    def extract_data_flow(self):
        """
        Usage:
            用dfg.py添加DFG相关边(包括提取ComesFrom、ComputedFrom边)，并存储到self.context_graph中
        """
        # 1. 前期准备，准备dfg.py的函数需要的输入内容(字典：{(start, end): (index, code)})
        # 获取叶子节点在AST结点列表中的index。
        leaves_ast_index = [self.context_graph['Edges']['NextToken'][0][0]] + \
                           [x[1] for x in self.context_graph['Edges']['NextToken']]
        # 获取叶子节点的(start, end)。
        leaves_start_end = [(self.context_graph['nodes'][x].start_point,
                             self.context_graph['nodes'][x].end_point) for x in leaves_ast_index]
        # 获取叶子节点的内容code。
        leaves_code = [self.context_graph['nodes'][x].text for x in leaves_ast_index]
        start_end_to_code = {}  # 字典：{(start, end): (index, code)}
        for order, (index, start_end, code) in enumerate(zip(leaves_ast_index, leaves_start_end, leaves_code)):
            start_end_to_code[start_end] = (index, code)  # index_to_code = dict((start,end):(叶子节点的index, 代码))

        # 2. 调用dfg.py中的函数，得到返回的四元组
        # dfg: (code, idx, "edgeType", [codes],[idx])
        try:
            dfg, _ = dfg_func_dict[self.lang](self._root_node, start_end_to_code, {})
        except Exception as e:
            dfg = []
        # 根据四元组中的idx排序
        dfg = sorted(dfg, key=lambda x: x[1])

        # 3. 处理返回的dfg四元组
        # 过滤掉添加的异常四元组
        index = set()
        for d in dfg:
            if len(d[-1]) != 0:
                index.add(d[1])
            for x in d[-1]:
                index.add(x)
        new_dfg = []
        for d in dfg:
            if d[1] in index:
                new_dfg.append(d)
        dfg = new_dfg
        # 将dfg四元组转换成边的dict
        dfg_edge_dict = dict()  # 存储了边类型到 边的映射。
        for d in dfg:
            if d[2] not in dfg_edge_dict:
                dfg_edge_dict[d[2]] = list()
            for from_idx in d[4]:
                # 将d[4]中的idx和d[1]组合成边
                dfg_edge_dict[d[2]].append([from_idx, d[1]])

        # 4. 将dfg边转换成上下文图的边
        for edge_name, edge_list in dfg_edge_dict.items():
            for edge in edge_list:
                add_edge(self.context_graph, edge_name, edge[0], edge[1])

    def add_cfg_edges(self, node):
        """
        Usage:
            添加CFG相关的边(包括CondTrue/CondFalse/WhileExec/WhileNext/ForExec/ForNext/NextStmt边)，并存储到self.context_graph中
        Args:
            node: 当前遍历的结点
        """
        condition_node = None
        last_block = None
        # 添加CondTrue和CondFalse边。Condition→block。
        if node.type == 'if_statement':
            first_node = 1
            for any_node in node.children:
                if any_node.type in ['if', 'else', '(', ')', ':']:
                    continue
                add_edge(self.context_graph, 'NextStmt', last_block,
                         self.context_graph['nodes'].index(any_node))
                last_block = self.context_graph['nodes'].index(any_node)
                if not condition_node:
                    condition_node = self.context_graph['nodes'].index(any_node)
                elif first_node:
                    add_edge(self.context_graph, 'CondTrue', condition_node,
                             self.context_graph['nodes'].index(any_node))
                    first_node = 0
                else:
                    add_edge(self.context_graph, 'CondFalse', condition_node,
                             self.context_graph['nodes'].index(any_node))
        # 添加WhileExec和WhileNext边，Condition↔block
        elif node.type == 'while_statement':
            for any_node in node.children:
                if any_node.type in ['while', '(', ')', ':']:
                    continue
                add_edge(self.context_graph, 'NextStmt', last_block,
                         self.context_graph['nodes'].index(any_node))
                last_block = self.context_graph['nodes'].index(any_node)
                if not condition_node:
                    condition_node = self.context_graph['nodes'].index(any_node)
                else:
                    add_edge(self.context_graph, 'WhileExec', condition_node,
                             self.context_graph['nodes'].index(any_node))
                    add_edge(self.context_graph, 'WhileNext',
                             self.context_graph['nodes'].index(any_node), condition_node)
        # 添加ForExec和ForNext边，Condition↔block
        elif node.type == 'for_statement':
            semicolon_nums = 0  # 分号的数量
            after_parentheses = 0  # 是否在括号后面
            has_tail = 0  # 是否已经记录过尾巴
            for any_node in node.children:
                if any_node.type == ';':
                    semicolon_nums = semicolon_nums + 1
                elif semicolon_nums == 2 and any_node.type == ')':
                    after_parentheses = 1
                if any_node.type in ['for', '(', ')', ';', ':']:
                    continue
                add_edge(self.context_graph, 'NextStmt', last_block,
                         self.context_graph['nodes'].index(any_node))
                last_block = self.context_graph['nodes'].index(any_node)
                if (semicolon_nums == 1) and (not condition_node):
                    condition_node = self.context_graph['nodes'].index(any_node)
                elif semicolon_nums == 2:
                    if not has_tail:  # 第二个分号后不管是什么，都是tail
                        add_edge(self.context_graph, 'ForNext',
                                 self.context_graph['nodes'].index(any_node), condition_node)
                        has_tail = 1
                    if after_parentheses:  # 第二个分号的括号后面不管是什么，都是循环体
                        add_edge(self.context_graph, 'ForExec', condition_node,
                                 self.context_graph['nodes'].index(any_node))

    def add_returns_to_edges(self, node):
        """
        Usage:
            添加ReturnsTo边，并存储到self.context_graph中
        Args:
            node: 当前遍历的结点
        """
        if node.type == 'return_statement':
            try:
                ori_node = self.context_graph['nodes'].index(node.children[1])  # return <ori>;
            except IndexError:  # 如果return后面没有结点了，就用自己作为返回结点（用来适应python） # <ori: return>
                ori_node = self.context_graph['nodes'].index(node)
            while node.parent \
                    and node.parent.type != 'method_declaration'\
                    and node.parent.type != 'function_definition':
                node = node.parent
            if node.parent:
                dst_node = self.context_graph['nodes'].index(node.parent.children[-3])  # public <dst> func(args){block}
                add_edge(self.context_graph, 'ReturnsTo', ori_node, dst_node)

    def lrd_traverse(self, node_list, node):
        """
        Usage:
            获取后序遍历顺序的结点列表，并在遍历过程中添加ReturnsTo边、CFG相关的边
        Args:
            node_list: 结点列表，用于存储遍历结果
            node: 当前遍历的结点
        """
        if node.type == "comment":  # 忽略注释结点
            return
        # 再记录孩子结点的信息
        for child in node.children:
            self.lrd_traverse(node_list, child)
        # 记录当前节点
        node_list.append(self.context_graph['nodes'].index(node))
        # 尝试添加ReturnsTo边
        self.add_returns_to_edges(node)
        # 尝试添加CFG相关的边
        self.add_cfg_edges(node)

    def extract_ncs_flow(self):
        """
        Usage:
            先调用lrd_traverse，然后利用lrd_traverse得到的结点列表提取NCS
        """
        # 获取ncs边
        # 获取所有的AST Node，按照先序深度优先遍历，然后连接各个节点
        # 先序遍历AST，添加遍历的边
        node_list = []
        self.lrd_traverse(node_list, self._root_node)

        if len(node_list) <= 1:
            print('结点数量过少，无法添加NCS边')
            return
        for i in range(len(node_list) - 1):
            add_edge(self.context_graph, 'NCS', node_list[i], node_list[i + 1])

    def fill_not_allow_list(self, node):
        """
        Usage:
            测试当前遍历的结点是否是非变量的identifier结点，如果是，则添加到self._text_not_allow中，
            用于过滤非变量的identifier结点。
        Args:
            node: 当前遍历的结点
        """
        sibling_not_allow = ['namespace', 'class', 'new']
        if node.type in sibling_not_allow:
            self._text_not_allow.add(node.next_named_sibling.text)
        elif (node.type == "method_declaration") or (node.type == "function_definition"):
            self._text_not_allow.add(node.children[-3].text)  # -1是函数体，-2是参数列表，-3是函数名
        elif node.type == 'invocation_expression':
            invoked = node.children[0].text.decode('utf-8').split('.')
            for one in invoked:
                self._text_not_allow.add(one)

    def add_slot_and_candidate(self, node):
        """
        Usage:
            提取slot和candidate结点
        Args:
            node: 当前遍历的结点
        """
        # 判断是否是不被允许的名称
        if node.text in self._text_not_allow:
            return
        if node.text in self._text_seen:
            # 见过的结点
            # 只将祖先中有method_declaration或函数声明的结点记为slot
            # 并记录方法/函数声明的祖先节点
            node_pre = node
            while node_pre.parent \
                    and node_pre.parent.type != 'method_declaration'\
                    and node_pre.parent.type != "function_definition":
                node_pre = node_pre.parent
            if node_pre.parent:
                self.slot_nodes.append(node)
                self.slot_methods.append(node_pre.parent)
        else:
            # 没见过的结点
            self._text_seen.add(node.text)
            self.candidates_node.append(node)

    def pre_traverse(self, node):
        """
        Usage:
            前序遍历，并添加Child、NextToken边，并提取slot和candidate
        Args:
            node: 当前遍历的结点
        """
        if node.type == "comment":  # 忽略注释结点
            return
        # 记录当前节点
        self.context_graph['nodes'].append(node)
        self.context_graph['NodeLabels'][str(self.node_cnt)] = node.type
        try:
            add_edge(self.context_graph, 'Child', self.context_graph['nodes'].index(node.parent), self.node_cnt)
        except ValueError:
            pass
        # 过滤非变量的identifier结点
        self.fill_not_allow_list(node)
        # 叶子结点添加NextToken边，并提取slot和candidate
        if node.child_count == 0:
            add_edge(self.context_graph, 'NextToken', self.last_token, self.node_cnt)
            self.last_token = self.node_cnt
            if node.type == 'identifier':
                # 将结点的Label直接设置为标识符
                self.context_graph['NodeLabels'][str(self.node_cnt)] = str(node.text, encoding='utf-8')
                # 提取slot和candidate
                self.add_slot_and_candidate(node)
        self.node_cnt = self.node_cnt + 1
        # 再记录孩子结点的信息
        for child in node.children:
            self.pre_traverse(child)

    def ast_traverse(self):
        """
        Usage:
            根据语法树遍历
        """
        # 前序遍历
        self.pre_traverse(self._root_node)

    #
    def construct_slot_context(self, input_path, output_path):
        """
        Usage:
            构建slot结点的上下文图
        Args:
            input_path: 输入的路径(用于构造数据条目中的filename项)
            output_path: 输出的路径(用于存放输出的数据条目)
        """
        with gzip.open(output_path, 'w') as f:
            pass  # 清空原数据集，以免之前提取的结果影响本次提取测试
        for idx, (slot_node, slot_method) in enumerate(zip(self.slot_nodes, self.slot_methods)):
            # 1. 随机选n个以内的candidate
            n = 8
            if len(self.candidates_node) < n:
                candidate_nodes = self.candidates_node
            else:
                candidate_nodes = random.sample(self.candidates_node, n)  # 随机选取
            # 2. 利用AstTraverse选取slot结点的AST
            traverse = AstTraverse(self.lang, slot_method, len(candidate_nodes) + 1)
            # 3. 将原结点替换成slot结点（index更改为为0）
            slot_index = traverse.context_graph['nodes'].index(slot_node)
            for edge_name, edges in traverse.context_graph['Edges'].items():
                for i in range(len(edges)):
                    if edges[i][0] == slot_index:
                        edges[i][0] = 0
                    if edges[i][1] == slot_index:
                        edges[i][1] = 0
                traverse.context_graph['Edges'][edge_name] = edges
            # 4. 在节点列表、节点标签列表、候选词列表中添加中slot结点和candidate结点
            # 4.1 在节点列表、节点标签列表中添加slot结点
            traverse.context_graph['nodes'][0] = slot_node
            traverse.context_graph['NodeLabels'][0] = "<SLOT>"
            # 在候选词列表中添加slot结点
            symbol_candidates = [{
                "SymbolDummyNode": 1,
                "SymbolName": str(slot_node.text, encoding='utf-8'),
                "IsCorrect": True
            }]
            # 4.2 添加candidate
            for i in range(len(candidate_nodes)):
                # 添加LastLexicalUse边使candidate指向AST中的原结点
                try:
                    add_edge(traverse.context_graph, "LastLexicalUse",
                             i + 1, traverse.context_graph['nodes'].index(candidate_nodes[i]))
                except ValueError:
                    print("new AST hasn't '%s' candidate." % candidate_nodes[i].text)
                # 在节点列表、节点标签列表中添加candidate结点
                traverse.context_graph['nodes'][i + 1] = candidate_nodes[i]
                traverse.context_graph['NodeLabels'][i + 1] = str(candidate_nodes[i].text, encoding='utf-8')
                # 在候选词中添加candidate结点
                symbol_candidates.append({
                    "SymbolDummyNode": i + 2,
                    "SymbolName": str(candidate_nodes[i].text, encoding='utf-8'),
                    "IsCorrect": False
                })
            # 5. 写入数据集
            with gzip.open(output_path, 'a') as f:
                del traverse.context_graph['nodes']
                slot_data = {
                    "filename": input_path,
                    "slotTokenIdx": slot_index,
                    "ContextGraph": traverse.context_graph,
                    "SlotDummyNode": 0,
                    "SymbolCandidates": symbol_candidates
                }
                f.write(bytes(json.dumps(slot_data, ensure_ascii=False) + '\n', 'utf-8'))
                # bytes(input_path + '\n', 'utf-8')
