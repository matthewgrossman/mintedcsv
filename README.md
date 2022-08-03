# mintedcsv
Convert our existing wedding spreadsheet to the format that [minted](https://www.minted.com/) expects

### Running
Ensure you have downloaded each sheet's csv in the directory:
```python
    csvs = [
        "Guests - Family RG.csv",
        "Guests - Family MG.csv",
        "Guests - Friends.csv",
        "Guests - Fam Friends.csv",
    ]
```

```bash
poetry run python mintedcsv.py && open output.csv
```
