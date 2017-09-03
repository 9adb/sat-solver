"""Boolean expression trees, with serialization."""

import collections

AndExpr = collections.namedtuple('AndExpr', ['exprs'])
OrExpr = collections.namedtuple('OrExpr', ['exprs'])
NotExpr = collections.namedtuple('NotExpr', ['expr'])
Variable = collections.namedtuple('Variable', ['name'])

def parse(input):
    """Parse a string into an expression tree."""

def format(expr):
    """Format an expression tree as a string."""

def simplify(expr):
    """Apply basic simplification rules."""
