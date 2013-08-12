Generate mapping consensus data for SeqFindR
============================================

Generate PBS jobs given the inputs to SeqFindR_nesoni and submits the jobs.

Assumes
    * Have access to a cluster running PBSPro,
    * Have Nesoni installed on the cluster and
    * Have python >= 2.7

We use the database file (in multi-fasta format) as the reference. 

The workflow is something like this::

    $ nesoni make-reference myref ref-sequences.fa
    $ ./SeqFindR_nesoni /path/to/reads/reads.dat /path/to/output/directory /path/to/mref/directory
    649527[].paroo3
    Warning : Job array will run for 0 days.

For each sample we then extract the consensus.fa file which we term the mapping
consensus. This file is a multi-fasta file of the consensus base calls relative
to the database sequences.


What does reads.dat look like?
------------------------------

For interleaved (default)::
    
    /path/to/rx.compression
    /path/to/ry.compression
    /path/to/rz.compression

For paired (-p)::

    /path/to/rx_1.compression
    /path/to/rx_2.compression
    /path/to/ry_1.compression
    /path/to/ry_2.compression
    /path/to/rz_1.compression
    /path/to/rz_1.compression


Usage
-----

Something like this::
    
    ./SeqFindR_nesoni -h
    usage: SeqFindR_nesoni [-h] [-v] [--version] [-p] [-i] [-d DELIM] [-c CORES]
                           [-m MEMORY]
                           reads_file output_base reference_dir

    SeqFindR_nesoni v0.1 - Generate a nesoni run for SeqFindR

    positional arguments:
      reads_file            Full path to a reads file
      output_base           Base location for nesoni output file to go
      reference_dir         Fullpath to the direcory created by nesoni make-
                            reference

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output
      --version             show program's version number and exit
      -p, --paired          Paired reads
      -i, --interleaved     Interleaved reads [Default = True]
      -d DELIM, --delim DELIM
                            Reads delimiter [Default = _ ]
      -c CORES, --cores CORES
                            CPU cores [Default = 4]
      -m MEMORY, --memory MEMORY
                            Memory [Default = 11]

    Licence: ECL 2.0 by Mitchell Stanton-Cook <m.stantoncook@gmail.com>


Caveats
-------

The (poor) alignment of reads at the start and the end of the database genes 
can result in N calls. This can result in downstream false negatives. We are 
currently working on solution to this.
