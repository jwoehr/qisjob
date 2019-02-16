# ibmqe_job.py
# Create job loading qasm source and run job with reporting in CSV
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

from IBMQuantumExperience import IBMQuantumExperience
from ibmqe_jobmgr import IBMQEJobMgr, IBMQEJobSpec
import argparse
import sys
import datetime
import time

explanation = """ibmqe_jobs.py : Create job loading one or more qasm sources
and run job with reporting in CSV.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
Exits (1) on status error.
Exits (2) on device error.
Exits (200) on no backend chosen.
"""

now = datetime.datetime.now().isoformat()

parser = argparse.ArgumentParser(description=explanation)
group = parser.add_mutually_exclusive_group()
group.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
group.add_argument("-b", "--backend", action="store",
                   help="Use specified IBM backend")
parser.add_argument("-c", "--credits", type=int, action="store", default=3,
                    help="Max credits to expend on run, default is 3")
parser.add_argument("-i", "--identity", action="store", required=True,
                    help="Use specified identity token")
parser.add_argument("-j", "--job", action="store_true",
                    help="Run a job")
parser.add_argument("-n", "--name", action="store",
                    default=now,
                    help="Your name for this experiment, default is timestamp")
parser.add_argument("-m", "--timeout", type=int, action="store", default=60,
                    help="Timeout in seconds, default is 60")
parser.add_argument("-o", "--outfile", action="store",
                    help="Write CSV to outfile overwriting silently, default is stdout")
parser.add_argument("-q", "--qubits", type=int, action="store", default=5,
                    help="Number of qubits for the experiment, default is 5")
parser.add_argument("-t", "--shots", type=int, action="store", default=1024,
                    help="Number of shots for the experiment, default is 1024")
parser.add_argument("-u", "--url",  action="store", default='https://quantumexperience.ng.bluemix.net/api',
                    help="URL, default is https://quantumexperience.ng.bluemix.net/api")
parser.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")
parser.add_argument("-y", "--yiqing", action="store_true",
                    help="Draw results as Yi Qing Oracle")
parser.add_argument("-z", "--sleeptime", type=int, action="store", default=4,
                    help="""Number of seconds to sleep between checks for
                    completion, default is 4""")
parser.add_argument("filepaths", nargs='+',
                    help="Filepath(s) to one more .qasm file(s), required")

args = parser.parse_args()

# Verbose script

def verbosity(text, count):
    if args.verbose >= count:
        print(text)

# Connect to IBMQE
api = IBMQuantumExperience(args.identity, config={
                           "url": args.url}, verify=True)

# Choose backend
if args.backend:
    backend = args.backend
elif args.sim:
    backend = 'ibmq_qasm_simulator'
else:
    print("No backend chosen, exiting.")
    exit(200)

# Choose outfile
outfile = None
if args.outfile is None:
    outfile = sys.stdout
else:
    outfile = args.outfile

jx = IBMQEJobMgr(api, backend=backend,
                 counts=args.shots, credits=args.credits, verbose=args.verbose)
for filepath in args.filepaths:
    jx.add_exec(IBMQEJobSpec(filepath=filepath))

jx.run_job()

while jx.get_job_status() != 'COMPLETED':
    print(jx.get_job_status())
    time.sleep(args.sleeptime)

verbosity(jx.get_job(), 1)

for i in range(0, len(jx.execs)):
    csv = jx.csv_execution(args.filepaths[i], i)
    for c in csv:
        print(c)

if args.yiqing:
	from qyqhex import QYQHexagram, QYQLine
	h = QYQHexagram(backend)
	for i in range(0, len(jx.execs)):
		h.assimilate(jx.get_job_qasms_result_data_counts(i))
		# verbosity(jx.get_job_qasms_result_data_counts(i), 1)
	h.draw(True)

verbosity('Done!', 1)

# End
