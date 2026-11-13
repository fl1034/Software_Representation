"""Reference implementation of `observe` (with folding and `since`), `page` and `find`.

Usage:
  python3 tools/fold.py <state.json> <path> [--budget 2048] [--max-children 100] [--view /cards=expand]
  python3 tools/fold.py <state.json> <path> --after <id>
  python3 tools/fold.py <state.json> <path> --find '{"where": {...}, "text": "..."}'

`since` needs a change log, so it is available from Python only: see `apply` and
`observe_since` below.

Prints the reply an app would send. Everything here is deliberately mechanical:

1. Overflow: a node never returns more than `max-children` data children. If it
   has more, it returns the first ones in its own order and adds an `overflow`
   note with the exact call that gets the next page.
2. Views: the agent may set any node to `fold` (barest summary) or `expand`
   (never folded automatically; only the overflow limit applies).
3. Folding: while the reply is over `budget` bytes (compact JSON), the largest
   node not protected by an `expand` is replaced with a stub that keeps its
   `path` and `api` and says how to observe it.
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


def parts(path):
    return [p for p in path.split("/") if p]


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


def count_children(node):
    n = len(data_keys(node)) if isinstance(node, dict) else len(node)
    return n, ("children" if isinstance(node, dict) else "items")


def auto_stub(node, path):
    """What the app folds on its own: a summary, but the node's path and api stay visible."""
    n, kind = count_children(node)
    b = count_busy(node)
    busy = f", {b} busy" if b else ""
    out = {k: node[k] for k in ("path", "api") if isinstance(node, dict) and k in node}
    out["folded"] = f"{n} {kind}{busy}, {size(node) / 1024:.1f} KB. Observe {path}"
    return out


def min_stub(node):
    """What the agent asked to fold: the barest summary."""
    n, kind = count_children(node)
    return {"folded": f"{n} {kind}"}


def child_path(path, key):
    return path.rstrip("/") + "/" + key


def template_at(tree, path):
    """The node that describes `path`: the real node, or a `*` template above it."""
    t = tree
    for key in parts(path):
        if not isinstance(t, dict):
            return {}
        t = t["*"] if "*" in t else t.get(key, {})
    return t if isinstance(t, dict) else {}


def is_collection(tmpl):
    """Children are ids, described by a `*`, not fixed fields. Every collection can be paged."""
    return "*" in tmpl


def window_all(tree, node, path, max_children, tmpl=None):
    """Apply the overflow limit to every collection in the subtree, not just the top."""
    if tmpl is None:
        tmpl = template_at(tree, path)
    if not isinstance(node, dict) or "busy" in node and isinstance(node["busy"], dict):
        return node
    keys = data_keys(node)
    if is_collection(tmpl) and len(keys) > max_children:
        node = window(tree, node, path, keys, max_children, {"action": "page", "path": path})
    for k in data_keys(node):
        child_tmpl = tmpl["*"] if "*" in tmpl else tmpl.get(k, {})
        node[k] = window_all(tree, node[k], child_path(path, k), max_children,
                             child_tmpl if isinstance(child_tmpl, dict) else {})
    return node


def foldable(node, path):
    """(path, parent, key, child) for every descendant that could be folded."""
    if not isinstance(node, dict):
        return
    for k, v in node.items():
        if k in NEVER_FOLD or not isinstance(v, (dict, list)):
            continue
        if isinstance(v, dict) and "folded" in v:
            continue
        p = child_path(path, k)
        yield p, node, k, v
        yield from foldable(v, p)


def fold(node, path, budget, views=None):
    """Apply the agent's views, then fold automatically, largest first, until under budget.

    views: {path: "fold" | "expand"}; anything else is "auto".
    - fold: shown as the barest summary wherever it appears below the observed node.
    - expand: never folded automatically, nor is anything inside it. Only the
      overflow limit applies. Its ancestors aren't folded either, so it stays reachable.
    """
    views = views or {}

    def apply_folds(n, p):
        if not isinstance(n, dict):
            return
        for k, v in list(n.items()):
            if k in NEVER_FOLD or not isinstance(v, (dict, list)):
                continue
            cp = child_path(p, k)
            if views.get(cp) == "fold":
                n[k] = min_stub(v)
            else:
                apply_folds(v, cp)
    apply_folds(node, path)

    expanded = [p for p, m in views.items() if m == "expand"]
    def protected(p):
        return any(p == e or p.startswith(e + "/") or e.startswith(p + "/") for e in expanded)
    if any(path == e or path.startswith(e + "/") for e in expanded):
        return node  # the observed node is itself expanded

    while isinstance(node, dict) and size(node) > budget:
        candidates = [(size(v), p, parent, k) for p, parent, k, v in foldable(node, path) if not protected(p)]
        if not candidates:
            break
        s_, p, parent, k = max(candidates, key=lambda c: c[0])
        folded = auto_stub(parent[k], p)
        if size(folded) >= s_:
            break
        parent[k] = folded
    return node


def reply(tree, path, node, action="observe"):
    """Queries answer with state directly; there is no receipt or ping."""
    return {"path": path, "version": tree.get("version"), "node": node}


def observe(tree, path, budget=2048, max_children=100, views=None):
    node = window_all(tree, copy.deepcopy(get(tree, path)), path, max_children)
    return reply(tree, path, fold(node, path, budget, views))


def view(tree, path, mode, views, budget=2048, max_children=100):
    """Set how a node is shown to this agent from now on, and show it that way."""
    if mode == "auto":
        views.pop(path, None)
    else:
        views[path] = mode
    if mode == "fold":
        node = min_stub(get(tree, path))
    else:
        node = observe(tree, path, budget, max_children, views)["node"]
    return {"path": path, "version": tree.get("version"), "view": mode, "node": node}


def page(tree, path, after, budget=2048, max_children=100, views=None):
    node = get(tree, path)
    keys = data_keys(node)
    rest = keys[keys.index(after) + 1:] if after in keys else keys
    return reply(tree, path, fold(window(tree, node, path, rest, max_children, {"action": "page", "path": path}), path, budget, views), "page")


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


def find(tree, path, where=None, text=None, after=None, budget=2048, max_children=100, views=None):
    node = get(tree, path)
    defaults = node.get("*", {}).get("defaults", {})
    keys = [k for k in data_keys(node) if matches(node[k], defaults, where, text)]
    if after in keys:
        keys = keys[keys.index(after) + 1:]
    call = {"action": "find", "path": path}
    if where: call["where"] = where
    if text: call["text"] = text
    return reply(tree, path, fold(window(tree, node, path, keys, max_children, call, "matches"), path, budget, views), "find")


# ---------- since ----------
# A real app stamps each node it writes, and its ancestors, with the new version,
# and keeps deletion markers for a while. Here a flat log of writes stands in for
# both: one entry per change, {"version", "op", "path"}.

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

def mark_busy(tree, submission, paths, progress=None):
    for p in paths:
        *parent, key = parts(p)
        node = get(tree, "/" + "/".join(parent))
        marker = {"by": submission}
        if progress:
            marker["progress"] = progress  # only when the app can really count its work
        marker["last"] = node[key]
        node[key] = {"busy": marker}
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
    ap.add_argument("--view", action="append", default=[], help="path=fold|expand, repeatable")
    a = ap.parse_args()
    tree = json.load(open(a.state))
    views = dict(v.split("=", 1) for v in a.view)
    if a.find:
        q = json.loads(a.find)
        r = find(tree, a.path, q.get("where"), q.get("text"), a.after, a.budget, a.max_children, views)
    elif a.after:
        r = page(tree, a.path, a.after, a.budget, a.max_children, views)
    else:
        r = observe(tree, a.path, a.budget, a.max_children, views)
    print(json.dumps(r, indent=2, ensure_ascii=False))
