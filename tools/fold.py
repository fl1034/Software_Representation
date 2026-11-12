"""Reference implementation of `observe`, `page` and `find`.

Usage:
  python3 tools/fold.py <state.json> <path> [--budget 2048] [--max-children 100]
  python3 tools/fold.py <state.json> <path> --after <id>
  python3 tools/fold.py <state.json> <path> --find '{"where": {...}, "text": "..."}'

Prints the reply an app would send. Everything here is deliberately mechanical:

1. Overflow: a node never returns more than `max-children` data children. If it
   has more, it returns the first ones in its own order and adds an `overflow`
   note with the exact call that gets the next page.
2. Folding: while the reply is over `budget` bytes (compact JSON), the largest
   child is replaced with a `folded` stub that says how to observe it.
"""
import argparse, copy, json

RESERVED = {"app", "version", "docs", "path", "api", "*", "defaults", "derived", "folded", "overflow"}
NEVER_FOLD = {"app", "version", "docs", "path", "api", "overflow"}


def size(node):
    return len(json.dumps(node, separators=(",", ":"), ensure_ascii=False))


def get(tree, path):
    node = tree
    for key in [p for p in path.split("/") if p]:
        node = node[key]
    return node


def data_keys(node):
    return [k for k in node if k not in RESERVED]


def doc_path(path, action, tree):
    """doc/<path with ids replaced by _>/<action>.md, walking the tree to tell ids from fixed keys."""
    parts, node = [], tree
    for key in [p for p in path.split("/") if p]:
        is_id = isinstance(node, dict) and "*" in node and key not in RESERVED
        parts.append("_" if is_id else key)
        node = node[key] if isinstance(node, dict) and key in node else {}
    return "doc/" + "/".join(parts + [action]) + ".md"


def window(tree, node, path, keys, max_children, next_call, noun="children"):
    """Keep reserved keys plus the first `max_children` of `keys`; note any overflow."""
    out = {k: v for k, v in node.items() if k in RESERVED and k != "overflow"}
    shown = keys[:max_children]
    for k in shown:
        out[k] = copy.deepcopy(node[k])
    if len(keys) > len(shown):
        hint = ""
        if "find" in node.get("api", []):
            hint = f", or narrow it down with find ({doc_path(path, 'find', tree)})"
        out["overflow"] = {
            "message": f"Showing {len(shown)} of {len(keys)} {noun}. Send `next` for more{hint}.",
            "next": dict(next_call, after=shown[-1]),
        }
    return out


def stub(node, path):
    n = len(data_keys(node)) if isinstance(node, dict) else len(node)
    kind = "children" if isinstance(node, dict) else "items"
    return {"folded": f"{n} {kind}, {size(node) / 1024:.1f} KB. Observe {path}"}


def fold(node, path, budget):
    while isinstance(node, dict) and size(node) > budget:
        candidates = [(size(v), k) for k, v in node.items()
                      if k not in NEVER_FOLD and isinstance(v, (dict, list))
                      and not (isinstance(v, dict) and "folded" in v)]
        if not candidates:
            break
        s, key = max(candidates)
        folded = stub(node[key], path.rstrip("/") + "/" + key)
        if size(folded) >= s:
            break
        node[key] = folded
    return node


def reply(tree, path, node):
    return {"ok": True, "version": tree.get("version"), "path": path, "node": node}


def observe(tree, path, budget=2048, max_children=100):
    node = get(tree, path)
    if isinstance(node, dict):
        node = window(tree, node, path, data_keys(node), max_children, {"action": "page", "path": path})
    return reply(tree, path, fold(copy.deepcopy(node), path, budget))


def page(tree, path, after, budget=2048, max_children=100):
    node = get(tree, path)
    keys = data_keys(node)
    rest = keys[keys.index(after) + 1:] if after in keys else keys
    return reply(tree, path, fold(window(tree, node, path, rest, max_children, {"action": "page", "path": path}), path, budget))


def matches(child, defaults, where, text):
    full = dict(defaults, **child) if isinstance(child, dict) else child
    for field, want in (where or {}).items():
        have = full.get(field)
        if isinstance(have, list) and not isinstance(want, list):
            if want not in have:
                return False
        elif have != want:
            return False
    if text:
        strings = [v for v in full.values() if isinstance(v, str)]
        if not any(text.lower() in s.lower() for s in strings):
            return False
    return True


def find(tree, path, where=None, text=None, after=None, budget=2048, max_children=100):
    node = get(tree, path)
    defaults = node.get("*", {}).get("defaults", {})
    keys = [k for k in data_keys(node) if matches(node[k], defaults, where, text)]
    if after in keys:
        keys = keys[keys.index(after) + 1:]
    call = {"action": "find", "path": path}
    if where: call["where"] = where
    if text: call["text"] = text
    return reply(tree, path, fold(window(tree, node, path, keys, max_children, call, "matches"), path, budget))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("state"); ap.add_argument("path")
    ap.add_argument("--budget", type=int, default=2048)
    ap.add_argument("--max-children", type=int, default=100)
    ap.add_argument("--after")
    ap.add_argument("--find", help='JSON: {"where": {...}, "text": "..."}')
    a = ap.parse_args()
    tree = json.load(open(a.state))
    if a.find:
        q = json.loads(a.find)
        r = find(tree, a.path, q.get("where"), q.get("text"), a.after, a.budget, a.max_children)
    elif a.after:
        r = page(tree, a.path, a.after, a.budget, a.max_children)
    else:
        r = observe(tree, a.path, a.budget, a.max_children)
    print(json.dumps(r, indent=2, ensure_ascii=False))
