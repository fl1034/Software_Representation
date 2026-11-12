"""Reference implementation of `observe` with folding.

Usage: python3 tools/fold.py <state.json> <path> [budget_bytes]

Prints the reply an app would send for {"action": "observe", "path": <path>}.
The rule is deliberately mechanical: while the node is over budget (measured as
compact JSON), replace its largest child with a stub. Bookkeeping keys are
never folded.
"""
import copy, json, sys

NEVER_FOLD = {"app", "version", "docs", "path", "api"}

def size(node):
    return len(json.dumps(node, separators=(",", ":"), ensure_ascii=False))

def get(tree, path):
    node = tree
    for key in [p for p in path.split("/") if p]:
        node = node[key]
    return node

def stub(node, path):
    n = len([k for k in node if k not in NEVER_FOLD | {"*"}]) if isinstance(node, dict) else len(node)
    kind = "children" if isinstance(node, dict) else "items"
    return {"folded": f"{n} {kind}, {size(node) / 1024:.1f} KB. Observe {path}"}

def observe(tree, path, budget=2048):
    node = copy.deepcopy(get(tree, path))
    if isinstance(node, dict):
        while size(node) > budget:
            candidates = [(size(v), k) for k, v in node.items()
                          if k not in NEVER_FOLD and isinstance(v, (dict, list))
                          and not (isinstance(v, dict) and "folded" in v)]
            if not candidates:
                break
            s, key = max(candidates)
            child_path = path.rstrip("/") + "/" + key
            folded = stub(node[key], child_path)
            if size(folded) >= s:
                break
            node[key] = folded
    return {"ok": True, "version": tree.get("version"), "path": path, "node": node}

if __name__ == "__main__":
    tree = json.load(open(sys.argv[1]))
    budget = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
    print(json.dumps(observe(tree, sys.argv[2], budget), indent=2, ensure_ascii=False))
