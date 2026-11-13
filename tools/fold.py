"""Reference implementation of the queries, plus helpers for submissions.

Usage:
  python3 tools/fold.py <state.json> <path> [--budget 2048] [--max-children 100] [--view /cards=expand]
  python3 tools/fold.py <state.json> <path> --after <id>
  python3 tools/fold.py <state.json> <path> --find '{"where": {...}, "text": "..."}'

Prints the answer an app would send, as compact JSON (add --pretty to read it).

State files hold the tree the agent sees, plus storage-only keys that start with
`_` and are never shown: `_version` (the current version) and `_defaults`
(values of fields that items leave out, per collection template path, used by
`find`). A real app keeps these however it likes.

Everything here is deliberately mechanical:

1. Overflow: a collection (a node with a `*`) never shows more than
   `max-children` children. If it has more, it shows the first ones and adds
   `"overflow": {"shown", "total", "next"}`, where `next` is the call for the rest.
2. Views: the agent may set any node to `fold` (barest summary) or `expand`
   (never folded automatically; only the overflow limit applies).
3. Folding: while the answer is over `budget` bytes, the app folds the smallest
   node whose folding alone brings it under budget, or, if no single node is
   enough, the largest node, and repeats. Nodes protected by an `expand` are
   never folded. A stub keeps the node's `api`.
"""
import argparse, copy, json

RESERVED = {"app", "api", "*", "folded", "overflow", "busy"}
NEVER_FOLD = {"app", "api", "overflow", "busy"}
LIST_CAP = 100  # most paths a ping, receipt or since-answer lists before giving a count


def size(node):
    return len(json.dumps(node, separators=(",", ":"), ensure_ascii=False))


def parts(path):
    return [p for p in path.split("/") if p]


def get(tree, path):
    node = tree
    for key in parts(path):
        node = node[key]
    return node


def exists(tree, path):
    try:
        get(tree, path); return True
    except (KeyError, TypeError):
        return False


def hidden(key):
    return key.startswith("_")


def data_keys(node):
    return [k for k in node if k not in RESERVED and not hidden(k)]


def visible(node):
    """Drop storage-only keys."""
    if isinstance(node, dict):
        return {k: visible(v) for k, v in node.items() if not hidden(k)}
    if isinstance(node, list):
        return [visible(v) for v in node]
    return node


def child_path(path, key):
    return path.rstrip("/") + "/" + key


# ---------- overflow ----------

def window(node, keys, max_children, next_call):
    """Keep reserved keys plus the first `max_children` of `keys`; note any overflow."""
    out = {k: v for k, v in node.items() if k in RESERVED and k != "overflow"}
    shown = keys[:max_children]
    for k in shown:
        out[k] = copy.deepcopy(node[k])
    if len(keys) > len(shown):
        out["overflow"] = {"shown": len(shown), "total": len(keys), "next": dict(next_call, after=shown[-1])}
    return out


def template_at(tree, path):
    """The node that describes `path`: the real node, or a `*` template above it."""
    t = tree
    for key in parts(path):
        if not isinstance(t, dict):
            return {}
        t = t["*"] if "*" in t else t.get(key, {})
    return t if isinstance(t, dict) else {}


def is_busy(node):
    return isinstance(node, dict) and isinstance(node.get("busy"), dict)


def window_all(tree, node, path, max_children, tmpl=None):
    """Apply the overflow limit to every collection in the subtree."""
    if tmpl is None:
        tmpl = template_at(tree, path)
    if not isinstance(node, dict) or is_busy(node):
        return node
    keys = data_keys(node)
    if "*" in tmpl and len(keys) > max_children:
        node = window(node, keys, max_children, {"action": "page", "path": path})
    for k in data_keys(node):
        child_tmpl = tmpl["*"] if "*" in tmpl else tmpl.get(k, {})
        node[k] = window_all(tree, node[k], child_path(path, k), max_children,
                             child_tmpl if isinstance(child_tmpl, dict) else {})
    return node


# ---------- folding and views ----------

def count_busy(node):
    if is_busy(node):
        return 1
    if isinstance(node, dict):
        return sum(count_busy(v) for k, v in node.items() if k != "*")
    return 0


def count_children(node):
    n = len(data_keys(node)) if isinstance(node, dict) else len(node)
    return f"{n} {'children' if isinstance(node, dict) else 'items'}"


def auto_stub(node, tmpl=None):
    """Folded by the app: a summary, with the node's api still visible (from the node or its template)."""
    b = count_busy(node)
    api = node.get("api") if isinstance(node, dict) else None
    api = api or (tmpl or {}).get("api")
    out = {"api": api} if api else {}
    out["folded"] = f"{count_children(node)}{f', {b} busy' if b else ''}, {size(node) / 1024:.1f} KB"
    return out


def min_stub(node):
    """Folded by the agent's choice: the barest summary."""
    return {"folded": count_children(node)}


def foldable(node, path):
    """(path, parent, key, child) for every descendant that could be folded."""
    if not isinstance(node, dict):
        return
    for k, v in node.items():
        if k in NEVER_FOLD or not isinstance(v, (dict, list)) or (isinstance(v, dict) and "folded" in v):
            continue
        p = child_path(path, k)
        yield p, node, k, v
        yield from foldable(v, p)


def fold(node, path, budget, views=None, tree=None):
    """Apply the agent's views, then fold automatically, largest first, until under budget.

    views: {path: "fold" | "expand"}; anything else is "auto".
    - fold: the barest summary wherever it appears below the observed node.
    - expand: never folded automatically, nor is anything inside it or above it.
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
    if any(path == e or path.startswith(e + "/") for e in expanded):
        return node

    def protected(p):
        return any(p == e or p.startswith(e + "/") or e.startswith(p + "/") for e in expanded)

    while isinstance(node, dict) and size(node) > budget:
        need = size(node) - budget
        candidates = []
        for p, parent, k, v in foldable(node, path):
            if protected(p):
                continue
            stub = auto_stub(v, template_at(tree, p) if tree else None)
            saving = size(v) - size(stub)
            if saving > 0:
                candidates.append((size(v), saving, parent, k, stub))
        if not candidates:
            break
        enough = [c for c in candidates if c[1] >= need]
        # the smallest node that alone is enough; otherwise the largest, and go round again
        _, _, parent, k, stub = min(enough, key=lambda c: c[0]) if enough else max(candidates, key=lambda c: c[0])
        parent[k] = stub
    return node


# ---------- queries ----------

def answer(tree, node):
    """Queries answer at once with state: no receipt, no ping, no echo of the call."""
    return {"version": tree["_version"], "node": node}


def observe(tree, path, budget=2048, max_children=100, views=None):
    node = window_all(tree, visible(copy.deepcopy(get(tree, path))), path, max_children)
    return answer(tree, fold(node, path, budget, views, tree))


def view(views, path, mode):
    """Set how a node is shown to this agent from now on. Answers with a confirmation only."""
    if mode == "auto":
        views.pop(path, None)
    else:
        views[path] = mode
    return {"view": mode}


def page(tree, path, after, budget=2048, max_children=100, views=None):
    node = visible(get(tree, path))
    keys = data_keys(node)
    rest = keys[keys.index(after) + 1:] if after in keys else keys
    return answer(tree, fold(window(node, rest, max_children, {"action": "page", "path": path}), path, budget, views, tree))


def template_path(tree, path):
    """/cards/k4/checklist -> /cards/*/checklist: the key `_defaults` uses."""
    out, t = [], tree
    for key in parts(path):
        is_id = isinstance(t, dict) and "*" in t
        out.append("*" if is_id else key)
        t = t["*"] if is_id else (t.get(key, {}) if isinstance(t, dict) else {})
    return "/" + "/".join(out)


def matches(child, defaults, where, text):
    full = dict(defaults, **child) if isinstance(child, dict) else child
    for field, want in (where or {}).items():
        have = full.get(field) if isinstance(full, dict) else None
        if isinstance(have, list) and not isinstance(want, list):
            if want not in have:
                return False
        elif have != want:
            return False
    if text:
        strings = [v for v in (full.values() if isinstance(full, dict) else [full]) if isinstance(v, str)]
        if not any(text.lower() in s.lower() for s in strings):
            return False
    return True


def find(tree, path, where=None, text=None, after=None, budget=2048, max_children=100, views=None):
    node = visible(get(tree, path))
    defaults = tree.get("_defaults", {}).get(template_path(tree, path) + "/*", {})
    keys = [k for k in data_keys(node) if matches(node[k], defaults, where, text)]
    if after in keys:
        keys = keys[keys.index(after) + 1:]
    call = {"action": "find", "path": path}
    if where: call["where"] = where
    if text: call["text"] = text
    return answer(tree, fold(window(node, keys, max_children, call), path, budget, views, tree))


# ---------- since ----------
# A real app stamps each node it writes, and its ancestors, with the new version,
# and keeps deletion markers for a while. Here a flat log of writes stands in for
# both: one entry per change, {"version", "op", "path"}.

def capped(out, key, paths):
    """Add a list of paths, at most LIST_CAP of them, with a count if there are more. Omit if empty."""
    if paths:
        out[key] = paths[:LIST_CAP]
        if len(paths) > LIST_CAP:
            out[key + "_total"] = len(paths)
    return out


def apply(tree, log, changes):
    """Apply add/set/remove changes as one new version, and record them in the log."""
    tree["_version"] += 1
    for c in changes:
        *parent, key = parts(c["path"])
        node = get(tree, "/" + "/".join(parent))
        if c["op"] == "remove":
            node.pop(key, None)
        else:
            node[key] = copy.deepcopy(c["value"])
        log.append({"version": tree["_version"], "op": c["op"], "path": c["path"]})
    return tree["_version"]


def observe_since(tree, log, path, since, oldest_kept=0, budget=2048):
    if since < oldest_kept:
        return {"error": "too_old", "message": f"Changes before version {oldest_kept} are no longer kept. Observe without since."}
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
        cur[rel[-1]] = visible(copy.deepcopy(get(tree, p)))
    return capped(answer(tree, fold(node, path, budget, None, tree)), "removed", removed)


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
    if paths:
        tree.setdefault("busy", []).extend(paths)


def receipt(submission, busy=None, feedback=None):
    r = {"receipt": submission}
    capped(r, "busy", busy or [])
    if feedback:
        r["feedback"] = feedback
    return r


def busy_event(submission, paths):
    """What listeners get when a submission makes paths busy. The caller gets its receipt instead."""
    return capped({"busy": submission}, "paths", paths)


def settle(tree, log, submission, changes, feedback=None):
    """Restore busy nodes, apply the changes as the next well-defined state, return the ping."""
    for p in list(tree.get("busy", [])):
        *parent, key = parts(p)
        node = get(tree, "/" + "/".join(parent))
        if is_busy(node.get(key)) and node[key]["busy"]["by"] == submission:
            node[key] = node[key]["busy"]["last"]
            tree["busy"].remove(p)
    if not tree.get("busy"):
        tree.pop("busy", None)
    if changes:
        apply(tree, log, changes)
    ping = {"ping": submission, "version": tree["_version"]}
    capped(ping, "changed", [c["path"] for c in changes if c["op"] != "remove"])
    capped(ping, "removed", [c["path"] for c in changes if c["op"] == "remove"])
    if feedback:
        ping["feedback"] = feedback
    return ping


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("state"); ap.add_argument("path")
    ap.add_argument("--budget", type=int, default=2048)
    ap.add_argument("--max-children", type=int, default=100)
    ap.add_argument("--after")
    ap.add_argument("--find", help='JSON: {"where": {...}, "text": "..."}')
    ap.add_argument("--view", action="append", default=[], help="path=fold|expand, repeatable")
    ap.add_argument("--pretty", action="store_true", help="indent the output for people to read")
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
    print(json.dumps(r, indent=2 if a.pretty else None, separators=None if a.pretty else (",", ":"), ensure_ascii=False))
