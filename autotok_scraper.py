#!/usr/bin/env python3
"""
Generate a word list from an apertium .autotok.hfst transducer.

Usage:
    python3 autotok_scraper.py <autotok.hfst> [max_cycles]

Arguments:
    autotok.hfst  Path to the compiled autotok transducer for your language.
                  Build it from the language package with: make <lang>.autotok.hfst
    max_cycles    Max cycles to follow in the transducer expansion (default: 0).
                  Increase if the word list seems too small.

Output:
    Writes <lang>_autotok_scraped.txt in the current directory, named after
    the input file (e.g. wuu.autotok.hfst → wuu_autotok_scraped.txt).

Example:
    python3 autotok_scraper.py wuu.autotok.hfst 0
    python3 autotok_scraper.py /path/to/cmn.autotok.hfst 0
"""

import subprocess
import sys
import os
from itertools import groupby
from pathlib import Path

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

hfst_path = sys.argv[1]
max_cycles = sys.argv[2] if len(sys.argv) > 2 else "0"

# Derive output filename from input: wuu.autotok.hfst → wuu_autotok_scraped.txt
lang = Path(hfst_path).name.split('.')[0]
out_path = f"{lang}_autotok_scraped.txt"

# Pass the full environment so DYLD_LIBRARY_PATH is inherited on macOS
env = os.environ.copy()
result = subprocess.run(
    f"hfst-expand -c{max_cycles} {hfst_path}",
    shell=True, capture_output=True, text=True, env=env
)

if result.returncode != 0:
    print(f"Error running hfst-expand: {result.stderr[:300]}", file=sys.stderr)
    print("Make sure hfst tools are installed and on PATH.", file=sys.stderr)
    sys.exit(1)

words = result.stdout.split()
words.sort(key=len)
grouped = [list(g) for _, g in groupby(words, key=len)]

with open(out_path, 'w') as f:
    for group in grouped:
        f.write(f"!!!!!{len(group[0])}\n")
        for word in group:
            if not (word.replace('.', '', 1).isdigit() or word.replace(',', '', 1).isdigit()):
                f.write(word + '\n')

print(f"Wrote {len(words)} words to {out_path}")
