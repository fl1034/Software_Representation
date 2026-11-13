# delete

Delete a sheet and its cells. Formulas on other sheets that refer to it then show `#REF!`.
Cannot be undone. The workbook must keep at least one sheet.

Call: `{"action": "delete", "path": "/sheets/<sheet id>"}`

Asks for confirmation first. The receipt carries an alert saying how many formulas
elsewhere would break, and the sheet and those formula cells are busy until someone
answers (see `doc/confirm.md`).

Changes, once confirmed: removes the sheet; formula cells elsewhere that used it.

Errors:
- `last_sheet`
