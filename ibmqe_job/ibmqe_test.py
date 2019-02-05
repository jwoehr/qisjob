# ibmqe_test.py
# Load from qasm source and run job with reporting
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

from IBMQuantumExperience import IBMQuantumExperience
import argparse
import sys
import datetime

explanation = """ibmqe_test.py : Load from qasm source and run job with reporting
in CSV form.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
Exits (1) on status error
Exits (2) on device error
Exits (200) on no backend chosen
"""

now = datetime.datetime.now().isoformat()

parser = argparse.ArgumentParser(description=explanation)
group = parser.add_mutually_exclusive_group()
group.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
group.add_argument("-b", "--backend", action="store",
                   help="Use specified IBM backend")
# parser.add_argument("-c", "--credits", type=int, action="store", default=3,
#                     help="Max credits to expend on run, default is 3")
parser.add_argument("-i", "--identity", action="store", required=True,
                    help="Use specified identity token")
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
parser.add_argument("filepath", nargs='?',
                    help="Filepath to .qasm file, default is stdin")

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


# Choose filepath
filepath = None
if args.filepath is None:
    filepath = sys.stdin
else:
    filepath = args.filepath

# Choose outfile
outfile = None
if args.outfile is None:
    outfile = sys.stdout
else:
    outfile = args.outfile

verbosity("File path is " + ("stdin" if filepath is sys.stdin else filepath), 2)

ifh = filepath if filepath is sys.stdin else open(filepath,  "r")

verbosity("File handle is " + str(ifh), 3)

# Read source
qasm_source = ifh.read()
ifh.close()
verbosity("qasm source:\n" + qasm_source, 1)

result_exp = api.run_experiment(qasm_source, backend, args.shots,
                                name=args.name, timeout=args.timeout)

verbosity(result_exp, 1)

# Exit on error
if 'error' in result_exp:
    print("error occurred (probably device error)")
    print(result_exp)
    exit(2)

status = result_exp['status']
if status != 'DONE':
    print("status was not 'DONE'")
    print(result_exp)
    exit(1)

measure = result_exp['result']['measure']
sorted_keys = measure['labels']
sorted_counts = measure['values']
bits = measure['qubits']

# Generate CSV


def csv_str(description, sorted_keys, sorted_counts):
    csv = []
    csv.append(description)
    keys = ""
    for key in sorted_keys:
        keys += key + ';'
    csv.append(keys)
    counts = ""
    for count in sorted_counts:
        counts += str(count) + ';'
    csv.append(counts)
    return csv


output = csv_str(str(backend) + ' ' + now + ' ' +
                 args.name + " qubits : " + str(bits),
                 sorted_keys, sorted_counts)

# Open outfile
verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2)
ofh = outfile if outfile is sys.stdout else open(outfile,  "w")
verbosity("File handle is " + str(ofh), 3)

# Write CSV
for line in output:
    ofh.write(line + '\n')

if outfile is not sys.stdout:
    ofh.close()

verbosity('Done!', 1)

# End
