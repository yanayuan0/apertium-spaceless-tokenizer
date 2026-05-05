#!/usr/bin/env python3
"""
Generate a word list from an apertium .dix dictionary file.

Use this for languages whose apertium package uses .dix format (e.g. apertium-zho
for Mandarin) rather than .lexd + .hfst format.

Usage:
    python3 dix_scraper.py <dictionary.dix>

Output:
    Writes <lang>_autotok_scraped.txt in the current directory, named after
    the input file (e.g. apertium-zho.zho.dix → zho_autotok_scraped.txt).

Example:
    python3 dix_scraper.py apertium-zho.zho.dix
    python3 dix_scraper.py /path/to/apertium-jpn.jpn.dix
"""

import sys
import unicodedata
import xml.etree.ElementTree as ET
from itertools import groupby
from pathlib import Path

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

dix_path = sys.argv[1]

# Derive output filename: apertium-zho.zho.dix → zho_autotok_scraped.txt
parts = Path(dix_path).stem.split('.')
lang = parts[-1] if len(parts) > 1 else parts[0]
out_path = f"{lang}_autotok_scraped.txt"

def is_target_script(s):
    """
    Return True if s contains only characters from non-Latin scripts
    (CJK, Arabic, Hebrew, Devanagari, etc.) with no spaces.

    This keeps the tokenizer language-agnostic: any spaceless script
    whose characters appear in the dictionary will be handled.
    """
    if not s or any(c.isspace() for c in s):
        return False
    for c in s:
        cat = unicodedata.category(c)
        # Allow letters (Lo = other letter covers CJK, Arabic, etc.)
        # and marks (Mn, Mc used in Devanagari, Arabic vowel marks, etc.)
        # Reject ASCII letters, digits, and punctuation.
        if cat not in ('Lo', 'Mn', 'Mc') or c.isascii():
            return False
    return True

tree = ET.parse(dix_path)
root = tree.getroot()

words = set()
for e in root.iter('e'):
    # lm attribute holds the lemma
    lm = (e.get('lm') or '').strip()
    if is_target_script(lm):
        words.add(lm)
    # <i> elements hold invariant (uninflected) surface forms
    for i in e.iter('i'):
        if i.text and is_target_script(i.text.strip()):
            words.add(i.text.strip())
    # <l> elements hold the left (surface) side of a pair
    for l in e.iter('l'):
        text = ''.join(l.itertext()).strip()
        if is_target_script(text):
            words.add(text)

words = sorted(words, key=len)
grouped = [list(g) for _, g in groupby(words, key=len)]

with open(out_path, 'w') as f:
    for group in grouped:
        f.write(f"!!!!!{len(group[0])}\n")
        for word in group:
            f.write(word + '\n')

print(f"Wrote {len(words)} words to {out_path}")
