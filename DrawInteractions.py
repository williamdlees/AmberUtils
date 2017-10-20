#! /usr/bin/env python

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

__author__ = 'William Lees'
__docformat__ = "restructuredtext en"

# Draw a residue interaction chart
# The control file specifies the residues to show on the chart. These are divided into columns
# and each column will contain the indicated residues in the order in which they are listed in the control file.
# Interactions will follow those listed in the decomp table. Line thicknesses will mirror the interaction energy
# from the decomp table. 

# Control file is csv format with the collowing columns:
# Col - number of the column in which this residue should be placed (1,2,3..)
# Id  - identifier of this residue in the decomp table
#     - can be 'Gap' to create a gap between residues
# Legend - legend for this residue in the interaction chart
#     - a + in front of the Legend will force the residue to be shown even if it has no interaction energy and -o is specified
# Fill - The colour for the residue on the interaction chart
#        This can be 'Hydro' to use the built-in hydrophobicity scale, or any colour specifier supported by matplotlib
#        (e.g. 'g', 'green', '#00FFFF')


import argparse
import csv
import math
import sys

import cairo
import matplotlib.colors as mc
from PIL import Image

# Dimensions in pixels - can be altered at will, but the underlying software library does impose some limits on maximum sizes.

WIDTH, HEIGHT = 1500,3000

RES_RADIUS = 60
COL_SPACING = 400
RES_Y_SPACING = 80
MARGIN = 100
FONT_SIZE = 24
DASH_SIZE = 10

res_codes = {}
res_codes['ALA'] = 'A'
res_codes['ARG'] = 'R'
res_codes['ASN'] = 'N'
res_codes['ASP'] = 'D'
res_codes['CYS'] = 'C'
res_codes['CYX'] = 'C'
res_codes['GLU'] = 'E'
res_codes['GLN'] = 'Q'
res_codes['GLY'] = 'G'
res_codes['HIS'] = 'H'
res_codes['HIE'] = 'H'
res_codes['HID'] = 'H'
res_codes['HIP'] = 'H'
res_codes['ILE'] = 'I'
res_codes['LEU'] = 'L'
res_codes['LYS'] = 'K'
res_codes['MET'] = 'M'
res_codes['PHE'] = 'F'
res_codes['PRO'] = 'P'
res_codes['SER'] = 'S'
res_codes['THR'] = 'T'
res_codes['TRP'] = 'W'
res_codes['TYR'] = 'Y'
res_codes['VAL'] = 'V'

res_singles = 'ARNDCEQGHILKMFPSTWYV'


def main(argv):
    parser = argparse.ArgumentParser(description='Plot residue interactions.')
    parser.add_argument('control', help='control file')
    parser.add_argument('decomp', help='decomp table produced by PairwiseDecompTable')
    parser.add_argument('hbonds', help='consolidated hbond file produced by ConsolidateHbonds')
    parser.add_argument('thresh', help='minimum threshold for hbonds')
    parser.add_argument('output', help='output file (PDF)')
    parser.add_argument('summary', help='summary file (CSV)')
    parser.add_argument('-o', '--omit_none', help='omit residues with no significant interaction energy', action='store_true')
    parser.add_argument('-c', '--compare_file', help='only display interactions that differ from those in this file')
    parser.add_argument('-t', '--compare_thresh', help='threshold for comparison (default 0.5 kcal/mol)')
    parser.add_argument('-x', '--omit_same_col', help='do not show interactions between residues in the same column', action='store_true')
    parser.add_argument('-l', '--add_title', help='add title to diagram')
    parser.add_argument('-p', '--png', help='output as png image', action='store_true')
    args = parser.parse_args()

    compare_thresh = 0.5 if args.compare_thresh is None else float(args.compare_thresh)

    surface = cairo.PDFSurface(args.output, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_font_size(FONT_SIZE)
    cols = {}
    residue_ids = []
    col_ids = []
    read_control_file(args.control, col_ids, cols, residue_ids)

    energies = {}
    res_with_energy = []
    read_decomp_file(args.decomp, energies, res_with_energy, residue_ids, False)

    if args.compare_file:
        comp_energies = {}
        comp_res_with_energy = []
        read_decomp_file(args.compare_file, comp_energies, comp_res_with_energy, residue_ids, True)

    hbonds = {}
    read_hbond_file(args.hbonds, energies, hbonds, args.thresh)

    # Remove interactions within a single column, if requested

    if args.omit_same_col:
        energies, res_with_energy = remove_single_column(col_ids, cols, energies)
        if args.compare_file:
            comp_energies, comp_res_with_energy = remove_single_column(col_ids, cols, comp_energies)

    # If there's a compare file, only keep the energies that change more than the threshold

    negatives = []

    if args.compare_file:
        res_with_energy = []
        new_energies = {}
        for k, v in energies.items():
            (r1, r2, energy) = v
            if k in comp_energies:
                diff = abs(abs(energy) - abs(comp_energies[k][2]))
                if diff >= compare_thresh:
                    new_energies[k] = (r1, r2, diff)
                    for r in (r1, r2):
                        if r not in res_with_energy:
                            res_with_energy.append(r)
                    if comp_energies[k][2] < energy:
                        negatives.append((r1 + r2))
            elif abs(energy) >= compare_thresh:
                new_energies[k] = (r1, r2, energy)
                for r in (r1, r2):
                    if r not in res_with_energy:
                        res_with_energy.append(r)
        for k,v in comp_energies.items():
            if k not in energies:
                if abs(v[2]) >= compare_thresh:
                    new_energies[k] = v
                    (r1, r2, _) = v
                    for r in (r1, r2):
                        if r not in res_with_energy:
                            res_with_energy.append(r)
                    negatives.append(r1 + r2)
        energies = new_energies

    # Remove residues we don't want to display

    if args.omit_none:
        for col_id in col_ids:
            new_col = []
            for res in cols[col_id]:
                if 'Gap' in res['Id'] or res['Id'] in res_with_energy or '+' in res['Legend']:
                    new_col.append(res)
                cols[col_id] = new_col

    global BIGGEST_CHANGE
    if args.compare_file:
        BIGGEST_CHANGE = get_biggest_change(new_energies)
    else:
        BIGGEST_CHANGE = 0.0

    locations = plot_interactions(col_ids, cols, ctx, energies, hbonds, surface, negatives)

    if(args.add_title):
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(100,80)
        ctx.show_text(args.add_title)

        subtitle = ""
        subtitle = subtitle + "(" + args.compare_thresh + " kcal/mol"
        if args.compare_file:
            subtitle = subtitle + ", " + args.compare_file +")"
        else:
            subtitle = subtitle + ")"
        ctx.set_font_size(FONT_SIZE-10)
        ctx.move_to(100,95)
        ctx.show_text(subtitle)

    if args.png:
        surface.write_to_png(args.output.split(".")[0] + ".png")
        img = Image.open(args.output.split(".")[0] + ".png")
        background = Image.new('RGBA', img.size, (255, 255, 255,1000))
        out_image = Image.alpha_composite(background, img)
        out_image = out_image.crop(img.getbbox())
        out_image.save(args.output.split(".")[0] + ".png")

    surface.finish()
    surface.flush()

    write_summary_file(args.summary, col_ids, cols, energies, locations)


def remove_single_column(col_ids, cols, energies):
    res_with_energy = []
    new_energies = {}
    for k, v in energies.items():
        (r1, r2, energy) = v
        if find_col(r1, cols, col_ids) != find_col(r2, cols, col_ids):
            new_energies[k] = v
            for r in (r1, r2):
                if r not in res_with_energy:
                    res_with_energy.append(r)
    energies = new_energies
    return energies, res_with_energy


def write_summary_file(summary, col_ids, cols, energies, locations):
    with open(summary, 'wb') as fo:
        writer = csv.writer(fo, delimiter=',')
        writer.writerow(['Column', 'Chain', 'Residue', 'Total'])
        for col_id in col_ids:
            for res in cols[col_id]:
                if 'Gap' not in res['Id']:
                    total = 0.
                    legend = res['Legend'].replace('+', '')
                    for k, v in energies.items():
                        (r1, r2, e) = v
                        if (r1 == res['Id'] or r2 == res['Id']) and locations[r1][0] != locations[r2][0]:
                            total += e
                    writer.writerow([col_id, res['Chain'], legend, total])
                else:
                    writer.writerow(['', '', ''])


def plot_interactions(col_ids, cols, ctx, energies, hbonds, surface, negatives):
    # Work out the longest column, so that we can centre
    max_res = 0
    for col_id in col_ids:
        max_res = max(max_res, len(cols[col_id]))
    centre_y = MARGIN + RES_RADIUS + RES_Y_SPACING * max_res / 2

    # Plot the residues
    locations = {}
    for col_id in col_ids:
        x = MARGIN + RES_RADIUS + col_id * COL_SPACING
        y = centre_y - len(cols[col_id]) * RES_Y_SPACING / 2

        for res in cols[col_id]:
            if 'Gap' not in res['Id']:
                legend = res['Legend'].replace('+', '')
                draw_residue(ctx, x, y, legend, res['Fill'], res['Chain'])
            locations[res['Id']] = (x, y)
            y += RES_Y_SPACING

    # Plot the interactions
    for k, v in energies.items():
        (r1, r2, e) = v
        colour = 'red' if r1 + r2 in hbonds else 'black'
        dashed = (r1 + r2 in negatives)
        connect_residue(ctx, locations[r1], locations[r2], abs(e), colour, dashed)
    surface.flush()
    return locations


def read_hbond_file(hbond_file, energies, hbonds, thresh):
    with open(hbond_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if int(row[2]) >= int(thresh):
                if row[1] < row[0]:
                    key = row[1] + row[0]
                else:
                    key = row[0] + row[1]

                if key not in energies:
                    print 'Warning: hbond between %s and %s but no corresponding energy value.' % (row[0], row[1])
                else:
                    hbonds[key] = row[2]


def read_decomp_file(decomp, energies, res_with_energy, residue_ids, is_compare_file):
    warned = []
    subs = {}
    
    with open(decomp, 'r') as f:
        reader = csv.DictReader(f)
        for res in reader.fieldnames:
            if res != 'Res' and res not in residue_ids:
                num = int(res.split()[1])
                for residue_id in residue_ids:
                    if 'Gap' not in residue_id:
                        nid = residue_id.split()[1]
                        if int(nid) == num:
                            if is_compare_file:
                                subs[res] = residue_id
                            else:
                                print 'Warning: control file id %s does not agree with decomp table id %s' % (residue_id, res)


        for row in reader:
            res1 = row['Res']
            if res1 in subs:
                res1 = subs[res1]
            for res2, energy in row.items():
                if res2 in subs:
                    res2 = subs[res2]
                if res2 != 'Res' and res2 != res1 and energy != '':
                    if res1 in residue_ids and res2 in residue_ids:
                        if res2 < res1:
                            energies[res2 + res1] = (res2, res1, float(energy))
                        else:
                            energies[res1 + res2] = (res1, res2, float(energy))
                        for r in (res1, res2):
                            if r not in res_with_energy:
                                res_with_energy.append(r)
                    else:
                        for r in (res1, res2):
                            if r not in residue_ids and r not in warned:
                                print 'Warning: %s has interaction energies but is not listed in the control file.' % r
                                warned.append(r)


def read_control_file(control, col_ids, cols, residue_ids):
    gapcount = 1  # used to make 'Gap' ids unique by adding a suffix
    with open(control, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            col_id = int(row['Col'])
            if col_id not in col_ids:
                cols[col_id] = []
                col_ids.append(col_id)
            cols[col_id].append(row)
            if row['Id'] == 'Gap':
                row['Id'] = 'Gap_%d' % gapcount
                gapcount += 1
            if row['Legend'][:1].isdigit():
                row['Legend'] = res_codes[row['Id'].split()[0]] + row['Legend']
            check_res(row['Id'], row['Legend'])
            residue_ids.append(row['Id'])


def draw_residue(ctx, x, y, text, colour, chain):
    ctx.set_source_rgb (*colour_residue(text, colour))
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(RES_RADIUS, RES_RADIUS / 2.)
    #ctx.arc(x, y, RES_RADIUS, 0, 2*math.pi)
    ctx.arc(0., 0., 1., 0., 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.set_source_rgb (0, 0, 0)
    (x_bearing, y_bearing, add_width, height, x_advance, y_advance) = ctx.text_extents("W")
    (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(text)
    ctx.move_to(x-(width+add_width)/2, y+height/2)
    ctx.show_text(chain + ':' + text)
    #ctx.rectangle(x-width/2-2, y-height/2-2, width+4, height+4)
    ctx.stroke()
 
    
def connect_residue(ctx, loc1, loc2, width, colour, dash):

    (x1, y1) = loc1
    (x2, y2) = loc2




    if x1 == x2:
        pass
    
    if x1 > x2:
        (x1, y1, x2, y2) = (x2, y2, x1, y1)
        
    if x1 < x2:
        start_x = x1 + RES_RADIUS
        start_y = y1
        end_x = x2 - RES_RADIUS
        end_y = y2
    else:               # same row
        start_x = x1
        end_x = x1
        start_y = min(y1, y2) + RES_RADIUS/2
        end_y = max(y1, y2) - RES_RADIUS/2
    
    if dash:
        ctx.set_dash([DASH_SIZE])
    else:
        ctx.set_dash({})
        
    ctx.move_to(start_x, start_y)
    ctx.set_line_width (width)
    ctx.set_source_rgb(*mc.colorConverter.to_rgb(colour)) 
    ctx.line_to(end_x, end_y)
    ctx.stroke()
    # add label with value of change for largest chang
    if width == math.fabs(BIGGEST_CHANGE):
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_font_size(FONT_SIZE - 10)
        x_bearing1, y_bearing1, width1, height1 = ctx.text_extents(str(BIGGEST_CHANGE))[:4]
        ctx.move_to((x1 + x2 - (width1 + 15 / 2)) / 2, (y1 + y2 - (height1 + 5 / 2)) / 2)
        ctx.show_text(str(BIGGEST_CHANGE))
    
    

# Remove the number from the name. If that leaves a three-letter residue, translate to a single letter
# Invalid codes translate to X
    
def decode_res(res):
    letters = list(res.upper())
    ret = ''
    for l in letters:
        if l.isalpha():
            ret += l
    
    if len(ret) == 4 or len(ret) == 2:           # we probably have an inserted residue, eg P52A
        ret = ret[:-1]
            
    if ret in res_codes:
        ret = res_codes[ret]
        
    if len(ret) != 1 or ret not in res_singles:
        ret = 'X'
        
    return ret

res_colours = {}
res_colours['#FF0000'] = 'FIWLVM'
res_colours['#FF8080'] = 'YCA'
res_colours['#00FF00'] = 'THGSQ'
res_colours['#00FFFF'] = 'RKNEPD'
    
def colour_residue(res, code):
    if code == 'Hydro':
        res = decode_res(res)
        code = 'black'
        for c,v in res_colours.items():
            if res in v:
                code = c
                
    return mc.colorConverter.to_rgb(code)

# Check residue in location is in line with single letter residue in legend

def check_res(id, legend):
    if 'Gap' in id:
        return
    leg = decode_res(legend)
    if leg == 'X':
        print 'Warning: invalid residue code in (%s, %s)' % (id, legend)
        return
    
    loc = id.split()[0]
    if loc not in res_codes:
        print 'Warning: invalid location code in (%s, %s)' % (id, legend)
        return
    
    if res_codes[loc] != leg:
        print 'Warning: three-letter and single-letter codes do not agree in (%s, %s)' % (id, legend)

# Find the column containing a residue

def find_col(res, cols, col_ids):
    for col_id in col_ids:
        for r in cols[col_id]:
            if r['Id'] == res:
                return col_id
    return None

def get_biggest_change(new_energies):
    biggest = 0.0
    smallest = 0.0
    for item in new_energies.values():
        if item[2] > biggest:
            biggest = item[2]
        if item[2] < smallest:
            smallest = item[2]

    if math.fabs(biggest) > math.fabs(smallest):
        return biggest
    else:
        return smallest



if __name__ == "__main__":
    main(sys.argv)
