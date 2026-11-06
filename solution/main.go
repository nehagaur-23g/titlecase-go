package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"unicode"
)

// smallFixed is the Python small-word alternation, in source order,
// excluding the v/vs patterns that can swallow a following dot.
var smallFixed = []string{
	"a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
	"of", "on", "or", "the", "to",
}

func main() {
	in := bufio.NewScanner(os.Stdin)
	in.Buffer(make([]byte, 64*1024), 10*1024*1024)
	out := bufio.NewWriter(os.Stdout)
	for in.Scan() {
		// Each physical line is one title. The scanner has already removed the
		// line break, so the result is exactly one output line.
		fmt.Fprintln(out, titlecaseLine(in.Text(), true))
	}
	if err := out.Flush(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := in.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

// titlecase mirrors titlecase() from the Python package with its default
// callback, preserve_blank_lines, and normalise_space_characters arguments.
// smallFirstLast is false for pieces inside a slash or hyphen split.
func titlecase(text string, smallFirstLast bool) string {
	lines := splitBreaks(text)
	out := make([]string, len(lines))
	for i, line := range lines {
		out[i] = titlecaseLine(line, smallFirstLast)
	}
	return strings.Join(out, "\n")
}

func titlecaseLine(line string, smallFirstLast bool) string {
	allCaps := pyUpper(line) == line
	words, spaces := splitSpaces(line)
	tc := make([]string, len(words))
	for i, word := range words {
		tc[i] = processWord(word, allCaps)
	}
	if smallFirstLast && len(tc) > 0 {
		tc[0] = applySmallFirst(tc[0])
		tc[len(tc)-1] = applySmallLast(tc[len(tc)-1])
	}
	return applySubphrase(joinWords(tc, spaces))
}

func processWord(word string, allCaps bool) string {
	if allCaps && isInitials(word) {
		return word
	}
	if rewritten, ok := rewriteApostrophe(word); ok {
		return rewritten
	}
	if prefix, rest, ok := splitMac(word); ok {
		return pyCapitalize(prefix) + titlecase(rest, true)
	}
	if isHonorific(word) {
		rs := []rune(word)
		return pyUpper(string(rs[0])) + string(rs[1:])
	}
	rs := []rune(word)
	if hasInlinePeriod(rs) || (!allCaps && hasUpperLater(rs)) {
		return word
	}
	if isSmallWord(word) {
		return pyLower(word)
	}
	if strings.Contains(word, "/") && !strings.Contains(word, "//") {
		parts := strings.Split(word, "/")
		for i, part := range parts {
			parts[i] = titlecase(part, false)
		}
		return strings.Join(parts, "/")
	}
	if strings.Contains(word, "-") {
		parts := strings.Split(word, "-")
		for i, part := range parts {
			parts[i] = titlecase(part, false)
		}
		return strings.Join(parts, "-")
	}
	if allCaps {
		word = pyLower(word)
	}
	if len([]rune(word)) > 2 && isAllConsonants(word) {
		return pyUpper(word)
	}
	return capFirst(word)
}

// splitBreaks matches Python re.split(r'[\r\n]+', text), including the empty
// trailing field when the text ends in a break.
func splitBreaks(text string) []string {
	if text == "" {
		return []string{""}
	}
	var lines []string
	start := 0
	for i := 0; i < len(text); i++ {
		if text[i] != '\r' && text[i] != '\n' {
			continue
		}
		lines = append(lines, text[start:i])
		for i < len(text) && (text[i] == '\r' || text[i] == '\n') {
			i++
		}
		start = i
		i--
	}
	lines = append(lines, text[start:])
	return lines
}

// splitSpaces keeps every Unicode space as its own separator. Consecutive
// spaces produce empty words between them, matching re.split(r'(\s)', line).
func splitSpaces(line string) (words, spaces []string) {
	var cur strings.Builder
	for _, r := range line {
		if unicode.IsSpace(r) {
			words = append(words, cur.String())
			cur.Reset()
			spaces = append(spaces, string(r))
			continue
		}
		cur.WriteRune(r)
	}
	words = append(words, cur.String())
	return words, spaces
}

func joinWords(words, spaces []string) string {
	var b strings.Builder
	for i, word := range words {
		b.WriteString(word)
		if i < len(spaces) {
			b.WriteString(spaces[i])
		}
	}
	return b.String()
}

func isPunct(r rune) bool {
	switch r {
	case '!', '"', '\u201C', '#', '$', '%', '&', '\'', '\u2018',
		'(', ')', '*', '+', ',', '-', '\u2012', '\u2013', '\u2014', '\u2015',
		'.', '/', ':', ';', '?', '@', '[', '\\', ']', '_', '`', '{', '|', '}', '~':
		return true
	default:
		return false
	}
}

func isSubMarker(r rune) bool {
	switch r {
	case ':', ';', '.', '?', '!', '-', '\u2012', '\u2013', '\u2014', '\u2015':
		return true
	default:
		return false
	}
}

func isWord(r rune) bool {
	return unicode.IsLetter(r) || unicode.IsDigit(r) || r == '_'
}

func boundaryAt(rs []rune, i int) bool {
	left := i > 0 && isWord(rs[i-1])
	right := i < len(rs) && isWord(rs[i])
	return left != right
}

func isLu(r rune) bool {
	return unicode.Is(unicode.Lu, r)
}

func isInitials(word string) bool {
	rs := []rune(word)
	if len(rs) == 0 {
		return false
	}
	return initialsFrom(rs, 0)
}

func initialsFrom(rs []rune, i int) bool {
	if i == len(rs) {
		return true
	}
	if i+1 < len(rs) && isLu(rs[i]) && rs[i+1] == '.' && initialsFrom(rs, i+2) {
		return true
	}
	if i+2 < len(rs) && isLu(rs[i]) && rs[i+1] == '.' && isLu(rs[i+2]) && initialsFrom(rs, i+3) {
		return true
	}
	return false
}

func isDOL(r rune) bool {
	switch r {
	case 'd', 'D', 'o', 'O', 'l', 'L':
		return true
	default:
		return false
	}
}

func isVowel(r rune) bool {
	switch r {
	case 'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U':
		return true
	default:
		return false
	}
}

func isApostropheS(r rune) bool {
	return r == '\'' || r == 's' || r == 'S'
}

func rewriteApostrophe(word string) (string, bool) {
	rs := []rune(word)
	if len(rs) < 3 || !isDOL(rs[0]) || (rs[1] != '\'' && rs[1] != '\u2018') {
		return "", false
	}
	i := 2
	if !unicode.IsLetter(rs[i]) {
		return "", false
	}
	i++
	for i < len(rs) && unicode.IsLetter(rs[i]) {
		i++
	}
	if i != len(rs) {
		if len(rs)-i != 2 || !isApostropheS(rs[i]) || !isApostropheS(rs[i+1]) {
			return "", false
		}
	}
	first := pyLower(string(rs[0]))
	if isVowel(rs[0]) {
		first = pyUpper(string(rs[0]))
	}
	third := pyUpper(string(rs[2]))
	return first + string(rs[1]) + third + string(rs[3:]), true
}

func splitMac(word string) (prefix, rest string, ok bool) {
	rs := []rune(word)
	pre := 0
	if strings.HasPrefix(word, "MC") {
		pre = 2
	} else if len(rs) >= 2 && (rs[0] == 'M' || rs[0] == 'm') && rs[1] == 'c' {
		pre = 2
	}
	if pre == 0 || len(rs) < pre+2 || !isWord(rs[pre]) {
		return "", "", false
	}
	j := pre + 1
	for j < len(rs) && rs[j] != '\n' && rs[j] != '\r' {
		j++
	}
	if j < pre+2 {
		return "", "", false
	}
	return string(rs[:pre]), string(rs[pre:j]), true
}

func isHonorific(word string) bool {
	switch strings.ToLower(word) {
	case "mr", "mrs", "ms", "dr":
		return true
	default:
		return false
	}
}

func hasInlinePeriod(rs []rune) bool {
	for i := 0; i+2 < len(rs); i++ {
		if unicode.IsLetter(rs[i]) && rs[i+1] == '.' && unicode.IsLetter(rs[i+2]) {
			return true
		}
	}
	return false
}

func hasUpperLater(rs []rune) bool {
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	if i >= len(rs) || !unicode.IsLetter(rs[i]) {
		return false
	}
	for i++; i < len(rs) && unicode.IsLetter(rs[i]); i++ {
		if isLu(rs[i]) {
			return true
		}
	}
	return false
}

func isSmallWord(word string) bool {
	for _, alt := range smallFixed {
		if strings.EqualFold(word, alt) {
			return true
		}
	}
	switch strings.ToLower(word) {
	case "v", "v.", "via", "vs", "vs.":
		return true
	default:
		return false
	}
}

func isAllConsonants(word string) bool {
	if word == "" {
		return false
	}
	for _, r := range word {
		switch r {
		case 'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z',
			'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Z':
		default:
			return false
		}
	}
	return true
}

func capFirst(word string) string {
	rs := []rune(word)
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	if i >= len(rs) || !unicode.IsLetter(rs[i]) {
		return word
	}
	return string(rs[:i]) + pyUpper(string(rs[i])) + string(rs[i+1:])
}

// pyUpper and pyLower follow Python's full Unicode case mappings for the
// characters whose mappings change length. Go's strings.ToUpper leaves ß and
// the Latin ligatures unchanged.
func pyUpper(s string) string {
	var b strings.Builder
	for _, r := range s {
		b.WriteString(pyUpperRune(r))
	}
	return b.String()
}

func pyLower(s string) string {
	var b strings.Builder
	for _, r := range s {
		b.WriteString(pyLowerRune(r))
	}
	return b.String()
}

func pyUpperRune(r rune) string {
	switch r {
	case 'ß':
		return "SS"
	case 'ﬁ':
		return "FI"
	case 'ﬂ':
		return "FL"
	case 'ﬀ':
		return "FF"
	case 'ﬃ':
		return "FFI"
	case 'ﬄ':
		return "FFL"
	case 'ﬅ', 'ﬆ':
		return "ST"
	case 'ΐ':
		return "Ι\u0308\u0301"
	case 'ΰ':
		return "Υ\u0308\u0301"
	default:
		return strings.ToUpper(string(r))
	}
}

func pyLowerRune(r rune) string {
	if r == 'İ' {
		return "i\u0307"
	}
	return strings.ToLower(string(r))
}

func pyCapitalize(s string) string {
	rs := []rune(s)
	if len(rs) == 0 {
		return ""
	}
	return pyUpper(string(rs[0])) + pyLower(string(rs[1:]))
}

func foldEqual(rs []rune, alt string) bool {
	return strings.EqualFold(string(rs), alt)
}

func matchSmallForward(rs []rune, i int, boundary bool) int {
	for _, alt := range smallFixed {
		n := len(alt)
		if i+n > len(rs) || !foldEqual(rs[i:i+n], alt) {
			continue
		}
		if boundary && !boundaryAt(rs, i+n) {
			continue
		}
		return n
	}
	if i < len(rs) && strings.EqualFold(string(rs[i]), "v") {
		if i+1 < len(rs) && rs[i+1] == '.' && (!boundary || boundaryAt(rs, i+2)) {
			return 2
		}
		if !boundary || boundaryAt(rs, i+1) {
			return 1
		}
	}
	if i+3 <= len(rs) && foldEqual(rs[i:i+3], "via") && (!boundary || boundaryAt(rs, i+3)) {
		return 3
	}
	if i+1 < len(rs) && foldEqual(rs[i:i+2], "vs") {
		if i+2 < len(rs) && rs[i+2] == '.' && (!boundary || boundaryAt(rs, i+3)) {
			return 3
		}
		if !boundary || boundaryAt(rs, i+2) {
			return 2
		}
	}
	return 0
}

func smallEndingAt(rs []rune, end int) (int, bool) {
	for _, alt := range smallFixed {
		n := len(alt)
		start := end - n
		if start < 0 || !foldEqual(rs[start:end], alt) || !boundaryAt(rs, start) {
			continue
		}
		return start, true
	}
	if end >= 2 && strings.EqualFold(string(rs[end-2]), "v") && rs[end-1] == '.' && boundaryAt(rs, end-2) {
		return end - 2, true
	}
	if end >= 1 && strings.EqualFold(string(rs[end-1]), "v") && boundaryAt(rs, end-1) {
		return end - 1, true
	}
	if end >= 3 && foldEqual(rs[end-3:end], "via") && boundaryAt(rs, end-3) {
		return end - 3, true
	}
	if end >= 3 && foldEqual(rs[end-3:end], "vs.") && boundaryAt(rs, end-3) {
		return end - 3, true
	}
	if end >= 2 && foldEqual(rs[end-2:end], "vs") && boundaryAt(rs, end-2) {
		return end - 2, true
	}
	return 0, false
}

func applySmallFirst(s string) string {
	rs := []rune(s)
	limit := 0
	for limit < len(rs) && isPunct(rs[limit]) {
		limit++
	}
	for p := 0; p <= limit; p++ {
		n := matchSmallForward(rs, p, true)
		if n == 0 {
			continue
		}
		return string(rs[:p]) + pyCapitalize(string(rs[p:p+n])) + string(rs[p+n:])
	}
	return s
}

func applySmallLast(s string) string {
	rs := []rune(s)
	if len(rs) == 0 {
		return s
	}
	if isPunct(rs[len(rs)-1]) {
		if start, ok := smallEndingAt(rs, len(rs)-1); ok {
			return string(rs[:start]) + pyCapitalize(string(rs[start:]))
		}
	}
	if start, ok := smallEndingAt(rs, len(rs)); ok {
		return string(rs[:start]) + pyCapitalize(string(rs[start:]))
	}
	return s
}

func applySubphrase(s string) string {
	rs := []rune(s)
	var b strings.Builder
	for i := 0; i < len(rs); {
		if i+1 < len(rs) && isSubMarker(rs[i]) && rs[i+1] == ' ' {
			if n := matchSmallForward(rs, i+2, false); n > 0 {
				b.WriteRune(rs[i])
				b.WriteRune(' ')
				b.WriteString(pyCapitalize(string(rs[i+2 : i+2+n])))
				i += 2 + n
				continue
			}
		}
		b.WriteRune(rs[i])
		i++
	}
	return b.String()
}
