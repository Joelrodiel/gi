# gi
`gi` is a minimal terminal application for fast Git adding & committing.

## Usage
```
Usage: gi.py [-h] [-a] [-c] [-u] [-s]

Fast Git management.

optional arguments:
  -h, --help  show this help message and exit

Options:
  -a          Add files to stage
  -c          Create new commit
  -u          Unstage files
  -s          Combination of -a and -c, choose files to add and commit
  -d          Batch add in directory
```
  
For commands `gi -a`, `gi -u` and `gi -s` number input can be a combination of:
* List of numbers (`1,2,3`)
* Ranges (`0-3`)
* Less thans (`<4`)
* Exclusion of numbers (`0-5, !2`)
* Select all (`.`)
