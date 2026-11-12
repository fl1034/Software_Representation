# page

Get the next tasks after a given one, in list order. Same reply as `observe`.

Call: `{"action": "page", "path": "/tasks", "after": "<id>"}`
- `after`: the last id you have. You don't usually write this call yourself:
  when a reply holds only some of the tasks, its `overflow.next` is this call, ready to send.

Up to 100 tasks per reply. If there are more, the reply has another `overflow` note.
