#python3 lva.py , to run this live variable analysis, uses AST
#You can tell your teacher:
# Langage: Python
# Module used: ast (Abstract Syntax Tree)
# Algorithm: Backward data-flow analysis using GEN/KILL sets
# Purpose: Calculate LIVE_IN and LIVE_OUT for variables per file
# 💡 Tip for Presentation:
# You can explain it like this:
# "I wrote a Python script that reads all project files, analyzes every variable’s usage, and uses 
# backward propagation to compute which variables are needed before and after each line. This gives 
# me total live variables per file, which helps understand variable usage in the project."

import ast
import os
from collections import defaultdict

class LiveVariableAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.func_vars = {}

    def visit_FunctionDef(self, node):
        gen_kill = {}
        for stmt in node.body:
            gen_kill.update(self.process_stmt(stmt))
        self.func_vars[node.name] = gen_kill
        self.generic_visit(node)

    def process_stmt(self, stmt):
        gen_kill = {}
        used, assigned = self.collect_vars(stmt)
        gen_kill[stmt.lineno] = {"gen": used, "kill": assigned}
        if hasattr(stmt, 'body'):
            for s in stmt.body:
                gen_kill.update(self.process_stmt(s))
        if hasattr(stmt, 'orelse'):
            for s in stmt.orelse:
                gen_kill.update(self.process_stmt(s))
        return gen_kill

    def collect_vars(self, stmt):
        used = set()
        assigned = set()

        class VarVisitor(ast.NodeVisitor):
            def visit_Name(self, n):
                if isinstance(n.ctx, ast.Load):
                    used.add(n.id)
                elif isinstance(n.ctx, ast.Store):
                    assigned.add(n.id)

        VarVisitor().visit(stmt)
        return used, assigned

def live_variable_analysis_file(file_path):
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)

    analyzer = LiveVariableAnalyzer()
    analyzer.visit(tree)

    total_live_in = 0
    total_live_out = 0

    for func, lines in analyzer.func_vars.items():
        live_in = {ln: set() for ln in lines}
        live_out = {ln: set() for ln in lines}
        changed = True
        line_nos = sorted(lines.keys(), reverse=True)

        while changed:
            changed = False
            for i, ln in enumerate(line_nos):
                succ_lines = line_nos[:i]
                out_set = set()
                if succ_lines:
                    out_set = live_in[succ_lines[0]]
                new_in = lines[ln]["gen"] | (out_set - lines[ln]["kill"])
                if new_in != live_in[ln] or out_set != live_out[ln]:
                    changed = True
                    live_in[ln] = new_in
                    live_out[ln] = out_set

        total_live_in += sum(len(v) for v in live_in.values())
        total_live_out += sum(len(v) for v in live_out.values())

    return {"total_live_in": total_live_in, "total_live_out": total_live_out}

def analyze_project(root_dir):
    total_summary = defaultdict(lambda: {"total_live_in": 0, "total_live_out": 0})
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root_dir)
                summary = live_variable_analysis_file(full_path)
                total_summary[rel_path]["total_live_in"] += summary["total_live_in"]
                total_summary[rel_path]["total_live_out"] += summary["total_live_out"]

    print("\n===== PROJECT-WIDE LIVE VARIABLE SUMMARY =====")
    print("File                                | Total LIVE_IN | Total LIVE_OUT")
    print("-------------------------------------------------------------------")
    for f, sums in total_summary.items():
        print(f"{f:<35} | {sums['total_live_in']:<13} | {sums['total_live_out']}")

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 2:
#         print("Usage: python lva.py <project_root_directory>")
#         sys.exit(1)
#     project_dir = sys.argv[1]
#     analyze_project(project_dir)

if __name__ == "__main__":
    import sys
   # Default folder if no argument is given
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "./HotinGo"
    analyze_project(project_dir)
