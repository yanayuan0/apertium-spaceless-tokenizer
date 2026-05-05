#!/usr/bin/env python3
"""
Evaluate tokenizer output against a gold-standard file.

Gold file format (one sentence per line, tokens separated by spaces):
    吃脱 好 辰光
    伊 老 讲 吃脱 好 辰光

Usage:
    # Run tokenizer and evaluate
    ./tokeniser <wordlist.txt> < eval/gold_wuu.txt | python3 eval/evaluate.py eval/gold_wuu.txt

    # Or compare two tokenizer outputs directly
    python3 eval/evaluate.py eval/gold_wuu.txt tokenizer_output.txt
"""

import sys

def load_gold(path):
    """Load gold file: list of lists of tokens."""
    with open(path) as f:
        return [line.strip().split() for line in f if line.strip()]

def load_output(source):
    """
    Load tokenizer output from a file path or stdin.
    Tokenizer output format: " tok1 tok2 tok3 " (leading/trailing spaces, space-delimited).
    """
    if source == '-':
        lines = sys.stdin.read().splitlines()
    else:
        with open(source) as f:
            lines = f.read().splitlines()
    return [line.strip().split() for line in lines if line.strip()]

def boundaries(tokens):
    """Convert token list to a set of (start, end) character-index pairs."""
    spans = set()
    pos = 0
    for tok in tokens:
        end = pos + len(tok)
        spans.add((pos, end))
        pos = end
    return spans

def evaluate(gold_sentences, pred_sentences):
    if len(gold_sentences) != len(pred_sentences):
        print(f"Warning: gold has {len(gold_sentences)} lines, output has {len(pred_sentences)} lines.")
        n = min(len(gold_sentences), len(pred_sentences))
        gold_sentences = gold_sentences[:n]
        pred_sentences = pred_sentences[:n]

    tp = fp = fn = 0
    errors = []

    for i, (gold, pred) in enumerate(zip(gold_sentences, pred_sentences)):
        gold_b = boundaries(gold)
        pred_b = boundaries(pred)
        tp += len(gold_b & pred_b)
        fp += len(pred_b - gold_b)
        fn += len(gold_b - pred_b)

        if gold != pred:
            errors.append((i + 1, ' '.join(gold), ' '.join(pred)))

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall    = tp / (tp + fn) if (tp + fn) else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print(f"Sentences evaluated : {len(gold_sentences)}")
    print(f"Precision           : {precision:.3f}")
    print(f"Recall              : {recall:.3f}")
    print(f"F1                  : {f1:.3f}")

    if errors:
        print(f"\nMismatches ({len(errors)}):")
        for lineno, g, p in errors[:10]:
            print(f"  Line {lineno}")
            print(f"    Gold : {g}")
            print(f"    Pred : {p}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    gold = load_gold(sys.argv[1])
    pred_source = sys.argv[2] if len(sys.argv) > 2 else '-'
    pred = load_output(pred_source)
    evaluate(gold, pred)
