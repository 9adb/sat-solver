"""Boolean expression trees, with serialization."""

import collections

AndExpr = collections.namedtuple('AndExpr', ['exprs'])
OrExpr = collections.namedtuple('OrExpr', ['exprs'])
NotExpr = collections.namedtuple('NotExpr', ['expr'])
Variable = collections.namedtuple('Variable', ['name'])

def make_not(expr):
    return NotExpr(expr)

def make_or(exprs):
    exprs = frozenset(exprs)
    if not exprs:
        return False
    elif len(exprs) == 1:
        return list(exprs)[0]
    else:
        return OrExpr(exprs)

def make_and(exprs):
    exprs = frozenset(exprs)
    if not exprs:
        return True
    elif len(exprs) == 1:
        return list(exprs)[0]
    else:
        return AndExpr(exprs)

def parse(input):
    """Parse a string into an expression tree."""
    tokens = _parse_into_tokens(iter(input))
    expr = _parse_into_tree(tokens)
    try:
        next(tokens)
    except StopIteration:
        return expr
    else:
        raise ValueError('Parse error (expected end of input).')

def _parse_into_tokens(input):
    yield '('
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
            raise ValueError('Parse error (invalid symbol).')
    if token:
        yield ''.join(token)
    yield ')'

def _parse_into_tree(tokens):
    while True:
        token = next(tokens)
        if token == '~':
            return make_not(_parse_into_tree(tokens))
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
                    raise ValueError('Parse error (operator disagreement).')
                else:
                    operator = token
            if operator == '&':
                return make_and(exprs)
            elif operator == '|':
                return make_or(exprs)
            elif len(exprs) == 1 and operator is None:
                return exprs[0]
            else:
                raise ValueError('Parse error (invalid operator).')
        else:
            raise ValueError('Parse error (unxpected token).') 
    
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

        return make_not(subexpr)

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

        return make_and(subexprs)

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

        return make_or(subexprs)

    else:
        return expr

def substitute(expr, vars):
    if isinstance(expr, Variable):
        return vars.get(expr.name, expr)
    if isinstance(expr, NotExpr):
        return make_not(substitute(expr.expr, vars))
    if isinstance(expr, AndExpr):
        return make_and(substitute(subexpr, vars) for subexpr in expr.exprs)
    if isinstance(expr, OrExpr):
        return make_or(substitute(subexpr, vars) for subexpr in expr.exprs)
    return expr

def evaluate(expr, vars):
    return simplify(substitute(expr, vars))

def variables(expr):
    if isinstance(expr, Variable):
        return {expr.name}
    if isinstance(expr, NotExpr):
        return variables(expr.expr)
    if isinstance(expr, (AndExpr, OrExpr)):
        v = set()
        for subexpr in expr.exprs:
            v |= variables(subexpr)
        return v
    return set()
