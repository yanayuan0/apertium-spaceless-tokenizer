# apertium-spaceless-tokenizer

A fast, general-purpose tokenizer for spaceless orthographies — written languages
that do not use spaces between words, such as Mandarin Chinese, Wu Chinese
(Shanghainese), Japanese, and Thai.

This tool is designed as a drop-in replacement for the Python-based tokenizer
used in [Apertium](https://apertium.org) language packages. It is approximately
**100× faster** and produces identical output.

## Background

Languages like Mandarin write sentences without spaces:

    中国人民站起来了

A tokenizer must decide where word boundaries are:

    中国 人民 站 起来 了

This is called **word segmentation**. The algorithm used here is
**Left-to-Right Longest Match (LRLM)**: starting from the left, always take
the longest known word that fits, then continue from where it ended.

The word inventory — the list of all valid words — is extracted from the
language's Apertium morphological analyzer. This makes the tokenizer
language-agnostic: it works for any language that has an Apertium package.

## Requirements

- A C++17 compiler (`g++` or `clang++`)
- Python 3 (for the word-list generation scripts)
- `hfst` tools (for `.hfst`-based languages like Wu Chinese)
  — install from [hfst.github.io](https://hfst.github.io) or build from source

## Building

```bash
make
```

This produces a single binary: `./tokeniser`.

## Usage

### Step 1: Generate a word list for your language

**If your language package uses `.hfst` (e.g. Wu Chinese, many newer packages):**

```bash
# Build the autotok transducer from your language package first:
#   cd /path/to/apertium-wuu && make wuu.autotok.hfst
python3 autotok_scraper.py /path/to/wuu.autotok.hfst
# → writes wuu_autotok_scraped.txt
```

**If your language package uses `.dix` (e.g. Mandarin `apertium-zho`):**

```bash
python3 dix_scraper.py /path/to/apertium-zho.zho.dix
# → writes zho_autotok_scraped.txt
```

### Step 2: Run the tokenizer

```bash
echo "中国人民站起来了" | ./tokeniser zho_autotok_scraped.txt
# Output:  中国 人民 站 起来 了
```

The tokenizer reads from stdin and writes to stdout. Non-target-script characters
(punctuation, numbers, Latin text) pass through unchanged.

### Step 3: Plug into an Apertium pipeline

The output format matches what `lt-proc -w` expects:

```bash
echo "中国人民站起来了" | ./tokeniser zho_autotok_scraped.txt | lt-proc -w zho.automorf.bin
# Output: ^中国/中国<np>$ ^人民/人民<n>$ ^站/站<n>$ ^起来/起来<vblex>$ ^了/了<pr>$
```

In `modes.xml`, replace the Python tokenizer step:

```xml
<!-- Before (slow) -->
<program name="python3">
  <file name="tokeniser.py"/>
  <file name="wuu.autotok.hfst"/>
</program>

<!-- After (fast) -->
<program name="./tokeniser">
  <file name="wuu_autotok_scraped.txt"/>
</program>
```

## Evaluation

Gold-standard test sets are in the `eval/` directory. To evaluate:

```bash
# Wuu Chinese
python3 -c "
lines = open('eval/gold_wuu.txt').readlines()
for l in lines: print(''.join(l.split()))
" | ./tokeniser wuu_autotok_scraped.txt | python3 eval/evaluate.py eval/gold_wuu.txt

# Mandarin
python3 -c "
lines = open('eval/gold_zho.txt').readlines()
for l in lines: print(''.join(l.split()))
" | ./tokeniser zho_autotok_scraped.txt | python3 eval/evaluate.py eval/gold_zho.txt
```

### Results

| Language | Sentences | Precision | Recall | F1 |
|----------|-----------|-----------|--------|----|
| Wu Chinese (Wuu) | 10 | 1.000 | 1.000 | 1.000 |
| Mandarin (Zho) | 10 | 1.000 | 1.000 | 1.000 |

### Speed comparison

On 500 lines of Wu Chinese input:

| Tokenizer | Time | Relative speed |
|-----------|------|----------------|
| Python (`tokeniser.py` + HFST) | 0.39s | 1× |
| C++ (`tokeniser` + word list) | 0.004s | ~100× faster |

## How it works

1. **Word list loading**: at startup, all words from the word list file are
   loaded into a hash set. Each individual character from every word is also
   stored in a character set (the "alphabet"), so the tokenizer knows which
   characters belong to the target script.

2. **Stream processing**: input is read line by line. Consecutive in-alphabet
   characters are grouped into a chunk; non-alphabet characters (punctuation,
   spaces, digits) are passed through unchanged.

3. **LRLM segmentation**: each chunk of target-script characters is segmented
   using Left-to-Right Longest Match — at each position, try the longest
   possible word first, decreasing until a known word is found. Unknown
   single characters are emitted as-is.

## Supported languages (tested)

| Language | Script | Word list source |
|----------|--------|-----------------|
| Wu Chinese (Wuu) | CJK | `autotok_scraper.py` + `.hfst` |
| Mandarin (Zho) | CJK | `dix_scraper.py` + `.dix` |

Any other Apertium language package with a spaceless script should work
by following the same steps.

## Files

| File | Description |
|------|-------------|
| `tokeniser.cpp` | The tokenizer — build with `make` |
| `autotok_scraper.py` | Generates word list from `.autotok.hfst` |
| `dix_scraper.py` | Generates word list from `.dix` dictionary |
| `Makefile` | Build rule |
| `eval/evaluate.py` | Computes precision/recall/F1 vs. gold standard |
| `eval/gold_wuu.txt` | Hand-annotated Wu Chinese test sentences |
| `eval/gold_zho.txt` | Hand-annotated Mandarin test sentences |
# apertium-spaceless-tokenizer
