# -*- coding: utf-8 -*-

# Copyright (c) 2015 William Lees

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from pandas import *
import scipy
import scikits.bootstrap as bootstrap
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import argparse

mean_results = []

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 18}

matplotlib.rc('font', **font)


def main(argv):
    parser = argparse.ArgumentParser(description='Analyse the distribution of MMPBSA/MMGBSA delta G')
    parser.add_argument('infile', help='input file containing energy totals (CSV format)')
    parser.add_argument('sumfile', help='summary file (text format)')
    parser.add_argument('trendfile', help='trend plot with confidence intervals (.png, .bmp, .pdf)')
    parser.add_argument('distfile', help='distribution plot of energy totals (.png, .bmp, .pdf)')
    args = parser.parse_args()
    
    global mean_results
    
    font = FontProperties()
    font.set_name('Calibri')
    font.set_size(18)
    
    means = read_csv(args.infile)
    results_m = []
    results_u = []
    results_l = []
    xs = []
    
    with open(args.sumfile, 'w') as fo:
        for i in range(5, len(means)+5, 5):
            mean_results = []
            bounds = conf_intervals(means["TOTAL"][:i])
            fo.write("%d mean %0.2f +%0.2f -%0.2f\n" % (i, bounds[0], bounds[1], bounds[2]))
            results_m.append(bounds[0])
            results_u.append(bounds[1]+bounds[0])
            results_l.append(bounds[2]+bounds[0])
            xs.append(i)

        plt.plot(xs, results_m, color='g')
        plt.plot(xs, results_u, linestyle='--', color='g')
        plt.plot(xs, results_l, linestyle='--', color='g')
        plt.xlabel(u'Samples', fontproperties=font)
        plt.ylabel(u'\u0394G (kcal/mol)', fontproperties=font)  
        plt.savefig(args.trendfile)
    
    pdmeans = Series(mean_results)
    
    lim_l = round(bounds[0] - 2.5, 0)
    
    plt.xlim(lim_l, lim_l+5)
    plt.ylim(0, 900)
    plt.xlabel(u'Bootstrapped mean \u0394G (kcal/mol)', fontproperties=font)
    plt.ylabel(u'Frequency', fontproperties=font)  
    plt.hist(pdmeans, bins=50)
    plt.savefig(args.distfile)


def conf_intervals(data):
	mean = scipy.mean(data)
	CIs = bootstrap.ci(data=data, statfunction=mymean)
	ubound = CIs[1]-mean
	lbound = CIs[0]-mean
	return(mean, ubound, lbound)
  
def mymean(data):
    global mean_results
    res = scipy.mean(data)
    mean_results.append(res)
    return res

if __name__ == "__main__":
    main(sys.argv)
