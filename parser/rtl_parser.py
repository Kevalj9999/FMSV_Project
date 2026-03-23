from pyverilog.vparser.parser import parse
import hashlib
import os
import re
import tempfile
import pickle


class RTLParser:
    """Incremental RTL parser with preprocessing + caching for scalability"""

    def __init__(self, cache_dir=".rtl_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    # -------- PREPROCESSING --------
    def preprocess_rtl(self, text):
        # Remove trailing commas in parameter lists
        text = re.sub(r",\s*\)", ")", text)

        # Remove generate/endgenerate (basic handling)
        text = text.replace("generate", "")
        text = text.replace("endgenerate", "")

        # Remove attributes (* ... *)
        text = re.sub(r"\(\*.*?\*\)", "", text)

        return text

    # -------- CACHE HELPERS --------
    def get_file_hash(self, filepath):
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def get_cache_key(self, filepath):
        filename = os.path.basename(filepath)
        file_hash = self.get_file_hash(filepath)
        return os.path.join(self.cache_dir, f"{filename}_{file_hash}.cache")

    # -------- CORE PARSER --------
    def parse_single_file(self, filepath):
        """
        Parse a single RTL file with preprocessing + caching.
        Returns: (ast, metadata)
        """
        cache_file = self.get_cache_key(filepath)

        # Load from cache if exists
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        try:
            # -------- READ + PREPROCESS --------
            with open(filepath, "r") as f:
                raw_code = f.read()

            clean_code = self.preprocess_rtl(raw_code)

            # -------- WRITE TEMP FILE --------
            with tempfile.NamedTemporaryFile(delete=False, suffix=".v") as tmp:
                tmp.write(clean_code.encode())
                tmp_path = tmp.name

            # -------- PARSE CLEAN FILE --------
            ast, directives = parse(
                [tmp_path],
                preprocess_include=['rtl'],
                preprocess_define=[]
            )

            # -------- CACHE RESULT --------
            with open(cache_file, 'wb') as f:
                pickle.dump((ast, directives), f)

            return ast, directives

        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
            return None, None

    # -------- INCREMENTAL PARSING --------
    def parse_rtl_incremental(self, file_list):
        """
        Parse RTL files incrementally and return combined AST.
        """
        asts = []

        for filepath in file_list:
            print(f"  Parsing {os.path.basename(filepath)}...")
            ast, _ = self.parse_single_file(filepath)
            if ast:
                asts.append(ast)

        if not asts:
            raise ValueError("No valid RTL files to parse")

        # If only one AST
        if len(asts) == 1:
            return asts[0]

        # -------- MERGE ASTs --------
        combined = asts[0]

        for ast in asts[1:]:
            if not hasattr(ast, 'description') or not hasattr(combined, 'description'):
                continue

            for definition in ast.description.definitions:
                if isinstance(combined.description.definitions, tuple):
                    combined.description.definitions = list(combined.description.definitions)

                combined.description.definitions.append(definition)

        return combined


# -------- PUBLIC FUNCTION --------
def parse_rtl(file_list, incremental=True):
    """
    Parses RTL files into AST
    """
    if incremental:
        parser = RTLParser()
        return parser.parse_rtl_incremental(file_list)
    else:
        ast, _ = parse(
            file_list,
            preprocess_include=['rtl'],
            preprocess_define=[]
        )
        return ast