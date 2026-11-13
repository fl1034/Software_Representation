# page

Get the next children of any collection, after a given one, in the collection's order.
Built in: works on every node with a `"*"`, without being listed in its `api`.
A query: changes nothing. Same answer as `observe`.

Call: `{"action": "page", "path": "<collection path>", "after": "<id>"}`, for example `/tasks`.
- `after`: the last id you have. You don't usually write this call yourself:
  when an answer holds only some of a collection's children, its `overflow.next` is
  this call, ready to send.

Up to 100 children per answer. If there are more, the answer has another `overflow` note.
