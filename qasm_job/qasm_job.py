"""qasm_job.py
Load from qasm source and run job with reporting
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import argparse
import sys
import datetime

from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
try:
    from qiskit.compiler import transpile
except ImportError:
    print("qasm_job WARNING: -x,--transpile not available this qiskit level")
from qiskit.tools.monitor import job_monitor


explanation = """qasm_job.py : Load from qasm source and run job with reporting
in CSV form.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""
parser = argparse.ArgumentParser(description=explanation)
group = parser.add_mutually_exclusive_group()
group.add_argument("-i", "--ibmq", action="store_true",
                   help="Use best genuine IBMQ processor (default)")
group.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
group.add_argument("-a", "--aer", action="store_true",
                   help="Use QISKit aer simulator")
group.add_argument("-b", "--backend", action="store",
                   help="Use specified IBM backend")
parser.add_argument("-c", "--credits", type=int, action="store", default=3,
                    help="Max credits to expend on run, default is 3")
parser.add_argument("-m", "--memory", action="store_true",
                    help="Print individual results of multishot experiment")
parser.add_argument("-o", "--outfile", action="store",
                    help="Write CSV to outfile overwriting silently, default is stdout")
parser.add_argument("-q", "--qubits", type=int, action="store", default=5,
                    help="Number of qubits for the experiment, default is 5")
parser.add_argument("-t", "--shots", type=int, action="store", default=1024,
                    help="Number of shots for the experiment, default is 1024")
parser.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")
parser.add_argument("-x", "--transpile", action="store_true",
                    help="Show circuit transpiled for chosen backend")
parser.add_argument("filepath", nargs='?',
                    help="Filepath to .qasm file, default is stdin")


args = parser.parse_args()


def verbosity(text, count):
    """Print text if count exceeds verbose level"""
    if args.verbose >= count:
        print(text)


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

ifh = filepath if filepath is sys.stdin else open(filepath, "r")

verbosity("File handle is " + str(ifh), 3)

# Read source
qasm_source = ifh.read()
ifh.close()
verbosity("qasm source:\n" + qasm_source, 1)

# Create circuit
circ = QuantumCircuit.from_qasm_str(qasm_source)
verbosity(circ.draw(), 2)

# Choose backend
backend = None
if args.aer:
    # Import Aer
    from qiskit import BasicAer
    # Run the quantum circuit on a statevector simulator backend
    backend = BasicAer.get_backend('statevector_simulator')
else:
    IBMQ.load_accounts()
    if args.backend:
        backend = IBMQ.get_backend(args.backend)
    elif args.sim:
        backend = IBMQ.get_backend('ibmq_qasm_simulator')
    else:
        from qiskit.providers.ibmq import least_busy
        large_enough_devices = IBMQ.backends(
            filters=lambda x: x.configuration().n_qubits >= args.qubits
            and not x.configuration().simulator)
        backend = least_busy(large_enough_devices)
        verbosity("The best backend is " + backend.name(), 2)

verbosity("Backend is " + str(backend), 1)

if backend is None:
    print("No backend available, quitting.")
    exit(100)

# Transpile if requested and available and show transpiled circuit
# ################################################################

try:
    transpile
except NameError:
    args.transpile = None

if args.transpile:
    print(transpile(circ, backend=backend))

# Prepare job
# ###########

# Number of shots to run the program (experiment); maximum is 8192 shots.
shots = args.shots
# Maximum number of credits to spend on executions.
max_credits = args.credits


def csv_str(description, sorted_keys, sorted_counts):
    """Generate a cvs as a string from sorted keys and sorted counts"""
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


# Execute
job_exp = execute(circ, backend=backend, shots=shots,
                  max_credits=max_credits, memory=args.memory)
job_monitor(job_exp)
result_exp = job_exp.result()
counts_exp = result_exp.get_counts(circ)
verbosity(counts_exp, 1)
sorted_keys = sorted(counts_exp.keys())
sorted_counts = []
for i in sorted_keys:
    sorted_counts.append(counts_exp.get(i))

# Raw data if requested
if args.memory:
    print(result_exp.data())

# Generate CSV
output = csv_str(str(backend) + ' ' + datetime.datetime.now().isoformat(),
                 sorted_keys, sorted_counts)

# Open outfile
verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2)
ofh = outfile if outfile is sys.stdout else open(outfile, "w")
verbosity("File handle is " + str(ofh), 3)

# Write CSV
for line in output:
    ofh.write(line + '\n')
if outfile is not sys.stdout:
    ofh.close()

verbosity('Done!', 1)

# End
