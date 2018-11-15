## Sanity check a FASTA DB

FASTA DB are easy to corrupt, and we are in need of a simple tool
to double check the DB has no unforeseen entries.

This tool will check for:

1. Duplicate entries with the same ID
2. Entries with different IDs but with overlapping sequences (i.e., 100% overlap, or one sequence completely included in another)
3. Where possible, it will try to parse the meaningful label off the FASTA header (e.g., ST allele number) and check for duplicates

### Dependencies

- CD-HIT

### Running

```
db_check.py <db.fasta>
```

### TODO

- Generalise the parsing of FASTA headers
