from tree_sitter import Language, Parser


# ToDo
def remove_comment(tree):
    pass


# input: lang:代码文本的编程语言; file_content:代码文本内容
# output: tree_sitter解析的AST
# 调用tree_sitter解析代码文本，并返回AST
def content_parser(lang, file_content):
    language = Language('./tree_sitters/my-languages.so', lang)
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(file_content, 'utf-8'))
    remove_comment(tree)  # 移除注释
    return tree
