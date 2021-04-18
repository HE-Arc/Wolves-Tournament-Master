import sympy
from sympy.physics.secondquant import AnnihilateBoson, CreateBoson, BosonicOperator, Commutator

class AnnihilateMode(AnnihilateBoson):
    def _sympystr(self, *args, **kwargs):
        return 'abcdefg'[self.args[0]]

    def __str__(self):
        return self._sympystr()

    def __repr__(self):
        return self._sympystr()

class CreateMode(CreateBoson):
    def _sympystr(self, *args, **kwargs):
        return 'abcdefg'[self.args[0]] + 'd'

    def __str__(self):
        return self._sympystr()

    def __repr__(self):
        return self._sympystr()

class NMode(BosonicOperator):
    def _sympystr(self, *args, **kwargs):
        return 'n' + 'abcdefg'[self.args[0]]

    def __str__(self):
        return self._sympystr()

    def __repr__(self):
        return self._sympystr()


a, b = AnnihilateMode(0), AnnihilateMode(1)
ad, bd = CreateMode(0), CreateMode(1)

def normal_order(x):
    #print 'ordering', x, '...'
    x = x.expand()
    if isinstance(x, sympy.Add):
        return sympy.Add(*map(normal_order, x.args))
    elif not isinstance(x, sympy.Mul):
        return x
    c, nc = x.args_cnc()
    ops = nc
    _ops = []
    for i in ops:
        if isinstance(i, sympy.Pow):
            _ops.extend([i.args[0]] * i.args[1])
        else:
            _ops.append(i)
    ops = _ops
    #print _ops
    while True:
        for i in range(len(ops)-1):
            op1, op2 = ops[i], ops[i+1]
            assert isinstance(op1, (AnnihilateBoson, CreateBoson)), (x, op1, type(op1))
            assert isinstance(op2, (AnnihilateBoson, CreateBoson)), (x, op2, type(op2))
            n1, n2 = op1.args[0], op2.args[0]
            if n1 > n2:
                ops[i], ops[i+1] = op2, op1
                #print 'switch', op1, op2
                break

            if n1 == n2 and isinstance(op1, AnnihilateBoson) and isinstance(op2, CreateBoson):
                #print sympy.Mul(*(c + ops)),
                ops[i] = (op2 * op1 + 1)
                ops.pop(i+1)
                #print '-->', sympy.Mul(*(c + ops))
                return normal_order(sympy.Mul(*(c + ops)))
        else:
            ret = sympy.Mul(*(c + ops))
            #print ret, 'is normal ordered'
            return ret

def anti_normal_order(x):
    #print 'ordering', x, '...'
    x = x.expand()
    if isinstance(x, sympy.Add):
        return sympy.Add(*map(anti_normal_order, x.args))
    elif not isinstance(x, sympy.Mul):
        return x
    c, nc = x.args_cnc()
    ops = nc
    _ops = []
    for i in ops:
        if isinstance(i, sympy.Pow):
            _ops.extend([i.args[0]] * i.args[1])
        else:
            _ops.append(i)
    ops = _ops
    #print _ops
    while True:
        for i in range(len(ops)-1):
            op1, op2 = ops[i], ops[i+1]
            assert isinstance(op1, (AnnihilateBoson, CreateBoson, NMode)), (x, op1, type(op1))
            assert isinstance(op2, (AnnihilateBoson, CreateBoson, NMode)), (x, op2, type(op2))
            n1, n2 = op1.args[0], op2.args[0]
            if n1 > n2:
                ops[i], ops[i+1] = op2, op1
                break

            if isinstance(op1, NMode):
                continue

            # a*n --> (n+1)*a
            if n1 == n2 and isinstance(op1, AnnihilateBoson) and isinstance(op2, NMode):
                ops[i] = (op2 + 1)
                ops[i+1] = op1
                return anti_normal_order(sympy.Mul(*(c + ops)))

            # ad*n --> (n-1)*ad
            if n1 == n2 and isinstance(op1, CreateBoson) and isinstance(op2, NMode):
                ops[i] = (op2 - 1)
                ops[i+1] = op1
                return anti_normal_order(sympy.Mul(*(c + ops)))

            # ad*a --> n
            if n1 == n2 and isinstance(op1, CreateBoson) and isinstance(op2, AnnihilateBoson):
                #print sympy.Mul(*(c + ops)),
                ops[i] = NMode(n1)
                ops.pop(i+1)
                break

            # a*ad --> (n + 1)
            if n1 == n2 and isinstance(op1, AnnihilateBoson) and isinstance(op2, CreateBoson):
                #print sympy.Mul(*(c + ops)),
                ops[i] = (NMode(n1) + 1)
                ops.pop(i+1)
                return anti_normal_order(sympy.Mul(*(c + ops)))

        else:
            ret = sympy.Mul(*(c + ops))
            #print ret, 'is normal ordered'
            return ret


def comm(x, y):
    return normal_order(Commutator(x, y).doit())


def BCH(x, y, n):
    term = y
    print('term 0', y)
    for i in range(n):
        term = comm(x, term)
        print('term', i+1, term)


def dagger(x):
    if isinstance(x, AnnihilateMode):
        return CreateMode(x.args[0])
    elif isinstance(x, CreateMode):
        return AnnihilateMode(x.args[0])
    elif isinstance(x, sympy.Pow):
        return sympy.Pow(dagger(x.args[0]), x.args[1])
    elif isinstance(x, sympy.Add):
        return sympy.Add(*map(dagger, x.args))
    elif isinstance(x, sympy.Mul):
        c, nc = x.args_cnc()
        new_c = [v.conjugate() for v in c]
        new_nc = list(reversed(map(dagger, nc)))
        return sympy.Mul(*(new_c + new_nc))
    else:
        raise TypeError(type(x))

