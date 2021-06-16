#!/usr/bin python2.7
# -*- coding: utf-8 -*-
# @Author: fengyq
# @Date:   2020-10-26 11:17:08
# @Last Modified by:   fengpku
# @Last Modified time: 2020-11-04 21:46:21
## Python version 2.7

from __future__ import print_function
import os
import re
import gzip
import itertools
import argparse

__author__ = 'FYQ'

# remove the linker in hichip fastq files.

def fq(file):
    ## check if the file exist in the folder
    if not os.path.isfile(file):
        raise FileNotFoundError("File %s not found!"%file)
    ## read fastq file
    if re.search('.gz$', file):
        fastq = gzip.open(file, 'r')
    else:
        fastq = open(file, 'r')
    with fastq as f:
        while True:
            l1 = f.readline()
            if not l1:
                break
            l2 = f.readline()
            l3 = f.readline()
            l4 = f.readline()
            yield [l1, l2, l3, l4]  ## read in 4 lines in 1 cycle.

# split merged read by linker
def linker_remove(read1, read2, read1_out,read2_out):

    # Create new r1 FASTQs
    r1_new_file = read1_out
    r1_splited = open(r1_new_file, 'w')
    # Create new r2 FASTQs
    r2_new_file = read2_out
    r2_splited = open(r2_new_file, 'w')
    # count the reads in paired fastq
    L1=0
    L2=0
    L4=0
    L5=0
    L6=0
    L8=0
    for r1,r2 in itertools.izip(fq(read1), fq(read2)):  ## iteration
    # read1
        # get read id in the header, replace with short id, reduce size
        r1_id=r1[0].replace('GWNJ-0965:633:GW2007273281','',1)
        # get the linker location
        linker_pos=re.search('^[ACGT]{0,6}TATCTTATCTGACAG.|^[AGCT]{0,6}AGATAAGATATCGCG.|.CGCGATATCTTATCT[AGCT]{0,6}$|.CTGTCAGATAAGATA[AGCT]{0,6}$',r1[1])
        if not linker_pos:
            L1=L1+1
            r1_seq=r1[1]
            r1_qual=r1[3]
        # if there is a linker, remove the linker_qual from quality line
        elif len(linker_pos.span())==2:
            L2=L2+1
            r1_seq="".join([r1[1][0:linker_pos.start()],r1[1][linker_pos.end():]])
            r1_qual="".join([r1[3][0:linker_pos.start()],r1[3][linker_pos.end():]])
        else:
            r1_seq=r1[1]
            r1_qual=r1[3]
            print('Read {} have >2 linkers \n'.format(r1[0]))

        r1_new=[r1_id,r1_seq,"+\n",r1_qual]
        L4=L4+1

        for line in r1_new:
            r1_splited.write(line)

    # read2
        # get read id in the header
        r2_id=r2[0].replace('GWNJ-0965:633:GW2007273281','',1)
        # get the linker location : re.search()  return the 1st match
        # re.findall() return all matches
        linker_pos2=re.search('^[ACGT]{0,6}TATCTTATCTGACAG.|^[AGCT]{0,6}AGATAAGATATCGCG.|.CGCGATATCTTATCT[AGCT]{0,6}$|.CTGTCAGATAAGATA[AGCT]{0,6}$',r2[1])
        if not linker_pos2:
            L5=L5+1
            r2_seq=r2[1]
            r2_qual=r2[3]
        # if there is a linker, remove the linker_qual from quality line
        elif len(linker_pos2.span())==2:
            L6=L6+1
            r2_seq="".join([r2[1][0:linker_pos2.start()],r2[1][linker_pos2.end():]])
            r2_qual="".join([r2[3][0:linker_pos2.start()],r2[3][linker_pos2.end():]])
        else:
            r2_seq=r2[1]
            r2_qual=r2[3]
            print('Read {} have >2 linkers \n'.format(r2[0]))

        r2_new=[r2_id,r2_seq,"+\n",r2_qual]
        L8=L8+1
        for line in r2_new:
            r2_splited.write(line)


    # double check the read numbers
    print (' number of reads in fq1 and fq2 have no linkers at their ends : {} VS {}\n'.format(L1,L5))
    print (' number of reads in fq1 and fq2 have 1 linker at their ends : {} VS {}\n'.format(L2,L6))
    print (' number of reads in fq1 and fq2 : {} VS {}\n'.format(L4,L8))

    r1_splited.close()
    r2_splited.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r1', '--read1', required=True,help="read1 input, fq or fq.gz")
    parser.add_argument('-r2', '--read2', required=True,help="read2 input, fq or fq.gz")
    parser.add_argument('-R1', '--read1_out', required=True,help="Read1 output")
    parser.add_argument('-R2', '--read2_out', required=True,help="Read2 output")
    args = vars(parser.parse_args())
    linker_remove(args['read1'], args['read2'],args['read1_out'], args['read2_out'])


if __name__ == '__main__':
    main()
