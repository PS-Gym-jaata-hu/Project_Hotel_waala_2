import ast
import os
from collections import defaultdict

class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.current_func = None
        self.func_calls = defaultdict(set)  # function_name -> set of called functions
        self.func_defs = set()              # all function definitions in this file

    def visit_FunctionDef(self, node):
        func_name = node.name
        if hasattr(node, "parent_class"):
            func_name = f"{node.parent_class}.{func_name}"
        self.func_defs.add(func_name)
        self.current_func = func_name
        for stmt in node.body:
            self.visit(stmt)
        self.current_func = None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            called_func = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # handle self.method() or Class.method()
            value = node.func.value
            if isinstance(value, ast.Name):
                called_func = f"{value.id}.{node.func.attr}"
            elif isinstance(value, ast.Attribute):
                called_func = f"{value.attr}.{node.func.attr}"
            else:
                called_func = node.func.attr
        else:
            called_func = None

        if called_func and self.current_func:
            self.func_calls[self.current_func].add(called_func)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for f in node.body:
            if isinstance(f, ast.FunctionDef):
                f.parent_class = node.name
        self.generic_visit(node)

def analyze_file(filepath):
    with open(filepath, "r") as f:
        tree = ast.parse(f.read(), filename=filepath)

    analyzer = FunctionAnalyzer(filepath)
    analyzer.visit(tree)
    return analyzer.func_defs, analyzer.func_calls

def analyze_project(root_dir):
    all_funcs = set()
    all_calls = defaultdict(set)

    # Collect all functions and calls
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                full_path = os.path.join(dirpath, fname)
                funcs, calls = analyze_file(full_path)
                all_funcs.update(funcs)
                for k, v in calls.items():
                    all_calls[k].update(v)

    # Calculate fan-in and fan-out
    fan_out = {f: len(all_calls.get(f, set())) for f in all_funcs}
    fan_in = {f: 0 for f in all_funcs}

    for caller, callees in all_calls.items():
        for callee in callees:
            if callee in fan_in:
                fan_in[callee] += 1

    avg_fan_in = sum(fan_in.values()) / len(fan_in) if fan_in else 0
    avg_fan_out = sum(fan_out.values()) / len(fan_out) if fan_out else 0
    info_flow = {f: (fan_in[f] * fan_out[f])**2 for f in all_funcs}

    # Print summary
    print("\n===== PROJECT-WIDE INFORMATION METRICS =====")
    print("Function               | Fan-in | Fan-out | Info-flow")
    print("------------------------------------------------------")
    for f in sorted(all_funcs):
        print(f"{f:<22} | {fan_in[f]:<6} | {fan_out[f]:<7} | {info_flow[f]}")

    print("\nTotal Functions:", len(all_funcs))
    print(f"Average Fan-in: {avg_fan_in:.2f}")
    print(f"Average Fan-out: {avg_fan_out:.2f}")

if __name__ == "__main__":
    import sys
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "./HotinGo"
    analyze_project(project_dir)
