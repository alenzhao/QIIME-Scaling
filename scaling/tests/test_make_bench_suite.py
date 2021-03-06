#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from unittest import TestCase, main

from scaling.make_bench_suite import (get_command_string,
                                      make_bench_suite_files,
                                      make_bench_suite_parameters)


class TestGetCommandString(TestCase):
    """Tests the get_command_string function"""

    def test_get_command_string_single(self):
        """Correctly generates a command with a single input option"""
        cmd = "pick_otus.py"
        base_name = "1000000"
        opts = ['-i']
        values = ['1000000.fna']
        out_opt = "-o"
        obs = get_command_string(cmd, base_name, opts, values, out_opt)
        exp = ("    timing_wrapper.sh $timing_dest/1000000/$i.txt pick_otus.py"
               " -i 1000000.fna -o $output_dest/1000000/$i")
        self.assertEqual(obs, exp)

    def test_get_command_string_multiple(self):
        """Correctly generates a command with multiple input options"""
        cmd = "split_libraries_fastq.py -m mapping.txt"
        base_name = "1000000"
        opts = ['-i', '-b']
        values = ['reads/1000000.fna', 'barcodes/1000000.fna']
        out_opt = "-o"
        obs = get_command_string(cmd, base_name, opts, values, out_opt)
        exp = ("    timing_wrapper.sh $timing_dest/1000000/$i.txt "
               "split_libraries_fastq.py -m mapping.txt -i reads/1000000.fna "
               "-b barcodes/1000000.fna -o $output_dest/1000000/$i")
        self.assertEqual(obs, exp)

    def test_get_command_string_error(self):
        """Correctly raises error if different number of options and values"""
        cmd = "split_libraries_fastq.py -m mapping.txt"
        base_name = "1000000"
        opts = ['-i', '-b']
        values = ['1000000.fna']
        out_opt = "-o"
        self.assertRaises(ValueError, get_command_string, cmd, base_name, opts,
                          values, out_opt)


class TestMakeBenchSuiteFiles(TestCase):
    """Tests the make_bench_suite_files function"""

    def test_make_bench_suite_files_single(self):
        """Correctly generates the benchmark suite for single input option"""
        cmd = "pick_otus.py"
        in_opts = ["-i"]
        bench_files = [["1000000.fna"], ["2000000.fna"], ["3000000.fna"]]
        out_opt = "-o"
        obs = make_bench_suite_files(cmd, in_opts, bench_files, out_opt)
        self.assertEqual(obs, exp_bench_suite_files_single)

    def test_make_bench_suite_files_multiple(self):
        """Correctly generates the bench suite for multiple input options"""
        cmd = "split_libraries_fastq.py -m mapping.txt"
        in_opts = ["-i", "-b"]
        bench_files = [["reads/1000000.fna", "barcodes/1000000.fna"],
                       ["reads/2000000.fna", "barcodes/2000000.fna"],
                       ["reads/3000000.fna", "barcodes/3000000.fna"]]
        out_opt = "-o"
        obs = make_bench_suite_files(cmd, in_opts, bench_files, out_opt)
        self.assertEqual(obs, exp_bench_suite_files_multiple)

    def test_make_bench_suite_files_pbs(self):
        """Correctly generates the bench suite for a pbs environment"""
        cmd = "pick_otus.py"
        in_opts = ["-i"]
        bench_files = [["1000000.fna"], ["2000000.fna"], ["3000000.fna"]]
        out_opt = "-o"
        pbs = True
        job_prefix = "test"
        queue = "friendlyq"
        pbs_extra_args = "-m abe"
        obs = make_bench_suite_files(cmd, in_opts, bench_files, out_opt, pbs,
                                     job_prefix, queue, pbs_extra_args)
        self.assertEqual(obs, exp_bench_suite_files_pbs)


class TestMakeBenchSuiteParameters(TestCase):
    """Tests the make_bench_suite_parameters function"""

    def test_make_bench_suite_parameters_single(self):
        """Correctly generates the benchmark suite for a single parameter"""
        cmd = "parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna"
        params = {"jobs_to_start": ["8", "16", "32"]}
        out_opt = "-o"
        obs = make_bench_suite_parameters(cmd, params, out_opt)
        self.assertEqual(obs, exp_bench_suite_parameters_single)

    def test_make_bench_suite_parameters_multiple(self):
        """Correctly generates the benchmark suite for multiple parameters"""
        cmd = "parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna"
        params = {"jobs_to_start": ["8", "16", "32"],
                  "similarity": ["0.94", "0.97", "0.99"]}
        out_opt = "-o"
        obs = make_bench_suite_parameters(cmd, params, out_opt)
        self.assertEqual(obs, exp_bench_suite_parameters_multiple)

    def test_make_bench_suite_parameters_pbs(self):
        """Correctly genreates the benchmark suite for a pbs environment"""
        cmd = "parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna"
        params = {"jobs_to_start": ["8", "16", "32"],
                  "similarity": ["0.94", "0.97", "0.99"]}
        out_opt = "-o"
        pbs = True
        job_prefix = "test"
        queue = "friendlyq"
        pbs_extra_args = "-m abe"
        obs = make_bench_suite_parameters(cmd, params, out_opt, pbs,
                                          job_prefix, queue, pbs_extra_args)
        self.assertEqual(obs, exp_bench_suite_parameters_pbs)

exp_bench_suite_files_single = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/pick_otus$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/1000000
mkdir $timing_dest/1000000
mkdir $output_dest/2000000
mkdir $timing_dest/2000000
mkdir $output_dest/3000000
mkdir $timing_dest/3000000
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/1000000/$i.txt pick_otus.py -i 1000000.fna -o $output_dest/1000000/$i
    timing_wrapper.sh $timing_dest/2000000/$i.txt pick_otus.py -i 2000000.fna -o $output_dest/2000000/$i
    timing_wrapper.sh $timing_dest/3000000/$i.txt pick_otus.py -i 3000000.fna -o $output_dest/3000000/$i
done

# Get the benchmark results and produce the plots
scaling process-bench-results -i $timing_dest/ -o $dest/plots/ 
"""

exp_bench_suite_files_multiple = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/split_libraries_fastq$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/1000000
mkdir $timing_dest/1000000
mkdir $output_dest/2000000
mkdir $timing_dest/2000000
mkdir $output_dest/3000000
mkdir $timing_dest/3000000
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/1000000/$i.txt split_libraries_fastq.py -m mapping.txt -i reads/1000000.fna -b barcodes/1000000.fna -o $output_dest/1000000/$i
    timing_wrapper.sh $timing_dest/2000000/$i.txt split_libraries_fastq.py -m mapping.txt -i reads/2000000.fna -b barcodes/2000000.fna -o $output_dest/2000000/$i
    timing_wrapper.sh $timing_dest/3000000/$i.txt split_libraries_fastq.py -m mapping.txt -i reads/3000000.fna -b barcodes/3000000.fna -o $output_dest/3000000/$i
done

# Get the benchmark results and produce the plots
scaling process-bench-results -i $timing_dest/ -o $dest/plots/ 
"""

exp_bench_suite_files_pbs = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/pick_otus$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/1000000
mkdir $timing_dest/1000000
mkdir $output_dest/2000000
mkdir $timing_dest/2000000
mkdir $output_dest/3000000
mkdir $timing_dest/3000000
scaling_jobs=""
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    scaling_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/1000000/$i.txt pick_otus.py -i 1000000.fna -o $output_dest/1000000/$i" | qsub -k oe -N test0 -q friendlyq -m abe`
    scaling_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/2000000/$i.txt pick_otus.py -i 2000000.fna -o $output_dest/2000000/$i" | qsub -k oe -N test1 -q friendlyq -m abe`
    scaling_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/3000000/$i.txt pick_otus.py -i 3000000.fna -o $output_dest/3000000/$i" | qsub -k oe -N test2 -q friendlyq -m abe`
done

# Get the benchmark results and produce the plots
scaling_jobs=${scaling_jobs#?}
scaling process-bench-results -i $timing_dest/ -o $dest/plots/ -w $scaling_jobs
"""

exp_bench_suite_parameters_single = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/parallel_pick_otus_uclust_ref$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/jobs_to_start
mkdir $timing_dest/jobs_to_start
mkdir $output_dest/jobs_to_start/8
mkdir $timing_dest/jobs_to_start/8
mkdir $output_dest/jobs_to_start/16
mkdir $timing_dest/jobs_to_start/16
mkdir $output_dest/jobs_to_start/32
mkdir $timing_dest/jobs_to_start/32
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/jobs_to_start/8/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 8 -o $output_dest/jobs_to_start/8/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/16/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 16 -o $output_dest/jobs_to_start/16/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/32/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 32 -o $output_dest/jobs_to_start/32/$i
done

# Get the benchmark results and produce the plots
mkdir $dest/plots
scaling process-bench-results -i $timing_dest/jobs_to_start -o $dest/plots/jobs_to_start 
"""

exp_bench_suite_parameters_multiple = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/parallel_pick_otus_uclust_ref$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/jobs_to_start
mkdir $timing_dest/jobs_to_start
mkdir $output_dest/jobs_to_start/8
mkdir $timing_dest/jobs_to_start/8
mkdir $output_dest/jobs_to_start/16
mkdir $timing_dest/jobs_to_start/16
mkdir $output_dest/jobs_to_start/32
mkdir $timing_dest/jobs_to_start/32
mkdir $output_dest/similarity
mkdir $timing_dest/similarity
mkdir $output_dest/similarity/0.94
mkdir $timing_dest/similarity/0.94
mkdir $output_dest/similarity/0.97
mkdir $timing_dest/similarity/0.97
mkdir $output_dest/similarity/0.99
mkdir $timing_dest/similarity/0.99
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/jobs_to_start/8/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 8 -o $output_dest/jobs_to_start/8/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/16/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 16 -o $output_dest/jobs_to_start/16/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/32/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 32 -o $output_dest/jobs_to_start/32/$i
    timing_wrapper.sh $timing_dest/similarity/0.94/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.94 -o $output_dest/similarity/0.94/$i
    timing_wrapper.sh $timing_dest/similarity/0.97/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.97 -o $output_dest/similarity/0.97/$i
    timing_wrapper.sh $timing_dest/similarity/0.99/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.99 -o $output_dest/similarity/0.99/$i
done

# Get the benchmark results and produce the plots
mkdir $dest/plots
scaling process-bench-results -i $timing_dest/jobs_to_start -o $dest/plots/jobs_to_start 
scaling process-bench-results -i $timing_dest/similarity -o $dest/plots/similarity 
"""

exp_bench_suite_parameters_pbs = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/parallel_pick_otus_uclust_ref$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/jobs_to_start
mkdir $timing_dest/jobs_to_start
mkdir $output_dest/jobs_to_start/8
mkdir $timing_dest/jobs_to_start/8
mkdir $output_dest/jobs_to_start/16
mkdir $timing_dest/jobs_to_start/16
mkdir $output_dest/jobs_to_start/32
mkdir $timing_dest/jobs_to_start/32
mkdir $output_dest/similarity
mkdir $timing_dest/similarity
mkdir $output_dest/similarity/0.94
mkdir $timing_dest/similarity/0.94
mkdir $output_dest/similarity/0.97
mkdir $timing_dest/similarity/0.97
mkdir $output_dest/similarity/0.99
mkdir $timing_dest/similarity/0.99
jobs_to_start_jobs=""
similarity_jobs=""
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    jobs_to_start_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/jobs_to_start/8/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 8 -o $output_dest/jobs_to_start/8/$i" | qsub -k oe -N test0 -q friendlyq -m abe`
    jobs_to_start_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/jobs_to_start/16/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 16 -o $output_dest/jobs_to_start/16/$i" | qsub -k oe -N test1 -q friendlyq -m abe`
    jobs_to_start_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/jobs_to_start/32/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 32 -o $output_dest/jobs_to_start/32/$i" | qsub -k oe -N test2 -q friendlyq -m abe`
    similarity_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/similarity/0.94/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.94 -o $output_dest/similarity/0.94/$i" | qsub -k oe -N test3 -q friendlyq -m abe`
    similarity_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/similarity/0.97/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.97 -o $output_dest/similarity/0.97/$i" | qsub -k oe -N test4 -q friendlyq -m abe`
    similarity_jobs+=","`echo "cd $PWD;     timing_wrapper.sh $timing_dest/similarity/0.99/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.99 -o $output_dest/similarity/0.99/$i" | qsub -k oe -N test5 -q friendlyq -m abe`
done

# Get the benchmark results and produce the plots
mkdir $dest/plots
jobs_to_start_jobs=${jobs_to_start_jobs#?}
similarity_jobs=${similarity_jobs#?}
scaling process-bench-results -i $timing_dest/jobs_to_start -o $dest/plots/jobs_to_start -w $jobs_to_start_jobs
scaling process-bench-results -i $timing_dest/similarity -o $dest/plots/similarity -w $similarity_jobs
"""

if __name__ == '__main__':
    main()
