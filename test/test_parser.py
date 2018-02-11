import protoform.protoform as lib


# Test basic tag matching to check basic parsing works
def test_match_tag():
    p = lib.tag("foo")
    assert(p("foo") == "foo")


def test_match_tag_fail():
    p = lib.tag("foo")
    assert(p("flo") is None)


def test_match_init():
    p = lib.tag("foo")
    assert(p.run_parser("foot") == ("foo", "t"))


def test_match_init_complete():
    p = lib.tag("foo")
    assert(p("foot") is None)


# Now test parser base class
def test_derived_partial():
    p = lib.tag("foo").partial()
    assert(p("foot") == "foo")


def test_map():
    p = lib.tag("foo").map(len)
    assert(p("foo") == 3)


def test_else_parse_else_branch():
    q = lib.tag("foo")
    p = lib.tag("bar").else_parse(q)
    assert(p("foo") == "foo")


def test_else_parse_success_branch():
    q = lib.tag("bar")
    p = lib.tag("foo").else_parse(q)
    assert(p("foo") == "foo")


def test_else_parse_can_still_fail():
    q = lib.tag("bar")
    p = lib.tag("foo").else_parse(q)
    assert(p("baz") is None)


# Test basic parsers
def test_anychar():
    p = lib.anychar()
    assert(p.run_parser("foo") == ("f", "oo"))


def test_anychar_fail():
    p = lib.anychar()
    assert(p.run_parser("") is None)


def test_peek():
    p = lib.peek(lib.tag("fo"))
    assert(p.run_parser("foo") == ("fo", "foo"))


def test_peek_fail():
    p = lib.peek(lib.tag("fo"))
    assert(p.run_parser("fro") is None)
    assert(p.run_parser("") is None)


# Test sequencing combinator
def test_sequence():
    p = lib.sequence(lib.tag("foo"), lib.tag("bar"))
    assert(p("foobar") == ("foo", "bar"))


def test_sequence_fail():
    p = lib.sequence(lib.tag("foo"), lib.tag("baz"))
    assert(p("foobar") is None)


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
    assert(plen("boo") is None)


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
    assert(p("foobaz") is None)
    assert(p("foobarr") is None)


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


def test_unless_no_stop():
    p = lib.unless(lib.char("b"), lib.anychar())
    assert(p.run_parser("foobar") == ("f", "oobar"))


def test_unless_stop_case():
    p = lib.unless(lib.char("f"), lib.anychar())
    assert(p.run_parser("foobar") is None)


def test_take_until():
    p = lib.take_until(lib.char("b"), lib.anychar())
    assert(p.run_parser("foobar") == (['f', 'o', 'o'], "bar"))
