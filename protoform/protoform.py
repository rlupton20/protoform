class ParseError(Exception):
    def __init__(self, message, remaining=None):
        self.message = message
        self.remaining = remaining


class Parser(object):
    """
    Base parser object. Provides utilities for deriving new parsers
    from old ones. Never constructed directly.
    """
    def __init__(self):
        pass

    def _run_parser(self, string):
        pass

    def __call__(self, string):
        """
        The function interface for a parser performs a parse, expecting
        to consume all the input.
        """
        m, r = self._run_parser(string)
        if r == "":
            return m
        else:
            raise ParseError("Failed to consume all input. Remaining: {}..."
                                 .format(r[0:10]),
                             remaining=r)

    def partial(self):
        """
        By default, parsers expect to consume all input. partial produces
        a parser that is happy to bin the rest of the input.
        """
        class Partial(self.__class__):
            def __call__(self, string):
                return self._run_parser(string)
        return Partial()

    def map(self, f):
        """
        On success apply the function f to the parsed value
        """
        class MappedParser(self.__class__):
            def _run_parser(self, string):
                m, r = super()._run_parser(string)
                return (f(m), r)
        return MappedParser()


# Basic parsers
def tag(tag):
    """
    Matches the beginning of a string if equal to tag
    """
    class Match(Parser):
        def _run_parser(self, string):
            if string.startswith(tag):
                return (tag, string[len(tag):])
            else:
                raise ParseError("Failed to match {}".format(tag))
    return Match()


def anychar():
    """
    Matches any character
    """
    class AnyChar(Parser):
        def _run_parser(self, string):
            if string == "":
                raise ParseError("Can't match anychar on empty string")
            else:
                x, *_ = string
                return (x, string[1:])
    return AnyChar()


def peek(p):
    """
    Tries to match the next part of the input stream against p, but
    doesn't consume any input if it matches.
    """
    class PeekP(Parser):
        def _run_parser(self, string):
            x, _ = p._run_parser(string)
            return (x, string)
    return PeekP()


def char(c):
    """
    Matches a single character
    """
    assert(len(c) == 1)
    return tag(c)


# The sequence combinator lets us build some decorators which
# help define more combinators
def sequence(*args):
    class Sequence(Parser):
        def _run_parser(self, string):
            acc = []
            for p in args:
                x, s = p._run_parser(string)
                acc.append(x)
                string = s
            return (tuple(acc), string)
    return Sequence()


# Decorators for specifying parsers in terms of functions/classes
# on successfully parsed values

# TODO Add keyword parsers
def parser(*parsers):
    """
    Decorator which allows combinations of parsers in terms of the values parsed.
    """
    def wrapped(f):
        return sequence(*parsers).map(lambda args: f(*args))
    return wrapped


class DeriveParser(object):
    """
    Decorator/mixin for classes to provide a parser
    """
    def __init__(self, *parsers):
        self.parsers = parsers

    def __call__(self, cls):
        class Wrapped(cls):
            def parser():
                return sequence(*self.parsers).map(lambda args: cls(*args))
        return Wrapped


# More combinators
def left(p, q):
    @parser(p, q)
    def l(x, _):
        return x
    return l


def right(p, q):
    @parser(p, q)
    def r(_, y):
        return y
    return r


def take_until(e, p):

    class TakeUntil(Parser):
        def _run_parser(self, string):
            acc = []
            while True:
                try:
                    peek(e)._run_parser(string)
                    return (acc, string)
                except ParseError:
                    x, string = p._run_parser(string)
                    acc.append(x)

    return TakeUntil()
