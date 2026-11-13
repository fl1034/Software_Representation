# Spreadsheet example

`app.html` is a small spreadsheet, built before its representation: sheets you can
add, rename and delete, a 26-column grid with a formula bar, formulas with ranges,
functions and references to other sheets, error values, and row insert/delete that
rewrites formulas to follow the moved cells. It opens on a household budget and a
summary sheet that refers to it.

- `state.json`: the workbook as the agent sees it, 1.7 KB. Small enough that
  `observe /` folds nothing.
- `doc/`: 17 files. The general ones match the other examples; the rest cover sheets
  and cells. `doc/sheets/_/cells/_/README.md` explains how cells are written.
- `exchange.json`: an agent corrects a figure and reports the new savings rate, adds a
  budget row, renames a sheet, backs out of deleting a sheet, and meets a refused
  submission, an error value and a long sheet. 18 steps, 6.1 KB.

The engine that generated the state and session is a Python port of the app's own.
On the starting workbook it agrees with the app on all 63 cells.

## How cells are written

```json
"B3": 410,                                         plain number
"A3": "Groceries",                                 plain text
"E3": {"f": "=SUM(B3:D3)", "v": 1247},             formula and its value
"B9": {"f": "=B5/0", "e": "#DIV/0!"}               formula whose value is an error
```

An agent sees each formula together with its value. A screenshot shows only values,
so it can't tell a typed 1247 from a computed one.

## What the protocol handled without changes

- **Cascading busy.** Changing C3 makes 12 cells on two sheets busy: every formula
  that depends on C3, directly or not. The ping then lists the 11 whose values
  changed. The 12th (`MAX` of the totals) was busy but kept its value, so it isn't in
  the ping. "Busy" means "may change", the ping says what did.
- **Errors in two places.** A formula that divides by zero is written successfully and
  its value is `#DIV/0!`: that's state, in the tree. A cell outside the grid is a
  refused submission: that's feedback, never in the tree.
- **App-specific `find`.** The cells' `find` takes a `range`, so the agent reads one
  row (`A8:F8`) without paging through the sheet.
- **Batches.** `set` writes many cells in one submission, all or none. The agent
  added a whole budget row, formulas included, in one call.
- **Confirmation.** Deleting a sheet asks first. Even with `wait`, the receipt comes
  back at once, carrying an alert that says 5 formulas on Summary would break. The
  sheet and those 5 cells are busy meanwhile; the rest of the workbook isn't. The agent
  checks with the person and cancels, and the delete's ping reports nothing changed.
- **Item docs.** The cell encoding and formula language are explained once, in the
  cells' item doc, instead of in every observation.

## What it exposed

**1. IDs that are positions.** The format assumes an item's path never changes. Cell
ids are positions, and positions are how spreadsheets and their formulas identify
cells, so the representation keeps them. But inserting one row in this small sheet
produced a ping listing 38 changed and 11 removed paths, because every cell below it
got a new id. On a sheet with thousands of cells, the same insert would always hit
the 100-path cap, and the list itself would say little.

A general fix: when a ping would list more paths than the cap, the app may name their
nearest common ancestor instead (`"changed": ["/sheets/s1/cells"]`, meaning anything
under it may have changed). The agent then re-observes or uses `find`. It's mechanical,
and it works for any app with positional ids or bulk changes.

**2. Where a nested collection's actions go.** The cells' own actions (`set`, `clear`,
`find`) are the same for every sheet, so they're written once in the sheets' `*`, as
`"cells": {"api": [...], "*": {}}`. The spec now says that `*` mirrors a child's shape,
including collections inside it. The app's own fold stubs look up a node's `api` in its
template, so a folded sheet's cells still show their actions.

## Not tested here

Long text in a single value, values that change continuously, and permissions. A text
editor or a media player would be the place to test those.

## Left out on purpose

The selected cell, the formula bar, column widths, scrolling and the in-cell editor.

## Behaviour that differs from the UI

- `set` writes several cells at once; the UI edits one at a time.
- `insert_rows` and `delete_rows` take a `count`; the UI inserts or deletes one row.
- `add` takes an optional name; the UI always starts with `Sheet<n>`.
