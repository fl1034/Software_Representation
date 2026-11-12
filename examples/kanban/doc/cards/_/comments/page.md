# page

Get the next comments after a given one, in the order they were posted. Same reply as `observe`.

Call: `{"action": "page", "path": "/cards/<card id>/comments", "after": "<id>"}`
- `after`: the last id you have. You don't usually write this call yourself:
  when a reply holds only some of the comments, its `overflow.next` is this call, ready to send.

Up to 100 comments per reply. If there are more, the reply has another `overflow` note.
