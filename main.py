#!/usr/bin/env python
import sys
import argparse
import itertools

import random

import scipy.stats as stats

import cip_greedy
import minimum_element


OUTPUT_FILE = 'results.txt'


def simulate(Xs_dist):
    return {x: rv.rvs() for x, rv in Xs_dist.iteritems()}


def clip(x, low, high):
    return max(low, min(high, x))


def do_uniform(C, n, m, sims):
    """
    Args:
        C: the cost budget
        n: the number of random variables
        m: the number of elements taken on by the distributions
    """
    with open(OUTPUT_FILE, 'w') as f:
        ties = 0
        cip_victories = 0
        basic_victories = 0
        for _ in xrange(sims):
            Xs_info = {}
            elements = range(0, 5 * m, 5)
            for i in xrange(n):
                x = stats.rv_discrete(
                    values=(elements,
                            [1.0 / len(elements) for _ in xrange(len(elements))]))
                # x = stats.randint(0, m + 1)
                # x = stats.geom(1. / 17)
                # x = stats.poisson(0.6)
                c = random.randint(1, C / (n / 2))
                Xs_info['x' + str(i)] = (x, c, lambda a: x.sf(a))

            f_cost = lambda S: len(S) + 1

            Xs_dist = {k: d for k, (d, _, _) in Xs_info.iteritems()}
            xs = simulate(Xs_dist)

            Xs_cip_info = {k: (c, p) for k, (_, c, p) in Xs_info.iteritems()}
            cip_result = cip_greedy.solve(Xs_cip_info, C, elements, f_cost, 0.01)
            cip_cost = sum(map(lambda x: xs[x], cip_result))
            print 'cip =', cip_cost,

            X_cost = {k: c for k, (_, c, _) in Xs_info.iteritems()}
            basic_result = minimum_element.minimum_element(X_cost, C, f_cost)
            basic_cost = sum(map(lambda x: xs[x], basic_result))
            print ', basic =', basic_cost

            if cip_cost < basic_cost:
                f.write('cip\n')
                cip_victories += 1
            elif cip_cost == basic_cost:
                f.write('tie\n')
                ties += 1
            else:
                f.write('basic\n')
                basic_victories += 1

        f.write('cip: {}, basic: {}, ties: {}\n'.format(
            cip_victories, basic_victories, ties))



def main():

    parser = argparse.ArgumentParser(description='Linear Programming Simulation Application developed by David Xu (davix@seas) and Brian Shi (brishi@seas).')

    parser.add_argument(
            '-C',   '--cost_budget',        type=float,   help='Cost budget for minimum element algorithm [Default: 100]',              default=100)
    parser.add_argument(
            '-n',   '--random_variables',   type=int,     help='Number of random variables [Default: 15]',                              default=15)
    parser.add_argument(
            '-m',   '--distribution_elts',  type=int,     help='The number of elements taken on by the distributions [Default: 20]',    default=20)
    parser.add_argument(
            '-s',   '--simulations',        type=int,     help='Number of simulations to run [Default: 100]',                           default=100)
    parser.add_argument(
            '-o',   '--output_file',        type=str,     help='Name of the output file for the results [Default: "results.txt"]',      default='results.txt')

    args = parser.parse_args()

    global OUTPUT_FILE
    OUTPUT_FILE = args.output_file

    do_uniform(
            args.cost_budget,
            args.random_variables,
            args.distribution_elts,
            args.simulations)


if __name__ == '__main__':
    main()
