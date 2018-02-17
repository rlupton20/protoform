import pytest
import protoform.protoform as lib


# Test basic tag matching to check basic parsing works
def test_match_tag():
    p = lib.tag("foo")
    assert(p("foo") == "foo")


def test_match_tag_fail():
    p = lib.tag("foo")
    with pytest.raises(lib.ParseError):
        p("flo")


def test_match_init():
    p = lib.tag("foo")
    assert(p._run_parser("foot") == ("foo", "t"))


def test_match_init_complete():
    p = lib.tag("foo")
    with pytest.raises(lib.ParseError):
        p("foot")


# Now test parser base class
def test_derived_partial():
    p = lib.tag("foo").partial()
    assert(p("foot") == ("foo", "t"))


def test_map():
    p = lib.tag("foo").map(len)
    assert(p("foo") == 3)


def test_bind():
    p = lib.anychar().bind(lambda c: lib.tag("foo") if c == 't' else lib.tag("bar"))
    assert(p("tfoo") == "foo")
    assert(p("fbar") == "bar")


def test_bind_initial_failue():
    p = lib.char('a').bind(lambda _: lib.tag("foo"))
    with pytest.raises(lib.ParseError):
        p("bfoo")


def test_bind_continuation_failure():
    p = lib.anychar().bind(lambda c: lib.tag("foo") if c == 't' else lib.tag("bar"))
    with pytest.raises(lib.ParseError):
        p("tbar")


# Test basic parsers
def test_anychar():
    p = lib.anychar()
    assert(p._run_parser("foo") == ("f", "oo"))


def test_anychar_fail():
    p = lib.anychar()
    with pytest.raises(lib.ParseError):
        p._run_parser("")


def test_peek():
    p = lib.peek(lib.tag("fo"))
    assert(p._run_parser("foo") == ("fo", "foo"))


def test_peek_fail():
    p = lib.peek(lib.tag("fo"))
    with pytest.raises(lib.ParseError):
        p._run_parser("fro")
    with pytest.raises(lib.ParseError):
        p._run_parser("")


# Test sequencing combinator
def test_sequence():
    p = lib.sequence(lib.tag("foo"), lib.tag("bar"))
    assert(p("foobar") == ("foo", "bar"))


def test_sequence_fail():
    p = lib.sequence(lib.tag("foo"), lib.tag("baz"))
    with pytest.raises(lib.ParseError):
        p("foobar")


def test_args_via_sequence():
    class Dummy(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    p = lib.sequence(lib.tag("foo"), lib.tag("bar")).map(lambda args: Dummy(*args))
    r = p("foobar")
    assert(r is not None)
    assert(r.x == "foo")
    assert(r.y == "bar")


# Test decorator combinators
def test_function_decorator():

    @lib.parser(lib.tag("foo"))
    def plen(s):
        return len(s)

    assert(plen("foo") == 3)
    with pytest.raises(lib.ParseError):
        plen("boo")


def test_class_decorator():

    @lib.DeriveParser(lib.tag("foo"), lib.tag("bar"))
    class Dummy(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    p = Dummy.parser()
    r = p("foobar")

    # Successful cases
    assert(r is not None)
    assert(r.x == "foo")
    assert(r.y == "bar")
    # Failure case
    with pytest.raises(lib.ParseError):
        p("foobaz")
    with pytest.raises(lib.ParseError):
        p("foobarr")


# Test other combinators
def test_left():
    p = lib.tag("foo")
    q = lib.tag("bar")
    parser = lib.left(p, q)
    assert(parser("foobar") == "foo")


def test_right():
    p = lib.tag("foo")
    q = lib.tag("bar")
    parser = lib.right(p, q)
    assert(parser("foobar") == "bar")


def test_take_until():
    p = lib.take_until(lib.char("b"), lib.anychar())
    assert(p._run_parser("foobar") == (['f', 'o', 'o'], "bar"))
