import math


def minimum_element(X_cost, C_relaxed, f_cost, S_0=None):
    S = set() if S_0 is None else set(S_0)

    print S
    while len(S) < len(X_cost) and sum(X_cost[i] for i in S) <= C_relaxed:
        argmin = None
        min_score = float("inf")

        for i, c in X_cost.iteritems():
            s_with_i = math.log(float(f_cost(S | set([i]))))
            s_only = math.log(float(f_cost(S)))
            score = (s_with_i - s_only) / c
            if score < min_score:
                min_score = score
                argmin = i

        S.add(argmin)

    return S

def modified_greedy(X_expectation, C, epsilon, f_cost):
    """Computes the minimum element greedily when the distributions are known to be uniform.
    """
    C_relaxed = 2 * C * log(1 / epsilon)
    t = min(X_expectation.values()) / epsilon

    S_dict = {}
    while t >= min(X_expectation.values()):
        S[t] = minimum_element(C_relaxed, f_cost)
        t /= 2.

    S_min = None
    min_expectation = float("inf")
    for S in S_dict.values():
        expectation = min(S, key=lambda x: X_expectation[x])
        if expectation < min_expectation:
            min_expectation = expectation
            S_min = S

    return S_min

