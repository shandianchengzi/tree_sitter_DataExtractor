from tree_sitter import Language, Parser


# ToDo
def remove_comment(tree):
    """
    Usage:
        (Not Complete)
        把AST中的comment(注释结点)删掉
    Args:
        tree: 需要处理的AST
    """
    pass


def content_parser(lang, file_content):
    """
    Usage：
        调用tree_sitter解析代码文本，并返回AST
    Args:
        lang: 代码文本的编程语言
        file_content: 代码文本内容
    Returns:
        tree_sitter解析的AST
    """
    language = Language('./tree_sitters/my-languages.so', lang)
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(file_content, 'utf-8'))
    remove_comment(tree)  # 移除注释
    return tree
