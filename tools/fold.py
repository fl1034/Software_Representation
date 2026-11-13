"""Reference implementation of `observe` (with folding and `since`), `page` and `find`.

Usage:
  python3 tools/fold.py <state.json> <path> [--budget 2048] [--max-children 100]
  python3 tools/fold.py <state.json> <path> --after <id>
  python3 tools/fold.py <state.json> <path> --find '{"where": {...}, "text": "..."}'

`since` needs a change log, so it is available from Python only: see `apply` and
`observe_since` below.

Prints the reply an app would send. Everything here is deliberately mechanical:

1. Overflow: a node never returns more than `max-children` data children. If it
   has more, it returns the first ones in its own order and adds an `overflow`
   note with the exact call that gets the next page.
2. Folding: while the reply is over `budget` bytes (compact JSON), the largest
   child is replaced with a `folded` stub that says how to observe it.
"""
import argparse, copy, json

RESERVED = {"app", "version", "docs", "path", "api", "*", "defaults", "derived", "folded", "overflow", "busy"}
NEVER_FOLD = {"app", "version", "docs", "path", "api", "overflow", "busy"}


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


def count_busy(node):
    if isinstance(node, dict):
        if "busy" in node and isinstance(node["busy"], dict):
            return 1
        return sum(count_busy(v) for k, v in node.items() if k not in ("*", "busy"))
    return 0


def stub(node, path):
    n = len(data_keys(node)) if isinstance(node, dict) else len(node)
    kind = "children" if isinstance(node, dict) else "items"
    b = count_busy(node)
    busy = f", {b} busy" if b else ""
    return {"folded": f"{n} {kind}{busy}, {size(node) / 1024:.1f} KB. Observe {path}"}


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


def reply(tree, path, node, action="observe"):
    """Queries answer with state directly; there is no receipt or ping."""
    return {"path": path, "version": tree.get("version"), "node": node}


def observe(tree, path, budget=2048, max_children=100):
    node = get(tree, path)
    if isinstance(node, dict):
        node = window(tree, node, path, data_keys(node), max_children, {"action": "page", "path": path})
    return reply(tree, path, fold(copy.deepcopy(node), path, budget))


def page(tree, path, after, budget=2048, max_children=100):
    node = get(tree, path)
    keys = data_keys(node)
    rest = keys[keys.index(after) + 1:] if after in keys else keys
    return reply(tree, path, fold(window(tree, node, path, rest, max_children, {"action": "page", "path": path}), path, budget), "page")


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
    return reply(tree, path, fold(window(tree, node, path, keys, max_children, call, "matches"), path, budget), "find")


# ---------- since ----------
# A real app stamps each node it writes, and its ancestors, with the new version,
# and keeps deletion markers for a while. Here a flat log of writes stands in for
# both: one entry per change, {"version", "op", "path"}.

def parts(path):
    return [p for p in path.split("/") if p]


def apply(tree, log, changes):
    """Apply add/set/remove changes as one new version, and record them in the log."""
    tree["version"] += 1
    for c in changes:
        *parent, key = parts(c["path"])
        node = get(tree, "/" + "/".join(parent))
        if c["op"] == "remove":
            node.pop(key, None)
        else:
            node[key] = copy.deepcopy(c["value"])
        log.append({"version": tree["version"], "op": c["op"], "path": c["path"]})
    return tree["version"]


def exists(tree, path):
    try:
        get(tree, path); return True
    except (KeyError, TypeError):
        return False


def observe_since(tree, log, path, since, oldest_kept=0, budget=2048):
    if since < oldest_kept:
        return {"path": path, "error": "too_old",
                "message": f"Changes before version {oldest_kept} are no longer kept. Observe without since."}
    prefix = path.rstrip("/") + "/"
    recent = [e for e in log if e["version"] > since and (e["path"] + "/").startswith(prefix)]
    written = sorted({e["path"] for e in recent if e["op"] != "remove" and exists(tree, e["path"])}, key=len)
    removed = sorted({e["path"] for e in recent if e["op"] == "remove" and not exists(tree, e["path"])})
    node, taken = {}, []
    for p in written:
        if any((p + "/").startswith(t + "/") for t in taken):
            continue  # an ancestor is already included whole
        taken.append(p)
        rel = parts(p)[len(parts(path)):]
        cur = node
        for k in rel[:-1]:
            cur = cur.setdefault(k, {})
        cur[rel[-1]] = copy.deepcopy(get(tree, p))
    r = reply(tree, path, fold(node, path, budget))
    r["since"] = since
    r["removed"] = removed
    return r


# ---------- submissions: busy and settle ----------
# A submission marks nodes busy at once and settles them later. While busy, a node
# shows its last well-defined value, and the root lists every busy path.

def mark_busy(tree, submission, paths):
    for p in paths:
        *parent, key = parts(p)
        node = get(tree, "/" + "/".join(parent))
        node[key] = {"busy": {"by": submission, "last": node[key]}}
    tree.setdefault("busy", []).extend(paths)


def settle(tree, log, submission, changes):
    """Restore busy nodes, apply the changes as the next well-defined state, return the ping."""
    for p in list(tree.get("busy", [])):
        *parent, key = parts(p)
        node = get(tree, "/" + "/".join(parent))
        if isinstance(node.get(key), dict) and node[key].get("busy", {}).get("by") == submission:
            node[key] = node[key]["busy"]["last"]
            tree["busy"].remove(p)
    if not tree.get("busy"):
        tree.pop("busy", None)
    if changes:
        apply(tree, log, changes)
    return {"ping": submission, "version": tree["version"],
            "changed": [c["path"] for c in changes if c["op"] != "remove"],
            "removed": [c["path"] for c in changes if c["op"] == "remove"]}


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
