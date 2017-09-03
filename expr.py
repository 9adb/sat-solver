"""Boolean expression trees, with serialization."""

import collections

AndExpr = collections.namedtuple('AndExpr', ['exprs'])
OrExpr = collections.namedtuple('OrExpr', ['exprs'])
NotExpr = collections.namedtuple('NotExpr', ['expr'])
Variable = collections.namedtuple('Variable', ['name'])

def parse(input):
    """Parse a string into an expression tree."""
    tokens = _parse_into_tokens(iter(input))
    expr = _parse_into_tree(tokens)
    try:
        next(tokens)
    except StopIteration:
        return expr
    else:
        raise ValueError('Parse error.')

def _parse_into_tokens(input):
    token = []
    for symbol in input:
        if symbol.isalpha():
            token.append(symbol)
        elif token:
            yield ''.join(token)
            token = []

        if symbol in (' ', '\t', '\n'):
            continue
        elif symbol in ('(', ')', '&', '|', '~', '0', '1'):
            yield symbol
        elif not symbol.isalpha():
            raise ValueError('Parse error.')
    if token:
        yield ''.join(token)

def _parse_into_tree(tokens):
    exprs = []
    while True:
        token = next(tokens)
        if token == '~':
            return NotExpr(_parse_into_tree(tokens))
        elif token == '0':
            return False
        elif token == '1':
            return True
        elif token.isalpha():
            return Variable(token)
        elif token == '(':
            operator = None
            exprs = []
            while True:
                exprs.append(_parse_into_tree(tokens))
                token = next(tokens)
                if token == ')':
                    break
                elif operator is not None and token != operator:
                    raise ValueError('Parse error.')
                else:
                    operator = token
            if operator == '&':
                return AndExpr(frozenset(exprs))
            elif operator == '|':
                return OrExpr(frozenset(exprs))
            else:
                raise ValueError('Parse error.')
        else:
            raise ValueError('Parse error.') 
    
def format(expr):
    """Format an expression tree as a string."""
    chunks = []
    _format_chunks(expr, chunks, outer=True)
    return ''.join(chunks)

def _format_chunks(expr, chunks, outer=False):
    if expr is True:
        chunks.append('1')
    elif expr is False:
        chunks.append('0')
    elif isinstance(expr, (AndExpr, OrExpr)):
        if isinstance(expr, AndExpr):
            operator = '&'
        else:
            operator = '|'
        chunks.append('(')
        for i, subexpr in enumerate(expr.exprs):
            _format_chunks(subexpr, chunks)
            if i < len(expr.exprs) - 1:
                chunks.append(operator)
        chunks.append(')')
    elif isinstance(expr, NotExpr):
        chunks.append('~')
        _format_chunks(expr.expr, chunks)
    elif isinstance(expr, Variable):
        chunks.append(expr.name)
    else:
        raise TypeError('Unexpected expression type %r' % type(expr))

def simplify(expr):
    """Apply basic simplification rules."""
    if isinstance(expr, NotExpr):
        subexpr = simplify(expr.expr)

        # Remove double-negation.
        if isinstance(subexpr, NotExpr):
            return subexpr.expr

        # ~1 -> 0
        if subexpr is True:
            return False

        # ~0 -> 1
        if subexpr is False:
            return True

        return NotExpr(subexpr)

    elif isinstance(expr, AndExpr):
        subexprs = set([simplify(subexpr) for subexpr in expr.exprs])

        # (0&...) -> 0
        if False in subexprs:
            return False

        # ((a&b)&c) -> (a&b&c)
        flattened_subexprs = set()
        for subexpr in subexprs:
            if isinstance(subexpr, AndExpr):
                flattened_subexprs |= subexpr.exprs
            else:
                flattened_subexprs.add(subexpr)
        subexprs = flattened_subexprs

        # (1&a) -> a
        subexprs.discard(True)

        if len(subexprs) > 1:
            return AndExpr(frozenset(subexprs))
        elif len(subexprs) == 1:
            return subexprs.pop()
        else:
            return True

    elif isinstance(expr, OrExpr):
        subexprs = set([simplify(subexpr) for subexpr in expr.exprs])

        # (1|...) -> 1
        if True in subexprs:
            return True

        # ((a|b)|c) -> (a|b|c)
        flattened_subexprs = set()
        for subexpr in subexprs:
            if isinstance(subexpr, OrExpr):
                flattened_subexprs |= subexpr.exprs
            else:
                flattened_subexprs.add(subexpr)
        subexprs = flattened_subexprs

        # (1|a) -> a
        subexprs.discard(False)

        if len(subexprs) > 1:
            return OrExpr(frozenset(subexprs))
        elif len(subexprs) == 1:
            return subexprs.pop()
        else:
            return False

    else:
        return expr
