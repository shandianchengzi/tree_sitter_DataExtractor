from tree_sitter import Language, Parser


# ToDo
def remove_comment(tree):
    pass


def content_parser(lang, file_content):
    language = Language('./tree_sitters/my-languages.so', lang)
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(file_content, 'utf-8'))
    remove_comment(tree)  # 移除注释
    return tree
