import sys
import os
import re
import logging
import subprocess
import math
import signal
import argparse
import datetime
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s :: %(levelname)s :: %(message)s',
    #> 2019-02-17 11:40:38,254 :: INFO :: job done!
    stream=sys.stdout
    file='sample.log') # log to a file instead of the console
# https://www.machinelearningplus.com/python-logging-guide/
log = logging.getLogger(__name__)

def get_ticks():
    """Returns time.
    # str(datetime.now())
    """
    t=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return  t
# get_ticks()

"""
1. complicated version run shell in python
"""
def run_shell_cmd(cmd):
    p = subprocess.Popen(
        ['/bin/bash', '-o', 'pipefail'],  # to catch error in pipe
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
        #preexec_fn=os.setsid)  # to make a new process with a new PGID
        start_new_session=True) # replace preexec_fn
    pid = p.pid # PID - Process ID
    pgid = os.getpgid(pid) # PGID - Process Group ID
    log.info('run_shell_cmd: PID={}, PGID={}, CMD={}'.format(pid, pgid, cmd))

    t0 = get_ticks() # start time
    stdout, stderr = p.communicate(cmd) # communicate() returns a tuple (stdout_data, stderr_data).
    rc = p.returncode # execution status
    t1 = get_ticks() # end time
    err_str = ('PID={pid}, PGID={pgid}, RC={rc}, DURATION_SEC={dur:.1f}\n''STDERR={stde}\nSTDOUT={stdo}').format(
                pid=pid, pgid=pgid, rc=rc, dur=t1 - t0, stde=stderr.strip(), stdo=stdout.strip())
    if rc: # A None value indicates that the process hasn’t terminated yet.
        # kill all child processes
        try:
            os.killpg(pgid, signal.SIGKILL)
        except:
            pass
        finally:
            raise Exception(err_str)
    else:
        log.info(err_str)
    return stdout.strip('\n')

# example usage of run_shell_cmd
def trim_fastq(fastq, trim_bp, out_dir):
    prefix = os.path.join(out_dir, os.path.basename(strip_ext_fastq(fastq)))
    trimmed = '{}.trim_{}bp.fastq.gz'.format(prefix, trim_bp)
    cmd = 'python $(which trimfastq.py) {0} {1} | gzip -nc > {0}'.format(fastq, trim_bp, trimmed)
    run_shell_cmd(cmd)


"""
2. simple version run shell in python
"""
def sort_bam(input_bam, output_prefix):
    """Calls samtools sort on input_bam filename and writes to
    output_bam."""
    output_bam = output_prefix + ".sort.bam"
    cmd = "samtools sort -o " + output_bam + " " + input_bam
    sys.stderr.write("running command: %s\n" % cmd)
    # check if file exists
    if not os.path.exists(output_bam):
        sys.stderr.write("output file %s does not exist\n" % output_bam)
    # run cmd
    try:
        subprocess.check_call(cmd, shell=True)
    except Exception as e:
        sys.stderr.write("samtools sort command failed:\n%s\n" %
                         str(e))

def mkdir_p(dirname):
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

def rm_f(files):
    if files:
        if type(files) == list:
            run_shell_cmd('rm -f {}'.format(' '.join(files)))
        else:
            run_shell_cmd('rm -f {}'.format(files))

def countLines(file):
    """Count the number of lines in a file"""
    with open(file) as f:
        n = sum(1 for _ in f)
    return n

def check_python_version():
    """Checks that Python version 3 is being used. Previous versions of
    WASP used python2.7, but version 3 is now required."""
    python_ver = int(sys.version.split()[0].split(".")[0])
    if python_ver < 3:
        raise ImportWarning("python version is %s, but version "
                            ">=3 is required" % (sys.version))
    return 0

def is_gzipped(filename):
    """Checks first two bytes of provided filename and looks for
    gzip magic number. Returns true if it is a gzipped file"""
    f = open(filename, "rb")
    # read first two bytes
    byte1 = f.read(1)
    byte2 = f.read(1)
    f.close()
    # check against gzip magic number 1f8b
    # return (byte1 == chr(0x1f)) and (byte2 == chr(0x8b))
    return (byte1 == b'\x1f') and (byte2== b'\x8b')
