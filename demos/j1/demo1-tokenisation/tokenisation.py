# /// script
# requires-python = ">=3.10"
# dependencies = ["tiktoken>=0.7"]
# ///
"""Tokenisation d'une phrase passee en argument.

Usage :
    uv run script.py "La phrase a tokeniser"
    uv run script.py --enc o200k_base "La phrase a tokeniser"
"""

import argparse

import tiktoken


def main():
    p = argparse.ArgumentParser(description="Tokenise une phrase avec tiktoken.")
    p.add_argument("texte", nargs="+", help="la phrase a tokeniser")
    p.add_argument(
        "--enc",
        default="cl100k_base",
        help="encodage tiktoken (cl100k_base, o200k_base, ...)",
    )
    args = p.parse_args()

    texte = " ".join(args.texte)
    enc = tiktoken.get_encoding(args.enc)
    ids = enc.encode(texte)

    print("Texte      : %s" % texte)
    print("Encodage   : %s" % args.enc)
    print("Caracteres : %d" % len(texte))
    print("Tokens     : %d" % len(ids))
    print()
    print("  %-4s %-9s %s" % ("rang", "id", "morceau"))
    for rang, tid in enumerate(ids):
        print("  %-4d %-9d %r" % (rang, tid, enc.decode([tid])))
    print()
    print("  " + " | ".join(enc.decode([t]) for t in ids))


if __name__ == "__main__":
    main()
