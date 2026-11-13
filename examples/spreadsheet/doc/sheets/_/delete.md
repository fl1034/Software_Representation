# delete

Delete a sheet and its cells. Formulas on other sheets that refer to it then show `#REF!`.
Cannot be undone. The workbook must keep at least one sheet.

Call: `{"action": "delete", "path": "/sheets/<sheet id>"}`

Asks for confirmation first: an alert goes out on the alert channel, saying how many
formulas elsewhere would break.

Busy until someone answers: the sheet, and every formula on other sheets that uses it (see `doc/confirm.md`).

Changes, once confirmed: removes the sheet; formula cells elsewhere that used it.

Errors:
- `last_sheet`
