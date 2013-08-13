#!/usr/bin/env python

# Copyright 2013 Mitchell Jon Stanton-Cook Licensed under the
# Educational Community License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
#    http://www.osedu.org/licenses/ECL-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
Generate a PBS script to run nesoni on a whole heap of strains
"""

__prog_name__ = 'SeqFindR_nesoni'
__version__ = '0.1'
__description__ = "Generate a nesoni run for SeqFindR"
__author__ = 'Mitchell Stanton-Cook'
__author_email__ = 'm.stantoncook@gmail.com'
__url__ = 'http://github.com/mscook/SeqFindR_nesoni'
__licence__ = 'ECL 2.0'

import os
import sys
import traceback
import argparse
import time
import stat


epi = "Licence: %s by %s <%s>" % (__licence__, __author__,
                                  __author_email__)
prog = __prog_name__.replace(' ', '_')
__doc__ = " %s v%s - %s" % (prog, __version__, __description__)


def get_read_ids(args):
    """
    Return - list of strain IDs, the number of reads and the list of read paths
    """
    ids = []
    with open(os.path.expanduser(args.reads_file)) as fin:
        reads = fin.readlines()
        ori = reads[:]
        if args.paired:
            reads = reads[0::2]
        for e in reads:
            ids.append(e.split('/')[-1].split(args.delim)[0])
    return ids, len(reads), ori


def init_output_dir(output_base):
    """
    Create the output base (if needed) and change dir to it
    """
    if not os.path.exists(output_base):
        os.makedirs(output_base)
    os.chdir(output_base)


def driver(args, num_reads):
    """
    Generate the PBS Driver
    """
    with open("nesoni_SeqFindR.pbs", "w") as fout:
        fout.write("#!/bin/bash\n")
        fout.write(
            "#PBS -l select=1:ncpus=" +
            args.cores +
            ":mem=" +
            args.memory +
            "g:NodeType=medium\n")
        fout.write("#PBS -N nesoni_SeqFindR\n")
        fout.write("#PBS -l walltime=48:00:00\n")
        fout.write("#PBS -J 1-" + str(num_reads) + "\n\n")
        fout.write(
            os.path.join(args.output_base,
                         "nesoni_SeqFindR.$PBS_ARRAY_INDEX"))
    st = os.stat("nesoni_SeqFindR.pbs")
    os.chmod("nesoni_SeqFindR.pbs", st.st_mode | stat.S_IEXEC)


def submit(script):
    """
    Submit the PBS job
    """
    os.system("qsub " + script)


def core(args):
    """
    Generate a PBSPro jobarray for a SeqFindR nesoni run
    """
    if args.paired:
        args.interleaved = False
    ids, num_reads, reads = get_read_ids(args)
    # Make output dir...
    args.output_base = os.path.abspath(os.path.expanduser(args.output_base))
    init_output_dir(args.output_base)
    args.reference_dir = os.path.abspath(
        os.path.expanduser(args.reference_dir))
    # Tidy up refernce dir and get id
    if args.reference_dir.endswith('/'):
        args.reference_dir = reference_dir[:-1]
    ref = args.reference_dir.split('/')[-1].strip()
    # Build the analysis scripts
    i, counter = 0, 0
    while i < num_reads:
        with open("nesoni_SeqFindR." + str(counter + 1), "w") as fout:
            fout.write("cd $TMPDIR\n")
            fout.write("cp -r " + args.reference_dir + " .\n")
            if args.paired:
                r1 = reads[i].split('/')[-1].strip()
                r2 = reads[i + 1].split('/')[-1].strip()
                fout.write("cp " + reads[i].strip() + " .\n")
                fout.write("cp " + reads[i + 1].strip() + " .\n")
                fout.write("nesoni analyse-sample: " + ids[counter] + " " + ref + " pairs: " + r1.split(
                    '/')[-1] + " " + r2.split('/')[-1] + "  --make-cores " + args.cores + 
                    " filter: --monogamous no --random yes\n")
                fout.write("cd " + ids[counter] + " && shopt -s extglob "
                           "&& rm !(consensus.fa) && mv "
                           "consensus.fa " + ids[counter] + "_cons.fa && cd ..\n")
                fout.write(
                    "cp -r " + ids[counter] + " " + args.output_base + "\n")
                i = i + 2
            else:
                r = reads[i].strip()
                fout.write("cp " + reads[i].strip() + " .\n")
                fout.write("nesoni analyse-sample: " + ids[i] + " " + ref + " interleaved: " + r.split(
                    '/')[-1] + "  --make-cores " + args.cores + 
                    " filter: --monogamous no  --random yes\n")
                fout.write("cd " + ids[i] + " && shopt -s extglob "
                           "&& rm !(consensus.fa) && mv "
                           "consensus.fa " + ids[i] + "_cons.fa && cd ..\n")
                fout.write("cp -r " + ids[i] + " " + args.output_base + "\n")
                i = i + 1
        st = os.stat("nesoni_SeqFindR." + str(counter + 1))
        os.chmod(
            "nesoni_SeqFindR." + str(counter + 1),
            st.st_mode | stat.S_IEXEC)
        counter = counter + 1
    driver(args, num_reads)
    submit("nesoni_SeqFindR.pbs")

if __name__ == '__main__':
    try:
        start_time = time.time()
        desc = __doc__.strip()
        parser = argparse.ArgumentParser(description=desc, epilog=epi)
        parser.add_argument('-v', '--verbose', action='store_true',
                            default=False, help='verbose output')
        parser.add_argument('--version', action='version',
                            version='%(prog)s ' + __version__)
        parser.add_argument('-p', '--paired', action='store_true',
                            default=False, help='Paired reads')
        parser.add_argument('-i', '--interleaved', action='store_true',
                            default=True, help=('Interleaved reads '
                                                '[Default = True]'))
        parser.add_argument('-d', '--delim', action='store',
                            default='_', help=('Reads delimiter '
                                                    '[Default = _ ]'))
        parser.add_argument('-c', '--cores', action='store',
                            default='4', help=('CPU cores '
                                                    '[Default = 4]'))
        parser.add_argument('-m', '--memory', action='store',
                            default='11', help=('Memory '
                                                '[Default = 11]'))
        parser.add_argument('reads_file', action='store',
                            type=str, help='Full path to a reads file')
        parser.add_argument('output_base', action='store',
                            type=str, help=('Base location for nesoni '
                                            'output file to go'))
        parser.add_argument('reference_dir', action='store',
                            type=str, help=('Fullpath to the direcory '
                                                    'created by '
                                                    'nesoni make-reference'))
        parser.set_defaults(func=core)
        args = parser.parse_args()
        args.func(args)
        if args.verbose:
            print "Executing @ " + time.asctime()
        if args.verbose:
            print "Ended @ " + time.asctime()
        if args.verbose:
            print 'total time in minutes:',
        if args.verbose:
            print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
