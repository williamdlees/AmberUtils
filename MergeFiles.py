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

# Merge n files so that the first line of each file comes first in thee merged file, then the second and so on

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

import sys

def main(argv):
    if len(argv) < 4:
        print "usage: MergeFiles.py <input files> <output file>."
        sys.exit(0)

    num_files = len(argv) - 2    
    contents = []
    
    for i in range(0, num_files):
      contents.append([])
      with open(argv[i+1], "r") as f:
          l = 0
          for line in f:
            if l > 0 or i == 0:  
              contents[i].append(line.rstrip('\n'))
            l += 1
    
    with open(argv[len(argv)-1], "w") as f:
        done = False
        j = 0
        while not done:
            done = True
            for i in range(0, num_files):
                if len(contents[i]) > j:
                    f.write(contents[i][j] + '\n')
                    done = False
            j = j + 1


if __name__ == "__main__":
    main(sys.argv)
