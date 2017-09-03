import unittest

import expr

class ExprTest(unittest.TestCase):

    def test_make_or(self):
        self.assertEqual(expr.make_or([]), False)
        self.assertEqual(expr.make_or([True]), True)
        self.assertEqual(expr.make_or([False]), False)
        self.assertEqual(
            expr.make_or([False, True]), expr.OrExpr(frozenset([False, True])))

    def test_make_and(self):
        self.assertEqual(expr.make_and([]), True)
        self.assertEqual(expr.make_and([True]), True)
        self.assertEqual(expr.make_and([False]), False)
        self.assertEqual(
            expr.make_and([False, True]), expr.AndExpr(frozenset([False, True])))

    def test_parse_atoms(self):
        self.assertEqual(expr.parse('1'), True)
        self.assertEqual(expr.parse('0'), False)
        self.assertEqual(expr.parse('a'), expr.Variable(name='a'))
        self.assertEqual(expr.parse('ab'), expr.Variable(name='ab'))
        self.assertEqual(expr.parse('(a)'), expr.Variable(name='a'))
        self.assertEqual(expr.parse(' 1'), True)
        self.assertEqual(expr.parse('1 '), True)

    def test_parse_exprs(self):
        self.assertEqual(
            expr.parse('a&1&0'),
            expr.AndExpr(exprs=frozenset([expr.Variable(name='a'), True, False])))
        self.assertEqual(
            expr.parse('a|1|0'),
            expr.OrExpr(exprs=frozenset([expr.Variable(name='a'), True, False])))
        self.assertEqual(
            expr.parse('~a'),
            expr.NotExpr(expr=expr.Variable(name='a')))

    def test_parse_errors(self):
        with self.assertRaises(ValueError):
            expr.parse('!')
        with self.assertRaises(ValueError):
            expr.parse('(a&b|c)')
        with self.assertRaises(ValueError):
            expr.parse('(a~b)')
        with self.assertRaises(ValueError):
            expr.parse('(a&b)c')
        with self.assertRaises(ValueError):
            expr.parse('(a&b))')

    def test_format_errors(self):
        with self.assertRaises(TypeError):
            expr.format('foo')

    def test_format_roundtrip(self):
        inputs = ['0', '1', 'a', '~a', '(a&a)', '(a&b)', '(a&b&c)', '(a|(a&b)|~d)']
        for input in inputs:
            self.assertEqual(
                expr.parse(input),
                expr.parse(expr.format(expr.parse(input))))

    def test_simplify_atoms(self):
        self.assertEqual(expr.simplify(expr.parse('0')), expr.parse('0'))
        self.assertEqual(expr.simplify(expr.parse('1')), expr.parse('1'))
        self.assertEqual(expr.simplify(expr.parse('a')), expr.parse('a'))

    def test_simplify_negation(self):
        self.assertEqual(expr.simplify(expr.parse('~a')), expr.parse('~a'))
        self.assertEqual(expr.simplify(expr.parse('~~a')), expr.parse('a'))
        self.assertEqual(expr.simplify(expr.parse('~~~a')), expr.parse('~a'))
        self.assertEqual(expr.simplify(expr.parse('~0')), expr.parse('1'))
        self.assertEqual(expr.simplify(expr.parse('~1')), expr.parse('0'))

    def test_simplify_and_identities(self):
        self.assertEqual(expr.simplify(expr.parse('a&a')), expr.parse('a'))
        self.assertEqual(expr.simplify(expr.parse('a&0')), expr.parse('0'))
        self.assertEqual(expr.simplify(expr.parse('a&1')), expr.parse('a'))
        self.assertEqual(expr.simplify(expr.parse('0&0')), expr.parse('0'))
        self.assertEqual(expr.simplify(expr.parse('1&1')), expr.parse('1'))

    def test_simplify_or_identities(self):
        self.assertEqual(expr.simplify(expr.parse('a|a')), expr.parse('a'))
        self.assertEqual(expr.simplify(expr.parse('a|0')), expr.parse('a'))
        self.assertEqual(expr.simplify(expr.parse('a|1')), expr.parse('1'))
        self.assertEqual(expr.simplify(expr.parse('0|0')), expr.parse('0'))
        self.assertEqual(expr.simplify(expr.parse('1|1')), expr.parse('1'))

    def test_simplify_and_associativity(self):
        self.assertEqual(
            expr.simplify(expr.parse('a&(b&c)')), expr.parse('a&b&c'))
        self.assertEqual(
            expr.simplify(expr.parse('(a&b)&c')), expr.parse('a&b&c'))
        self.assertEqual(
            expr.simplify(expr.parse('a&(a&b)')), expr.parse('a&b'))

    def test_simplify_or_associativity(self):
        self.assertEqual(
            expr.simplify(expr.parse('a|(b|c)')), expr.parse('a|b|c'))
        self.assertEqual(
            expr.simplify(expr.parse('(a|b)|c')), expr.parse('a|b|c'))
        self.assertEqual(
            expr.simplify(expr.parse('a|(a|b)')), expr.parse('a|b'))

    def test_evaluate_constant(self):
        self.assertEqual(expr.evaluate(expr.parse('0'), {'a': True}), False)
        self.assertEqual(expr.evaluate(expr.parse('1'), {'a': True}), True)

    def test_evaluate_simple(self):
        self.assertEqual(expr.evaluate(expr.parse('a'), {'a': True}), True)
        self.assertEqual(expr.evaluate(expr.parse('a'), {'a': False}), False)

    def test_evaluate_negated(self):
        self.assertEqual(expr.evaluate(expr.parse('~a'), {'a': True}), False)
        self.assertEqual(expr.evaluate(expr.parse('~a'), {'a': False}), True)

    def test_evaluate_and(self):
        self.assertEqual(
            expr.evaluate(expr.parse('a&b&c'), {'a': True}), expr.parse('b&c'))
        self.assertEqual(
            expr.evaluate(expr.parse('a&b&c'), {'a': False}), expr.parse('0'))

    def test_evaluate_or(self):
        self.assertEqual(
            expr.evaluate(expr.parse('a|b|c'), {'a': True}), expr.parse('1'))
        self.assertEqual(
            expr.evaluate(expr.parse('a|b|c'), {'a': False}), expr.parse('b|c'))

    def test_variables(self):
        self.assertEqual(expr.variables(expr.parse('0')), set())
        self.assertEqual(expr.variables(expr.parse('1')), set())
        self.assertEqual(expr.variables(expr.parse('a')), {'a'})
        self.assertEqual(expr.variables(expr.parse('~a')), {'a'})
        self.assertEqual(expr.variables(expr.parse('a&b')), {'a', 'b'})
        self.assertEqual(expr.variables(expr.parse('a|b')), {'a', 'b'})

if __name__ == '__main__':
    unittest.main()
