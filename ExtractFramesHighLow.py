#! /usr/bin/env python

# Copyright (c) 2017 Martin Rosellen

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

import argparse
import operator
import sys


def main(argv):
    parser = argparse.ArgumentParser(description='Creates cpptraj input files to extract high and low energy frames.')
    parser.add_argument('energies', help='file with energies created by ExtractMMPBSATotals.py (e.g. out.csv)')
    parser.add_argument('number', help='number of frames that should be extracted')
    parser.add_argument('-w', '--low', help='low energy cpptraj file (default: low_energy_frames.cpptraj)')
    parser.add_argument('-i', '--high', help='high energy cpptraj (default: high_energy_frames.cpptraj)')
    parser.add_argument('-l', '--low_traj', help='file name of trajectory for low energy frames(default: '
                                                 'low_energy_frames.nc')
    parser.add_argument('-t', '--high_traj', help='file name of trajectory for high energy frames(default: '
                                                  'high_energy_frames.nc')
    parser.add_argument('-s', '--summary', help='frame numbers with according energy values (default: high_low.txt)')
    args = parser.parse_args()

    n_frames = int(args.number)

    if args.summary:
        summary = args.summary
    else:
        summary = 'high_low.txt'

    if args.low:
        low_out = args.low
    else:
        low_out = 'low_energy_frames.cpptraj'

    if args.high:
        high_out = args.high
    else:
        high_out = 'high_energy_frames.cpptraj'

    if args.low_traj:
        low_traj = args.low_traj
    else:
        low_traj = 'low_energy_frames.nc'

    if args.high_traj:
        high_traj = args.high_traj
    else:
        high_traj = 'high_energy_frames.nc'

    with open(args.energies, 'r') as f:
        content = f.readlines()
    energies = [float(item) for item in content[1:]]

    frames = {}
    for i in range(0, len(energies)):
        frames[i+1] = energies[i]

    frames = sorted(frames.items(), key=operator.itemgetter(1))

    low = sorted(frames[:n_frames])
    high = sorted(frames[-n_frames:])

    with open(summary, 'w') as s:
        s.write("High energy frames:\n")
        for key, val in high:
            s.write(str(key) + "," + str(val) + "\n")

        s.write("\nLow energy frames:\n")
        for key, val in low:
            s.write(str(key) + "," + str(val) + "\n")

    low_frames = [str(item[0]) for item in low]
    low_frames = ','.join(low_frames)

    with open(low_out, 'w') as l:
        l.write("trajout " + low_traj + " mdcrd onlyframes " + low_frames + "\ngo")

    high_frames = [str(item[0]) for item in high]
    high_frames = ','.join(high_frames)

    with open(high_out, 'w') as l:
        l.write("trajout " + high_traj + " mdcrd onlyframes " + high_frames + "\ngo")


if __name__ == "__main__":
    main(sys.argv)
