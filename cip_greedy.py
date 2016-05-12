import itertools
import math
import platform

import pulp

import minimum_element


def lp(cs, C, ls, ps):
    """
    Args:
        cs: a list containing the cost of probing `X_1, ..., X_n`
        C: the cost budget
        ls: a list of the lengths of the intervals `I_1, ..., I_m`. Each
            element of the list contains the length of the corresponding
            interval.
        ps: a list of functions, each of which takes that take in one argument
            `j` and returns `Pr[X_i >= a_j]`
    Returns:
        a triple of type `(pulp.LpVariable, list of pulp.LpVariable,
        pulp.LpProblem)` with values of `(z, list of y_i,
        unsolved linear program)`.
    """
    assert len(ps) == len(cs)
    n = len(ps)
    m = len(ls)

    problem = pulp.LpProblem('Step 1', pulp.LpMinimize)

    z = pulp.LpVariable('z', cat='Integer')
    ys = [pulp.LpVariable('y' + str(i), lowBound=0, upBound=1, cat='Integer')
          for i in xrange(n)]

    problem += z
    for j in xrange(1, m + 1):
        aa = (math.log(1.0 / p(j)) for p in ps)
        problem += pulp.lpDot(ys, aa) <= math.log(ls[j - 1]) - z, 'j=' + str(j)
    problem += pulp.lpDot(cs, ys) <= C, 'cost'

    return z, ys, problem


def solve(Xs_info, C, aa, f_cost, epsilon):
    """
    Args:
        Xs_info: map from distribution to tuple of type (probe cost, p_ij)
        C: the cost budget
        aa: the values taken on by the distribution
        epsilon: the epsilon 
    """
    # Compute interval lengths. Note that I_i = [a_j, a_{j + 1}].
    assert len(set(aa)) == len(aa), \
        'The values taken on by the distribution must be distinct'
    assert all(itertools.imap(lambda a: a >= 0, aa)), \
        'The values taken on by the distribution must be nonnegative'

    
    ls = [t - s for s, t in zip(aa, aa[1:])]
    cs, ps = zip(*Xs_info.itervalues())
    z, ys, problem = lp(cs, C, ls, ps)

    print problem

    problem.solve()

    print 'z = {}, ys = {}'.format(z.value(), [y.value() for y in ys])

    # The subset S corresponding to i s.t. y_i = 1 is feasible
    s0 = [x for x, y in zip(Xs_info.iterkeys(), ys) if y == 1]

    # new cost budget C(log log m + log 1/e)
    m = len(aa)
    C_relaxed = C * (math.log(math.log(m)) + math.log(1.0 / epsilon))

    X_cost = {k: c for k, (c, _) in Xs_info.iteritems()}
    return minimum_element.minimum_element(X_cost, C_relaxed, f_cost, S_0=s0)


if __name__ == '__main__':
    solve({'x1': (1, lambda _: 0.5), 'x2': (2, lambda _: 0.5)}, 100, [17, 18], len, 0.001)
