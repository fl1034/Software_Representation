# page

Get the next cards after a given one, in the order they were created. Same reply as `observe`.

Call: `{"action": "page", "path": "/cards", "after": "<id>"}`
- `after`: the last id you have. You don't usually write this call yourself:
  when a reply holds only some of the cards, its `overflow.next` is this call, ready to send.

Up to 100 cards per reply. If there are more, the reply has another `overflow` note.
