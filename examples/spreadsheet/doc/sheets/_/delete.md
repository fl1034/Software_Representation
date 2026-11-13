# delete

Delete a sheet and its cells. Formulas on other sheets that refer to it then show `#REF!`.
Cannot be undone. The workbook must keep at least one sheet.

Call: `{"action": "delete", "path": "/sheets/<sheet id>"}`

Changes: removes the sheet; formula cells elsewhere that used it.

Errors:
- `last_sheet`
