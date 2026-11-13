# page

Get the next children of any collection, after a given one, in the collection's order.
Built in: works on every node with a `"*"`, without being listed in its `api`.
A query: changes nothing. Same answer as `observe`.

Call: `{"action": "page", "path": "<collection path>", "after": "<id>"}`, for example `/cards`.
- `after`: the last id you have. You don't usually write this call yourself: when an
  answer holds only some of a collection's children, its `overflow.next` is this call.

Up to 100 children per answer, with another `overflow` note if there are more.

It also works on an array that was cut short (one ending in `"... <n> more items"`):
there `after` is the number of items you already have, like `"after": 100`.
