import difflib
import argparse
import sys


def main(argv):
    parser = argparse.ArgumentParser(description='Compare two text files and report differences')
    parser.add_argument('file1', help='file 1')
    parser.add_argument('file2', help='file 2')
    args = parser.parse_args()

    l1 = open(args.file1, 'r').readlines()
    l2 = open(args.file2, 'r').readlines()

    differences = False
    d = difflib.Differ()
    diff = d.compare(l1, l2)
    for line in diff:
        if line[0] != ' ':
            print line
            differences = True
            
    if differences:
        print '\n*******ERROR*******     Differences were found.'

if __name__ == "__main__":
    main(sys.argv)
