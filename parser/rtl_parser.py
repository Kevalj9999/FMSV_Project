from pyverilog.vparser.parser import parse
import json
import hashlib
import os


class RTLParser:
    """Incremental RTL parser with caching for scalability"""
    
    def __init__(self, cache_dir=".rtl_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get_file_hash(self, filepath):
        """Get hash of file content for cache validation"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def get_cache_key(self, filepath):
        """Generate cache filename for a RTL file"""
        filename = os.path.basename(filepath)
        file_hash = self.get_file_hash(filepath)
        return os.path.join(self.cache_dir, f"{filename}_{file_hash}.cache")
    
    def parse_single_file(self, filepath):
        """
        Parse a single RTL file with caching.
        Returns: (ast, metadata)
        """
        cache_file = self.get_cache_key(filepath)
        
        # Check if cached
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                import pickle
                return pickle.load(f)
        
        # Parse file
        try:
            ast, directives = parse(
                [filepath],
                preprocess_include=['rtl'],
                preprocess_define=[]
            )
            
            # Cache result
            import pickle
            with open(cache_file, 'wb') as f:
                pickle.dump((ast, directives), f)
            
            return ast, directives
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
            return None, None
    
    def parse_rtl_incremental(self, file_list):
        """
        Parse RTL files incrementally and return combined AST.
        More memory efficient than parsing all at once.
        """
        asts = []
        
        for filepath in file_list:
            print(f"  Parsing {os.path.basename(filepath)}...")
            ast, _ = self.parse_single_file(filepath)
            if ast:
                asts.append(ast)
        
        if not asts:
            raise ValueError("No valid RTL files to parse")
        
        # Combine ASTs
        if len(asts) == 1:
            return asts[0]
        
        # Merge multiple ASTs into first one
        combined = asts[0]

        for ast in asts[1:]:
            if not hasattr(ast, 'description') or not hasattr(combined, 'description'):
                continue

            for definition in ast.description.definitions:
                # Ensure it's a list before appending
                if isinstance(combined.description.definitions, tuple):
                    combined.description.definitions = list(combined.description.definitions)

                combined.description.definitions.append(definition)

        return combined


def parse_rtl(file_list, incremental=True):
    """
    Parses RTL files into AST
    
    Args:
        file_list: List of RTL file paths
        incremental: If True, parse files incrementally (more scalable)
    
    Returns:
        ast: Combined AST
    """
    if incremental:
        parser = RTLParser()
        return parser.parse_rtl_incremental(file_list)
    else:
        # Legacy: parse all at once (not recommended for large designs)
        ast, _ = parse(
            file_list,
            preprocess_include=['rtl'],
            preprocess_define=[]
        )
        return ast