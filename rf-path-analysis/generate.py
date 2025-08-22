#!/usr/bin/env python

import sys
import csv
import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('summitscsv') # input file path for downloaded summitslist.csv with the first line stripped
parser.add_argument('outcsv') # output file path for updated summitslist.csv with propagation values
parser.add_argument('splatpath')
parser.add_argument('homeqthfile') # path of *.qth file to use for home location
parser.add_argument('summitqthdir') # path of directory to put generated *.qth for summit locations in. will be in nested subdirectory by $summitqthdir/$association/$region/
parser.add_argument('terrdir') # path of directory containing *.sdf terrain files
parser.add_argument('outdir') # path of directory to put output files in. will be in nested subdirectory by $outdir/$association/$region/
parser.add_argument('-r', '--region') # only do this region to save time
args = parser.parse_args()

args.homeqthfile = args.homeqthfile.lstrip('./') # fixup - if './' is included in the transmitter qth path, splat will fail to find the *.lrp file (which it expects to have the same basename and be in the same directory)

qth_template = '''{}
{:f}
{:f}
{:f}'''

with open(args.summitscsv, 'r') as inf, open(args.outcsv, 'w') as outf:
    rd = csv.DictReader(inf)
    fn = rd.fieldnames
    fn.append('FreeSpacePathLoss')
    fn.append('OverallPathLoss')
    fn.append('TerrainPathLoss')
    fn.append('RxSignalPower')
    fn.append('PropagationMode')
    wt = csv.DictWriter(outf, fn)
    wt.writeheader()

    for row in rd:
        code = row['SummitCode']
        assoc,rest = code.split('/')
        reg,sid = rest.split('-')
        if args.region and reg != args.region:
            continue # skip this summit
        lat = float(row['Latitude'])
        long = float(row['Longitude'].strip('-'))
        name = row['SummitName']

        # make a *.qth file using lat, lon, name, 5ft AGL
        qth = qth_template.format(name, lat, long, 5.0)
        qthfile = os.path.join(args.summitqthdir, assoc, reg, f'{sid}.qth')
        with open(qthfile, 'w') as qf:
            qf.write(qth)

        # use same apt.lrp file for each, output will then be "apartment-to-XXXXXX.txt"

        # shell out to run splat-hd
        cmd = [args.splatpath, '-t', args.homeqthfile, '-r', qthfile, '-d', args.terrdir, '-H', sid]
        subprocess.run(cmd)

        # organize output? maybe W7W folder, then folder for each region, and keep to.txt, H.png for each
        outpath = os.path.join(args.outdir, assoc, reg)
        cmd = f'mv apartment-to-*.txt {outpath}/{sid}.txt' # TODO don't hardcode "apartment" name, read from first line of homeqthfile
        subprocess.run(cmd, shell=True)
        cmd = f'mv {sid}.png {outpath}/'
        subprocess.run(cmd, shell=True)

        # read the text file to determine values of interest
        print(outpath)
        print(sid)
        with open(f'{outpath}/{sid}.txt', 'r', encoding='latin') as of:
            for line in of:
                if "Free space path loss" in line:
                    fspl = float(line.split(':')[1].split(' ')[1])
                elif "ITWOM Version 3.0 path loss" in line:
                    opl = float(line.split(':')[1].split(' ')[1])
                elif "Attenuation due to terrain shielding" in line:
                    tpl = float(line.split(':')[1].split(' ')[1])
                elif "Signal power level at" in line:
                    rsp = float(line.split(':')[1].split(' ')[1])
                elif "Mode of propagation" in line:
                    pm = line.split(':')[1].strip(' \n')
                    break # this is expected to be ordered last, don't bother reading the rest of the file lines

        # then save values of interest back to the csv
        row['FreeSpacePathLoss'] = fspl
        row['OverallPathLoss'] = opl
        row['TerrainPathLoss'] = tpl
        row['RxSignalPower'] = rsp
        row['PropagationMode'] = pm
        wt.writerow(row)

