#!/usr/bin/env python3
"""Generate visible and hidden titlecase cases from the Python oracle.

Run from the task root:

    python tests/gen.py

Each output file is JSON Lines. Line i is one JSON string. Line i of an
inputs file pairs with line i of the matching expected file. Expected
strings are titlecase(input) with default arguments.
"""

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE_ROOT = ROOT.parent / "python-titlecase"
sys.path.insert(0, str(ORACLE_ROOT))

from titlecase import titlecase  # noqa: E402

CASES_PER_SPLIT = 2000
EDGE_PER_SPLIT = 1000
ORDINARY_PER_SPLIT = 1000

DATA_DIR = ROOT / "tests" / "data"

CONTENT = [
    "garden", "river", "bridge", "market", "castle", "forest", "ocean",
    "history", "science", "music", "winter", "summer", "secret", "golden",
    "silver", "quiet", "final", "lost", "ancient", "modern", "public",
    "private", "northern", "southern", "little", "great", "red", "blue",
    "green", "black", "white", "city", "village", "island", "valley",
    "mountain", "captain", "letter", "journey", "return", "shadow",
    "light", "story", "report", "guide", "notes", "chapter", "volume",
    "harbor", "compass", "lantern", "meadow", "orchard", "portrait",
    "voyage", "window", "yellow", "copper", "marble", "thunder",
]

SMALL = [
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
    "of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.",
]

# Inputs only. Expected text is computed with titlecase().
CURATED = [
    "this is a test",
    "this v that",
    "this v. that",
    "this vs that",
    "this vs. that",
    "a thing",
    "Small word at end is nothing to be afraid of",
    "'by the Way, small word at the start but within quotes.'",
    "the",
    "of",
    "yes, a thing",
    "word of.",
    "  the end",
    "  a  test  ",
    "the end  ",
    "AT&T and Q&A",
    "AT&T",
    "Q&A",
    "THIS IS ALL CAPS AND SHOULD BE ADDRESSED",
    "WASHINGTON, D.C. SHOULD BE FIXED BUT MIGHT BE A PROBLEM",
    "D.C.",
    "A.B",
    "U.S.A.",
    "this is a TEST",
    "ST. LOUIS",
    "USA IS ALL CAPS",
    "MC",
    "l'grange",
    "d'angelo",
    "o'grange",
    "o'grange's",
    "l\u2018grange",
    "L'Grange",
    "L'GRANGE",
    "d'Artagnan",
    "n'grange",
    "it's a test",
    "O'BRIEN",
    "o'brien",
    "o'clock",
    "mcclelland",
    "mcdonald",
    "McCLELLAND",
    "McA",
    "macintosh",
    "McDonald",
    "dr",
    "mrs",
    "ms",
    "Mr",
    "DR",
    "MRS",
    "mRs",
    "mR",
    "Dr.",
    "DR. SMITH",
    "Mr Smith and Ms Jones and Mrs Peel and Dr Who",
    "iTunes should be unmolested",
    "iPhone and iTunes",
    "already MixedCase stays",
    "the CNN news",
    "this is just an example.com",
    "e.g. this",
    "Q&A session",
    "keep D.C. please",
    "a.b.c",
    "non-u.s. thing",
    "example.com",
    "word/word",
    "end-to-end",
    "end-to-end test",
    "state-of-the-art",
    "rock-and-roll",
    "word-of-mouth",
    "foo//bar",
    "this is http://foo.com",
    "foo / bar",
    "well\u2014known",
    "this and/or that",
    "and/or else",
    "and/or",
    "of-the",
    "TCP/IP",
    "Words with all consonants like cnn are acronyms",
    "cnn",
    "fwd this",
    "HTML and css",
    "my nth try",
    "I LOVE TCP",
    "www",
    "st marks",
    "St",
    "YYY",
    "rhythm and blues",
    "III",
    "by",
    "a \"quoted\" word",
    "(this is a test)",
    '"a quote"',
    "2nd place",
    "rock 'n' roll",
    "Starting Sub-Phrase With a Small Word: a Trick, Perhaps?",
    "Question? a small word.",
    "Wait! a bird",
    "one; a two",
    "dash - a thing",
    "Hello: a start",
    "colon: a",
    "no-space:a thing",
    "see of. the cat",
    "",
    "end \u2014 a dash",
    "end \u2013 a dash",
    "end \u2015 a dash",
    "end \u2012 a dash",
    "text\twith\ttabs",
    "many   spaces here",
    "  leading space",
    "trailing space  ",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]


def dedupe(items):
    seen = set()
    unique = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def pick(options):
    return random.choice(options)


def content_word():
    word = pick(CONTENT)
    roll = random.random()
    if roll < 0.15:
        return word.upper()
    if roll < 0.30:
        return word.capitalize()
    return word


def ordinary_phrase():
    count = random.randint(2, 10)
    words = []
    for index in range(count):
        at_edge = index == 0 or index == count - 1
        if at_edge or random.random() < 0.6:
            words.append(content_word())
        else:
            words.append(pick(SMALL))
    return " ".join(words)


def apply_line_case(text):
    mode = random.randrange(4)
    if mode == 0:
        return text.lower()
    if mode == 1:
        return text.upper()
    if mode == 2:
        return " ".join(part.capitalize() for part in text.split(" "))
    return text


def ordinary_case():
    text = apply_line_case(ordinary_phrase())
    roll = random.random()
    if roll < 0.12:
        return f'"{text}"'
    if roll < 0.22:
        return f"({text})"
    if roll < 0.30:
        return f"'{text}'"
    return text


def all_upper_case():
    return ordinary_phrase().upper()


def initials_case():
    groups = []
    for _ in range(random.randint(2, 4)):
        letter = pick("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if random.random() < 0.7:
            groups.append(letter + ".")
        else:
            groups.append(letter + "." + pick("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    token = "".join(groups)
    if random.random() < 0.5:
        return f"{pick(CONTENT).upper()} {token} SHOULD BE FIXED"
    return f"keep {token} please"


def apostrophe_case():
    first = pick("dolDOL")
    mark = pick(["'", "\u2018"])
    tail = pick(["grange", "angelo", "brien", "clock", "artagnan", "neil", "souza", "hare"])
    word = first + mark + tail
    if random.random() < 0.35:
        word += "'s"
    if random.random() < 0.25:
        word = word.upper()
    if random.random() < 0.2:
        word = pick("nits") + "'" + tail
    return f"{word} {content_word()}"


def mc_case():
    prefix = pick(["mc", "Mc", "MC"])
    length = random.randint(2, 8)
    tail = "".join(pick("abcdefghijklmnopqrstuvwxyz") for _ in range(length))
    if random.random() < 0.3:
        tail = tail.upper()
    word = prefix + tail
    if random.random() < 0.15:
        word = prefix + pick("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{word} and {pick(['dr', 'mrs', 'ms', 'Dr'])} {content_word()}"


def honorific_case():
    title = pick(["mr", "mrs", "ms", "dr", "MR", "MRS", "MS", "DR", "mRs", "mR", "Dr", "Mr"])
    if random.random() < 0.25:
        title += "."
    sentence = f"{title} {content_word()} {pick(SMALL)} {content_word()}"
    if random.random() < 0.35:
        return sentence.upper()
    return sentence


def mixed_case_case():
    brand = pick(["iTunes", "iPhone", "eBay", "YouTube", "MixedCase", "MacBook", "IPv6"])
    shouted = pick(CONTENT).upper()
    return f"{pick(SMALL)} {brand} and {shouted} {content_word()}"


def inline_period_case():
    kind = random.randrange(4)
    if kind == 0:
        token = f"{pick(CONTENT)}.com"
    elif kind == 1:
        token = "e.g."
    elif kind == 2:
        letters = [pick("abcdefghijklmnopqrstuvwxyz") for _ in range(random.randint(2, 4))]
        token = ".".join(letters)
    else:
        token = f"http://{pick(CONTENT)}.com"
    return f"{pick(SMALL)} {token} {content_word()}"


def slash_case():
    kind = random.randrange(4)
    if kind == 0:
        token = f"{content_word()}/{content_word()}"
    elif kind == 1:
        token = f"{pick(SMALL)}/{pick(SMALL)}"
    elif kind == 2:
        token = f"{pick(CONTENT)}//{pick(CONTENT)}"
    else:
        left = "".join(pick("BCDFGHJKLMNPQRSTVWXZ") for _ in range(random.randint(3, 4)))
        right = pick(["IP", "US", "AI", "OK", pick(CONTENT).upper()])
        token = f"{left}/{right}"
    if random.random() < 0.5:
        return f"{content_word()} {token} {content_word()}"
    return token


def hyphen_case():
    kind = random.randrange(4)
    if kind == 0:
        token = f"{content_word()}-{pick(SMALL)}-{content_word()}"
    elif kind == 1:
        token = f"{content_word()}-{pick(SMALL)}-{pick(SMALL)}-{content_word()}"
    elif kind == 2:
        dash = pick(["\u2014", "\u2013", "\u2012", "\u2015"])
        token = f"{content_word()}{dash}{content_word()}"
    else:
        token = "-".join(content_word() for _ in range(random.randint(2, 4)))
    if random.random() < 0.4:
        return token
    return f"{content_word()} {token} {pick(SMALL)} {content_word()}"


def acronym_case():
    kind = random.randrange(4)
    if kind == 0:
        letters = "bcdfghjklmnpqrstvwxz"
        token = "".join(pick(letters) for _ in range(random.randint(3, 6)))
    elif kind == 1:
        token = "".join(pick("bcdfghjklmnpqrstvwxz") for _ in range(2))
    elif kind == 2:
        token = "".join(pick("yyyiii") for _ in range(random.randint(3, 5)))
    else:
        token = pick(["cnn", "tcp", "html", "css", "www", "nth", "fwd", "usa", "st", "psst"])
    if random.random() < 0.4:
        token = token.upper()
    return f"{content_word()} {pick(SMALL)} {token} {content_word()}"


def punctuation_case():
    marker = pick([": ", "; ", ". ", "? ", "! ", " - ", " \u2014 ", " \u2013 ", " \u2012 ", " \u2015 "])
    if random.random() < 0.2:
        marker = pick([":", ";"])
    left = content_word()
    small = pick(SMALL)
    right = content_word()
    text = f"{left}{marker}{small} {right}"
    if random.random() < 0.3:
        text = f'"{text}"'
    return text


def whitespace_case():
    words = []
    for _ in range(random.randint(2, 6)):
        words.append(pick(SMALL) if random.random() < 0.4 else content_word())
    separator = pick(["  ", "\t", " \t ", "   "])
    text = separator.join(words)
    edge = random.randrange(4)
    if edge == 0:
        return "  " + text
    if edge == 1:
        return text + "  "
    if edge == 2:
        return "\t" + text + " "
    return text


def blank_line_case():
    separator = pick(["  ", "   ", "\t", " \t "])
    return ordinary_phrase() + separator + ordinary_phrase()


EDGE_BUILDERS = [
    all_upper_case,
    initials_case,
    apostrophe_case,
    mc_case,
    honorific_case,
    mixed_case_case,
    inline_period_case,
    slash_case,
    hyphen_case,
    acronym_case,
    punctuation_case,
    whitespace_case,
    blank_line_case,
]


def edge_case():
    return pick(EDGE_BUILDERS)()


def fill(factory, count, blocked):
    created = []
    tries = 0
    limit = max(count * 1000, 1000)
    while len(created) < count:
        tries += 1
        if tries > limit:
            raise RuntimeError(f"stopped after {tries} tries with {len(created)} cases")
        item = factory()
        if item in blocked:
            continue
        blocked.add(item)
        created.append(item)
    return created


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def expected_for(inputs):
    return [titlecase(text) for text in inputs]


def main():
    random.seed(1)
    curated = dedupe(CURATED)
    visible_curated = curated[0::2]
    hidden_curated = curated[1::2]
    if len(visible_curated) > EDGE_PER_SPLIT or len(hidden_curated) > EDGE_PER_SPLIT:
        raise RuntimeError("curated edge cases exceed the edge-case budget")

    blocked = set(curated)
    visible = list(visible_curated)
    visible.extend(fill(edge_case, EDGE_PER_SPLIT - len(visible), blocked))
    visible.extend(fill(ordinary_case, ORDINARY_PER_SPLIT, blocked))

    hidden = list(hidden_curated)
    hidden.extend(fill(edge_case, EDGE_PER_SPLIT - len(hidden), blocked))
    hidden.extend(fill(ordinary_case, ORDINARY_PER_SPLIT, blocked))

    random.shuffle(visible)
    random.shuffle(hidden)

    if len(visible) != CASES_PER_SPLIT or len(hidden) != CASES_PER_SPLIT:
        raise RuntimeError("unexpected case count")
    if set(visible) & set(hidden):
        raise RuntimeError("visible and hidden inputs overlap")
    if len(set(visible)) != CASES_PER_SPLIT or len(set(hidden)) != CASES_PER_SPLIT:
        raise RuntimeError("duplicate inputs within a split")

    visible_expected = expected_for(visible)
    hidden_expected = expected_for(hidden)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "visible_inputs.jsonl": visible,
        "visible_expected.jsonl": visible_expected,
        "hidden_inputs.jsonl": hidden,
        "hidden_expected.jsonl": hidden_expected,
    }
    for name, rows in files.items():
        write_jsonl(DATA_DIR / name, rows)

    for name, rows in files.items():
        print(f"{DATA_DIR / name}: {len(rows)}")


if __name__ == "__main__":
    main()
