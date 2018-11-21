## Sanity check a FASTA DB

FASTA DB are easy to corrupt, and we are in need of a simple tool
to double check the DB has no unforeseen entries.

This tool will check for:

1. Duplicate entries with the same ID
2. Entries with different IDs but with overlapping sequences (i.e., 100% overlap, or one sequence completely included in another)
3. Optionally, it will try to parse the meaningful category or label off the FASTA header (e.g., ST allele number) and ensure that distinct labels are given to completely or partially overlapping sequences.

The tool outputs:

1. A log to `stderr` signalling any potential issues.
2. A report in Markdown straight to `stdout`. You can then add it to your GitHub, or post it as a GitHub Issue, or push it through `pandoc` to transform it in to any supported format you like (e.g., PDF for your paper).
3. Optionally, the output files produced by `CD-HIT`

## What does completely and/or partially overlapping sequences mean?

Under the hood, `db-check` is running `CD-HIT` (in particular, `cd-hit-est`). Here, `db-check` runs `cd-hit-est` to identify any sequences that have 100% identity and 100% coverage (i.e., have all the same bases and are exactly the same length, and thus are identical) OR where one sequence is 100% identical to another, but it is shorter (i.e., one sequence is exactly containted within another). The first case is what we call `completely overlapping` and the second case is what we call `partially overlapping`.

Obviously, neither case is ideal. The case of `completely overlapping` means your DB has redundant sequences that should be removed. It can be especially problematic if you have two identical sequences but they are identified as distinct categories.

The case of `partially overlapping` sequences is less clear cut whether it is an issue or not. We have seen cases where novel MLST alleles were added to a scheme as exact subsets of already established alleles. In those case, it turned out the new alleles were caused by a break in the assembly, and thus were **NOT** novel alleles at all. However, there are cases where partially overlapping sequences might be biologically real (e.g. indicating a real deletion or insertion), and you do wish to keep that in your DB. If that is the case, additional logic will have to be applied to your BLAST filtering steps to make sure you get the right variant.

Whatever your case, hopefully, this tool will help you get a quick assessment of your FASTA DB, and be aware of any internal issues before releasing it in to the wild. Or, if you are a user of a FASTA DB, and you are getting funny results, hopefully this tool can help you troubleshoot the DB and pass on the developer any issues they may have with their FASTA DB.

## Dependencies

- `CD-HIT`
- `Python >=3.6`

Optionally, `pandoc`.

## Installation

### Conda

```
conda -c bioconda cd-hit
pip3 install db-check
```

### Brew

```
brew install cd-hit
pip3 install db-check
```

_NOTE_: I found that `brew install` on my MacOSX Mojave machine failed because the bottled version was compiled with a different set of headers. I fixed it by forcing it to install from source like so:

```
brew uninstall cd-hit
brew install -s cd-hit
```

## Running

```
db-check <db.fasta> > report.md
```

### Running an example

```
db-check --example
```

### Parsing categories from sequence ID

#### Using `--delimiter` and `--field`:

In some cases your category is encoded in the sequence ID with a particular delimiter (e.g., `|` or `~~`), and once the ID is split along this delimiter, the field of interest might be the second (`--field 1` --- `1` because it is 0-indexed) or, perhaps, the last one (`--field -1`).

For example, let us say you have IDs coded with the following pattern: `>seq1~~catA`. In this case, you would do the following:

```
db-check --delimiter "~~" --field -1 /path/to/db
```

#### Using `--regex`:

In some cases your category might be encoded in a more convoluted manner, and perhaps a `regex` expression with a capture group would work best. The above case could thus be equally parsed with:

```
db-check --regex ".*~~(.*)" /path/to/db
```

#### Using a `callback` function

_Implementation pending_

#### Command-line options

```
Usage: db-check [OPTIONS] FASTA

  Check a FASTA DB for potential issues.

Options:
  -d, --delimiter TEXT   When parsing a category from seqid, split on this
                         delimiter (use -1 for last element, -2 for second to
                         last, etc.).
  -f, --field INTEGER    When parsing a category from seqid using a delimiter,
                         keep this field number (0-index).
  -r, --regex TEXT       When parsing a category from seqid extract using this
                         regex.
  -a, --author TEXT      Who is running the check. (default: $USER)
  -n, --db_name TEXT     Name of the Database. (default: filename)
  -t, --threads INTEGER  How many threads to give CD-HIT (default: 1)
  -p, --prefix TEXT      Prefix of output files from CD-HIT (default: cdhit)
  -k, --keep_files       Whether to keep CD-HIT output files (default: False)
  --example              Run an example set
  --version              Show the version and exit.
  -h, --help             Show this message and exit.
```

## Examples using `pandoc` to convert the output to other formats

### Convert to HTML

```
db-check --example | pandoc --from markdown --to html5 > report.html
```

### Convert to PDF

```
db-check --example | pandoc --from markdown --to latex -o report.pdf
```

### Conver to plain text

```
db-check --example | pandoc --from markdown --to plain > report.txt
```

## TODO

- add conda recipe
- add brew recipe
- add travisCI recipe
