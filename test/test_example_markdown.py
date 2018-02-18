"""
Test the library by building an simplified parser for markdown
and then running some tests on it.

Our parser will only structure the document into sections, each
subsection nested within the parent.
"""
import pytest
import protoform.protoform as lib


class Section(object):
    """
    A section has a depth, title, and a collection of lines of text
    and subsections (it's children)
    """
    def __init__(self, depth, title, children):
        self.depth = depth
        self.title = title
        self.children = children


def as_string(p):
    """
    Take a parser which parses a list of characters, and modify it to
    return the string consisting of those characters.
    """
    return p.map(lambda cs: "".join(cs))


newline = lib.char('\n')


line = as_string(
    lib.alternative(
        lib.left(lib.take_until(newline, lib.anychar()), newline),
        lib.many1(lib.anychar())))


def build_section_parser():
    """
    Build a parser for structure of markdown document.

    This works by recursion - we build a parser which captures all
    subsections of header depth at least n (markdown_depth(n)). A
    markdown parser is then just as many markdown_depth(0) as we can
    possibly collect.

    When we parse a header, we need to figure out whether we are going to
    add it inside the subsections of the currently accumulating section,
    or go up a level instead. To do this we use a lookahead parse (lib.peek)
    and a conditional subsequent parse. This is the motivation for
    parse_section_if_depth_sat.
    """
    parser_concat = lib.lift(lambda *args: "".join(args))

    header_tag = parser_concat(
        lib.char('#'),
        lib.take_until(lib.char(' '), lib.char('#')).map(lambda cs: "".join(cs)))

    def parse_section_if_depth_sat(pred):
        """
        Parses a header if it's depth satisfies the passed predicate
        """
        def conditional_parse(t):
            return section(len(t)) if pred(len(t)) else lib.fail()

        return lib.peek(header_tag).bind(conditional_parse)

    def markdown_depth(n):
        """
        Parse markdown of section depth at least n
        """
        return lib.alternative(
            parse_section_if_depth_sat(lambda m: m > n),
            line)

    def section(n):
        """
        Capture the contents of a section of depth n. Note that
        this function assumes that n is the correct depth for the
        next header.

        A section of depth n is parsed by parsing it's title,
        then parsing all subsections of depth exceeding n+1
        """
        remove_whitespace = lib.lift(lambda s: s.strip())
        title = remove_whitespace(lib.right(header_tag, line))
        subsections = lib.take_until(
            parse_section_if_depth_sat(lambda m: m <= n),
            markdown_depth(n))

        @lib.parser(title, subsections)
        def _section(t, ss):
            return Section(n, t, ss)

        return _section

    return lib.many(markdown_depth(0))


markdown = build_section_parser()


# Tests
def test_line():
    assert(line("foo\n") == "foo")
    assert(line("foo") == "foo")
    assert(line(" ") == " ")
    with pytest.raises(lib.ParseError):
        line("")


def test_markdown_level_parser():
    test_md = "# This is a markdown document\n" \
              "This is being used to test parsing markown\n" \
              "## Subsection 1\n" \
              "Here is some text in subsection 1\n" \
              "### Super subsection\n" \
              "Text\n" \
              "## Subsection 2\n" \
              "More text"
    res = markdown(test_md)
    assert(len(res) == 1)
    assert(res[0].title == "This is a markdown document")
    assert(len(res[0].children) == 3)
