# titlecase notes

Notes on the default behavior of `titlecase()` in the Python package at `../python-titlecase`. Each example below was run against that function.

- Package version: 2.4.1 (`titlecase.__version__`)
- License: The MIT License (MIT), copyright (c) 2021 Patrick William Pannuto (`LICENSE.txt`)
- Repository: https://github.com/ppannuto/python-titlecase
- Commit SHA: `42f43e2de55bf003b286c6f8e8d8b2d26676a167`
- Commit date: 2024-04-05 22:03:59 -0700
- Inspected: 2026-11-06

Calls below use the default arguments (`callback=None`, `small_first_last=True`, `preserve_blank_lines=False`, `normalise_space_characters=False`) unless a flag is named. The text is split into lines, and each line is split into words on whitespace. An earlier matching rule skips the later word rules.

## Small words and first or last word

A word that is exactly a small word is lowercased. The small words are `a`, `an`, `and`, `as`, `at`, `but`, `by`, `en`, `for`, `if`, `in`, `of`, `on`, `or`, `the`, `to`, `v`, `v.`, `via`, `vs`, and `vs.`. Matching is case-insensitive. Words that are not on this list are not treated as small, including `is`.

After the other word rules, a small word that is the first word of the line is capitalized, including when punctuation stands immediately before it. A small word that is the last word of the line is capitalized, including when one punctuation character follows it. A one-word line is both first and last, so a small word there is capitalized.

- `this is a test` → `This Is a Test`
- `this v that` → `This v That`
- `this vs. that` → `This vs. That`
- `a thing` → `A Thing`
- `Small word at end is nothing to be afraid of` → `Small Word at End Is Nothing to Be Afraid Of`
- `'by the Way, small word at the start but within quotes.'` → `'By the Way, Small Word at the Start but Within Quotes.'`
- `the` → `The`

Exceptions:

- A small word in the middle stays lowercase. `yes, a thing` → `Yes, a Thing`. A comma does not by itself capitalize the following small word.
- Punctuation stuck to a small word means it is no longer exactly a small word, so the lowercase-small-word step does not apply. `word of.` → `Word Of.`
- Leading or trailing whitespace creates empty word slots. Those slots occupy the first and last positions, so the visible word is not capitalized as a first or last word. `  the end` → `  the End`, and `  a  test  ` → `  a  Test  `.
- Inside a slash- or hyphen-separated piece, this first and last capitalization is turned off. It can still apply to the joined word when that word itself is first or last on the line. See the slash and hyphen sections.
- On a line that is not entirely uppercase, a first word that merely begins with a small word is rewritten at the boundary. `AT&T and Q&A` → `At&T and Q&A`.

## All-uppercase input and initials

A line is all uppercase when `line.upper() == line`. Digits and punctuation do not stop a line from qualifying. On such a line, a word that is initials is kept unchanged. Initials are one or more groups of an uppercase letter plus a period (`D.C.`, `U.S.A.`) or an uppercase letter, a period, and another uppercase letter (`A.B`).

Every other word on an all-uppercase line is lowercased before the remaining capitalization rules, so a shouted sentence becomes title case. A mixed-case line is not lowercased as a whole, so an already uppercase word on that line can stay uppercase.

- `THIS IS ALL CAPS AND SHOULD BE ADDRESSED` → `This Is All Caps and Should Be Addressed`
- `WASHINGTON, D.C. SHOULD BE FIXED BUT MIGHT BE A PROBLEM` → `Washington, D.C. Should Be Fixed but Might Be a Problem`
- `D.C.` → `D.C.`
- `A.B` → `A.B`
- `this is a TEST` → `This Is a TEST`

Exceptions:

- Two letters before a period are not initials. `ST. LOUIS` → `St. Louis`.
- An all-uppercase word that contains a vowel is lowercased and then title-cased. It is not preserved just because it looks like an acronym. `USA IS ALL CAPS` → `Usa Is All Caps`.
- A bare `MC` is not initials and is not handled by the Mc rule. The all-uppercase path produces `Mc`.

## Apostrophe handling

A whole word that starts with `d`, `o`, or `l`, then a straight apostrophe (`'`) or a left single quotation mark (`‘`, U+2018), then one or more letters, is rewritten and the later word rules are skipped. An optional two-character ending made of `'` and `s` is allowed, which covers a possessive `'s`.

`d` and `l` are consonants here and are forced lowercase. `o` is a vowel and is forced uppercase. The letter immediately after the apostrophe is capitalized. The rest of the word is left as it was, so an all-uppercase tail stays uppercase.

- `l'grange` → `l'Grange`
- `d'angelo` → `d'Angelo`
- `o'grange` → `O'Grange`
- `o'grange's` → `O'Grange's`
- `l‘grange` → `l‘Grange`
- `L'Grange` → `l'Grange`
- `L'GRANGE` → `l'GRANGE`
- `d'Artagnan` → `d'Artagnan`

Exceptions:

- Any other first letter does not use this rule. Only the first letter is capitalized, and the tail is unchanged. `n'grange` → `N'grange`, and `it's a test` → `It's a Test`.
- The word must match this shape completely. `O'BRIEN` → `O'BRIEN` because the tail is preserved, not because the whole word was title-cased.

## Mc-name handling

A word that starts with `Mc`, `mc`, or `MC`, followed by at least two more word characters, becomes `Mc` plus the title-cased remainder. `MC` is normalized by capitalizing that prefix, so it also becomes `Mc`. The remainder is passed through `titlecase` on its own.

- `mcclelland` → `McClelland`
- `mcdonald` → `McDonald`
- `McCLELLAND` → `McClelland`

Exceptions:

- Fewer than two characters after the prefix do not match. `McA` → `McA` through the mixed-case rule below, and a bare `MC` → `Mc` only through the all-uppercase path.
- A word that does not start with that prefix is an ordinary word. `macintosh` → `Macintosh`.
- A name that already has a capital later in the word can be left untouched by the mixed-case rule when this pattern does not fire, and when it does fire the remainder is still title-cased. `McDonald` → `McDonald`.

## Mr, Mrs, Ms, and Dr

A word that is entirely `Mr`, `Mrs`, `Ms`, or `Dr`, in any capitalization and with no period, keeps an uppercase first letter and leaves every following character as it was. Later word rules are skipped.

- `dr` → `Dr`
- `mrs` → `Mrs`
- `ms` → `Ms`
- `Mr Smith and Ms Jones and Mrs Peel and Dr Who` → `Mr Smith and Ms Jones and Mrs Peel and Dr Who`

Exceptions:

- The remainder is not rewritten into a canonical spelling. `DR` → `DR`, `MRS` → `MRS`, `mRs` → `MRs`, and `mR` → `MR`.
- A period means this rule does not match. `Dr.` → `Dr.`. On an all-uppercase line, `DR. SMITH` → `Dr. Smith` because `DR.` is lowercased and then given a capital first letter, not because the honorific rule matched.
- Longer words such as `mister` do not match.

## Existing mixed case and inline periods

On a line that is not entirely uppercase, a word that already contains an uppercase letter after its opening letters is left unchanged. Leading punctuation is allowed before those letters. This keeps brand names, internal capitals, and an already uppercase word on a mixed line.

Separately, a word that contains a letter, a period, and another letter is left unchanged on every line, including an all-uppercase line. That covers hostnames and dotted abbreviations.

- `iTunes should be unmolested` → `iTunes Should Be Unmolested`
- `iPhone and iTunes` → `iPhone and iTunes`
- `already MixedCase stays` → `Already MixedCase Stays`
- `this is a TEST` → `This Is a TEST`
- `the CNN news` → `The CNN News`
- `this is just an example.com` → `This Is Just an example.com`
- `e.g. this` → `e.g. This`
- `Q&A session` → `Q&A Session`
- `keep D.C. please` → `Keep D.C. Please`

Exceptions:

- The mixed-case check does not run on an all-uppercase line. Those words are lowercased unless an earlier rule, such as initials, kept them.
- If a preserved word is the first or last word, the small-word pass can still rewrite a small word at its edge. `a.b.c` → `A.b.c`, while a middle token such as `example.com` in `this is just an example.com` stays fully unchanged.
- An inline period anywhere in the word also prevents the later hyphen split. `non-u.s. thing` → `non-u.s. Thing`.

## Slash-separated and hyphen-separated words

If a word contains `/` and does not contain `//`, each piece is title-cased on its own and the pieces are joined with `/`. First and last small-word capitalization is off inside each piece.

If a word contains an ASCII `-`, and an earlier rule did not already keep it, each piece is title-cased the same way and joined with `-`. A small word in the middle stays lowercase.

- `word/word` → `Word/Word`
- `end-to-end` → `End-to-End`
- `end-to-end test` → `End-to-End Test`
- `state-of-the-art` → `State-of-the-Art`
- `rock-and-roll` → `Rock-and-Roll`
- `word-of-mouth` → `Word-of-Mouth`

Exceptions:

- `//` blocks the slash split, and only the first letter of the whole token is capitalized. `foo//bar` → `Foo//bar`. `this is http://foo.com` → `This Is http://foo.com` (the token is also kept because of the inline period).
- A spaced slash is three separate words, not one split token. `foo / bar` → `Foo / Bar`.
- Only the ASCII hyphen splits a word. An em dash does not. `well—known` → `Well—known`.
- Small pieces stay small only while they are inside the split. If the joined token is the first or last word of the line, that pass runs on the joined token. `this and/or that` → `This and/or That`, `and/or else` → `And/or Else`, `and/or` → `And/Or`, and `of-the` → `Of-The`.
- Each piece is a full `titlecase` call, so a short all-uppercase piece is not always an acronym. `TCP/IP` → `TCP/Ip`.

## All-consonant acronyms

After an all-uppercase word has been lowercased, a word of more than two characters made only of consonants is written in full capitals. The vowels for this test are `a`, `e`, `i`, `o`, `u`, and `y`. Every other ASCII letter is a consonant. The word may not contain punctuation or digits.

- `Words with all consonants like cnn are acronyms` → `Words With All Consonants Like CNN Are Acronyms`
- `cnn` → `CNN`
- `fwd this` → `FWD This`
- `HTML and css` → `HTML and CSS`
- `my nth try` → `My NTH Try`
- `I LOVE TCP` → `I Love TCP`
- `www` → `WWW`

Exceptions:

- Length of two or less does not qualify. `st marks` → `St Marks`, and `St` → `St`.
- `y` is treated as a vowel, so it blocks the rule. `YYY` → `Yyy`, and `rhythm and blues` → `Rhythm and Blues`.
- A vowel blocks the rule even when the line was all uppercase. `USA IS ALL CAPS` → `Usa Is All Caps`, and `III` → `Iii`.
- Small words are handled earlier, so `by` does not become `BY`.
- On a mixed-case line, an already uppercase word is usually kept by the mixed-case rule before this test. `the CNN news` → `The CNN News`.

## Capitalization after punctuation

If no earlier rule claimed the word, the first letter is capitalized and the rest of the word is unchanged. Punctuation before that letter stays in place. A leading digit is not a letter, so a word such as `2nd` is unchanged.

After the line is joined, a small word that follows a subphrase marker and a space is capitalized. The markers are `:`, `;`, `.`, `?`, `!`, and the dashes `-`, `–`, `‒`, `—`, and `―`.

- `a "quoted" word` → `A "Quoted" Word`
- `(this is a test)` → `(This Is a Test)`
- `"a quote"` → `"A Quote"`
- `2nd place` → `2nd Place`
- `rock 'n' roll` → `Rock 'N' Roll`
- `Starting Sub-Phrase With a Small Word: a Trick, Perhaps?` → `Starting Sub-Phrase With a Small Word: A Trick, Perhaps?`
- `Question? a small word.` → `Question? A Small Word.`
- `Wait! a bird` → `Wait! A Bird`
- `one; a two` → `One; A Two`
- `dash - a thing` → `Dash - A Thing`
- `Hello: a start` → `Hello: A Start`
- `colon: a` → `Colon: A`
- `end — a dash` → `End — A Dash`

Exceptions:

- The marker must be followed by a space. `no-space:a thing` → `No-Space:a Thing`.
- A comma is not a marker. `yes, a thing` → `Yes, a Thing`.
- This pass capitalizes a small word after a period even when the period belongs to the previous word. `see of. the cat` → `See Of. The Cat`.
- A new line is a separate line, not a subphrase space. `one.\na two` → `One.\nA Two` because `a` is the first word of the second line.

## Whitespace and blank lines

Whitespace between words is preserved by default, including repeated spaces and tabs. Leading and trailing whitespace is preserved. As described above, that whitespace also inserts empty first or last word slots.

Lines are split on a run of `\r` or `\n`. Consecutive breaks collapse, so a blank line is dropped. A Windows `\r\n` pair is one break. The lines are joined again with `\n` only. A trailing break remains one trailing newline. `hello\n\n` and `hello\n` both end as one trailing newline.

- `text\twith\ttabs` → `Text\tWith\tTabs`
- `many   spaces here` → `Many   Spaces Here`
- `  leading space` → `  Leading Space`
- `trailing space  ` → `Trailing Space  `
- Input `Line number one\n\nand Line three\n` → `Line Number One\nAnd Line Three\n`
- `one\r\ntwo\r\n\r\nthree` → `One\nTwo\nThree`
- `one\n` → `One\n`

Exceptions:

- `preserve_blank_lines=True` splits on every individual `\r` or `\n`, so a blank line stays. The same input `Line number one\n\nand Line three\n` → `Line Number One\n\nAnd Line Three\n`. Because `\r` and `\n` are separate breaks, `one\r\ntwo` → `One\n\nTwo`.
- `normalise_space_characters=True` joins the word pieces with a single ordinary space. A tab becomes a space: `text\twith\ttabs` → `Text With Tabs`. Repeated spaces still produce empty pieces, so they remain: `many   spaces here` → `Many   Spaces Here`.



## Final observations

**1. Which rules did the agent get wrong most?**

The most challenging rules involved small-word capitalization, mixed-case preservation, acronyms, hyphenated words, and punctuation handling.

**2. What would you add to make the task harder?**

I would add more hidden test cases involving Unicode characters, unusual punctuation, whitespace variations, and combinations of capitalization rules.