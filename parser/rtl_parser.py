from pyverilog.vparser.parser import parse


def parse_rtl(file_list):
    """
    Parses RTL files into AST
    """
    ast, _ = parse(
        file_list,
        preprocess_include=['rtl'],  # 👈 IMPORTANT
        preprocess_define=[]
    )
    return ast