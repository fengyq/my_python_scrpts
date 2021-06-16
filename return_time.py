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

def run_shell_cmd(cmd):
    p = subprocess.Popen(
        ['/bin/bash', '-o', 'pipefail'],  # to catch error in pipe
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        #preexec_fn=os.setsid)  # to make a new process with a new PGID
        start_new_session=True) # replace preexec_fn
    pid = p.pid # PID - Process ID
    pgid = os.getpgid(pid) # PGID - Process Group ID
    log.info('run_shell_cmd: PID={}, PGID={}, CMD={}'.format(pid, pgid, cmd))

    t0 = get_ticks() # start time
    stdout, stderr = p.communicate(cmd) # communicate() returns a tuple (stdout_data, stderr_data).
    rc = p.returncode # execution status
    t1 = get_ticks() # end time

    err_str = (
        'PID={pid}, PGID={pgid}, RC={rc}, DURATION_SEC={dur:.1f}\n'
        'STDERR={stde}\nSTDOUT={stdo}'
    ).format(
        pid=pid, pgid=pgid, rc=rc, dur=t1 - t0, stde=stderr.strip(), stdo=stdout.strip()
    )

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


def mkdir_p(dirname):
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

def rm_f(files):
    if files:
        if type(files) == list:
            run_shell_cmd('rm -f {}'.format(' '.join(files)))
        else:
            run_shell_cmd('rm -f {}'.format(files))
