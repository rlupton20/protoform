class Parser(object):
    """
    Base parser object. Provides utilities for deriving new parsers
    from old ones. Never constructed directly.
    """
    def __init__(self):
        pass

    def run_parser(self, string):
        pass

    def __call__(self, string):
        """
        The function interface for a parser performs a parse, expecting
        to consume all the input.
        """
        res = self.run_parser(string)
        if res != None:
            m, r = res
            if r != "":
                return None
            else:
                return m
        else:
            return None

    def partial(self):
        """
        By default, parsers expect to consume all input. partial produces
        a parser that is happy to bin the rest of the input.
        """
        class Partial(self.__class__):
            def __call__(self, string):
                res = self.run_parser(string)
                if res != None:
                    m, _ = res
                    return m
                else:
                    return None
        return Partial()

    def map(self, f):
        class MappedParser(self.__class__):
            def run_parser(self, string):
                res = super().run_parser(string)
                if res == None:
                    return None
                else:
                    m, r = res
                    return (f(m), r)
        return MappedParser()

    
def tag(tag):
    class Match(Parser):
        def run_parser(self, string):
            if string.startswith(tag):
                return (tag, string[len(tag):])
            else:
                return None
    return Match()


def sequence(*args):
    class Sequence(Parser):
        def run_parser(self, string):
            acc = []
            try:
                for p in args:
                    x, s = p.run_parser(string)
                    acc.append(x)
                    string = s
                return (tuple(acc), string)
            except TypeError:
                return None
    return Sequence()


# Decorators
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
                
            
