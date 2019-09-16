"""qasm_job.py
Load from qasm source and run job with reporting
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import argparse
import datetime
import pprint
import sys

from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
try:
    from qiskit import __qiskit_version__
except ImportError:
    print("qasm_job WARNING: --qiskit_version not available this qiskit level")
try:
    from qiskit.compiler import transpile
except ImportError:
    print("qasm_job WARNING: -x,--transpile not available this qiskit level")
from qiskit.tools.monitor import job_monitor


EXPLANATION = """qasm_job.py : Loads from one or more qasm source files and runs
experiments with reporting in CSV form. Also can give info on backend properties,
qiskit version, transpilation, etc. Can run as multiple jobs or all as one job.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""
PARSER = argparse.ArgumentParser(description=EXPLANATION)
GROUP = PARSER.add_mutually_exclusive_group()
GROUP.add_argument("-i", "--ibmq", action="store_true",
                   help="Use best genuine IBMQ processor (default)")
GROUP.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
GROUP.add_argument("-a", "--aer", action="store_true",
                   help="""Use QISKit Aer simulator.
                   Default is Aer statevector simulator.
                   Use -a --qasm-simulator to get Aer qasm simulator.
                   Use -a --unitary-simulator to get Aer unitary simulator.""")
PARSER.add_argument("--qasm_simulator", action="store_true",
                    help="""With -a use Aer qasm simulator
                    instead of Aer statevector simulator""")
PARSER.add_argument("--unitary_simulator", action="store_true",
                    help="""With -a use Aer unitary simulator
                    instead of Aer statevector simulator""")
GROUP.add_argument("-b", "--backend", action="store",
                   help="Use specified IBMQ backend")
PARSER.add_argument("--api_provider", action="store",
                    help="""Backend api provider,
                    currently supported are [IBMQ | QI].
                    Default is IBMQ.""", default="IBMQ")
PARSER.add_argument("--backends", action="store_true",
                    help="Print list of backends to stdout and exit")
PARSER.add_argument("-1", "--one_job", action="store_true",
                    help="Run all experiments as one job")
PARSER.add_argument("-c", "--credits", type=int, action="store", default=3,
                    help="Max credits to expend on each job, default is 3")
PARSER.add_argument("-j", "--job", action="store_true",
                    help="Print job dictionary")
PARSER.add_argument("-m", "--memory", action="store_true",
                    help="Print individual results of multishot experiment")
PARSER.add_argument("-o", "--outfile", action="store",
                    help="Write appending CSV to outfile, default is stdout")
PARSER.add_argument("-p", "--properties", action="store",
                    help="Print properties for specified backend to stdout and exit 0")
PARSER.add_argument("-q", "--qubits", type=int, action="store", default=5,
                    help="Number of qubits for the experiment, default is 5")
PARSER.add_argument("--qiskit_version", action="store_true",
                    help="Print Qiskit version and exit 0")
PARSER.add_argument("-r", "--result", action="store_true",
                    help="Print job result")
PARSER.add_argument("-t", "--shots", type=int, action="store", default=1024,
                    help="Number of shots for the experiment, default 1024, max 8192")
PARSER.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")
PARSER.add_argument("-x", "--transpile", action="store_true",
                    help="""Print circuit transpiled for chosen backend to stdout
                    before running job""")
PARSER.add_argument("--histogram", action="store_true",
                    help="""Write image file of histogram of experiment results""")
PARSER.add_argument("--plot_state_city", type=int, action="store",
                    help="""Write image file of state city plot of statevector to
                    PLOT_STATE_CITY decimal points""")
PARSER.add_argument("--figure_basename", type=str, action="store",
                    default='figout',
                    help="""basename including path (if any) for figure output,
                    default='figout', backend name, figure type, and timestamp
                    will be appended""")
PARSER.add_argument("--qasm", action="store_true",
                    help="Print qasm file to stdout before running job")
PARSER.add_argument("--status", action="store_true",
                    help="""Print status of chosen --backend to stdout
                    (default all backends)
                    of --api_provider (default IBMQ)
                    and exit""")
PARSER.add_argument("--token", action="store",
                    help="Use this token")
PARSER.add_argument("--url", action="store",
                    help="Use this url")
PARSER.add_argument("filepath", nargs='*',
                    help="Filepath(s) to 0 or more .qasm files, default is stdin")


# Utility functions
# #################


def verbosity(text, count):
    """Print text if count exceeds verbose level"""
    if ARGS.verbose >= count:
        print(text)


def ibmq_account_fu(token, url):
    """Load IBMQ account appropriately and return provider"""
    if token:
        provider = IBMQ.enable_account(token, url=url)
    else:
        provider = IBMQ.load_account()
    return provider


def qi_account_fu(token):
    """Load Quantum Inspire account appropriately and return provider"""
    from quantuminspire.qiskit import QI
    from quantuminspire.credentials import enable_account
    if token:
        enable_account(token)
    QI.set_authentication()
    return QI


def account_fu(token, url):
    """Load account from correct API provider"""
    a_p = API_PROVIDER.upper()
    if a_p == "IBMQ":
        provider = ibmq_account_fu(token, url)
    elif a_p == "QI":
        provider = qi_account_fu(token)
    return provider


def csv_str(description, sort_keys, sort_counts):
    """Generate a cvs as a string from sorted keys and sorted counts"""
    csv = []
    csv.append(description)
    keys = ""
    for key in sort_keys:
        keys += key + ';'
    csv.append(keys)
    counts = ""
    for count in sort_counts:
        counts += str(count) + ';'
    csv.append(counts)
    return csv


# Choose backend
# ##############


def choose_backend(aer, token, url, b_end, sim, qubits):
    """Return backend selected by user if account will activate and allow."""
    backend = None
    if aer:
        # Import Aer
        from qiskit import BasicAer
        # Run the quantum circuit on a statevector simulator backend
        backend = BasicAer.get_backend('qasm_simulator'
                                       if QASM_SIMULATOR else
                                       'statevector_simulator')
    else:
        provider = account_fu(token, url)
        verbosity("Provider is " + str(provider), 3)
        verbosity("provider.backends is " + str(provider.backends()), 3)
        if b_end:
            backend = provider.get_backend(b_end)
            verbosity('b_end provider.get_backend() returns ' + str(backend), 3)
        elif sim:
            backend = provider.get_backend('ibmq_qasm_simulator')
            verbosity('sim provider.get_backend() returns ' + str(backend), 3)
        else:
            from qiskit.providers.ibmq import least_busy
            large_enough_devices = provider.backends(
                filters=lambda x: x.configuration().n_qubits >= qubits
                and not x.configuration().simulator)
            backend = least_busy(large_enough_devices)
            verbosity("The best backend is " + backend.name(), 2)
    verbosity("Backend is " + str(backend), 1)
    return backend

# Result processing
# #################


def fig_name_str(filepath, backend):
    """Create name consisting of filepath, backend and timestamp"""
    return filepath + '_' + str(backend) + '_' + datetime.datetime.now().isoformat()


def save_fig(figure, filepath, backend, tail):
    """Write a figure to an algorithmically named destination file"""
    figure.savefig(fig_name_str(filepath, backend) + '.' + tail)


def state_city_plot(result_exp, circ, figure_basename, backend, decimals=3):
    """Plot state_city style the output state
    result_exp - experiment result
    circ - the circuit
    figure_basename - base file name of output
    backend - backend run on
    decimals - how many decimal places
    """
    outputstate = result_exp.get_statevector(circ, decimals)
    fig = plot_state_city(outputstate)
    save_fig(fig, figure_basename, backend, 'state_city.png')


def histogram(result_exp, circ, figure_basename, backend):
    """Plot histogram style the counts of
    result_exp - experiment result
    circ - the circuit
    figure_basename - base file name of output
    backend - backend run on
    """
    outputstate = result_exp.get_counts(circ)
    fig = plot_histogram(outputstate)
    save_fig(fig, figure_basename, backend, 'histogram.png')


def process_result(result_exp, circ, memory, backend, qasm_source, ofh):
    """Process the result of one circuit circ
    from result result_exp
    printing to output file handle ofh
    passing original qasm filepath for figure output filename generation
    """
    # Write qasm if requested
    if ARGS.qasm:
        ofh.write(qasm_source + '\n')

    # Raw data if requested
    if memory:
        print(result_exp.data(circ))

    # Print counts if any measurment was taken
    if 'counts' in result_exp.data(circ):
        counts_exp = result_exp.get_counts(circ)
        verbosity(counts_exp, 1)
        sorted_keys = sorted(counts_exp.keys())
        sorted_counts = []
        for i in sorted_keys:
            sorted_counts.append(counts_exp.get(i))

        # Generate CSV
        output = csv_str(str(backend) + ' ' + datetime.datetime.now().isoformat(),
                         sorted_keys, sorted_counts)

        # Write CSV
        for line in output:
            ofh.write(line + '\n')

        if PLOT_STATE_CITY:
            state_city_plot(result_exp, circ, FIGURE_BASENAME,
                            backend, decimals=PLOT_STATE_CITY)
        if HISTOGRAM:
            histogram(result_exp, circ, FIGURE_BASENAME, backend)

# Do job loop
# ###########


def one_exp(filepath, backend, outfile, xpile, shots, memory, j_b, res):
    """Load qasm and run the job, print csv and other selected output"""

    if filepath is None:
        filepath = sys.stdin
    if outfile is None:
        outfile = sys.stdout

    if backend is None:
        print("No backend available, quitting.")
        exit(100)

    # Get file
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

    # Transpile if requested and available and show transpiled circuit
    # ################################################################

    if xpile:
        try:
            print(transpile(circ, backend=backend))
        except NameError:
            print('Transpiler not available this Qiskit level.', file=sys.stderr)

    # Prepare job
    # ###########

    # Maximum number of credits to spend on executions.
    max_credits = ARGS.credits

    # Execute
    job_exp = execute(circ, backend=backend, shots=shots,
                      max_credits=max_credits, memory=memory)
    if j_b:
        print(job_exp)

    job_monitor(job_exp)
    result_exp = job_exp.result()

    if res:
        print(result_exp)

    # Open outfile
    verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2)
    ofh = outfile if outfile is sys.stdout else open(outfile, "a")
    verbosity("File handle is " + str(ofh), 3)

    process_result(result_exp, circ, memory, backend, qasm_source, ofh)

    if outfile is not sys.stdout:
        ofh.close()

# Do all as one job
# #################


def multi_exps(filepaths, backend, outfile, xpile, shots, memory, j_b, res):
    """Load qasms and run all as one the job,
    print csvs and other selected output
    """

    if outfile is None:
        outfile = sys.stdout

    if backend is None:
        print("No backend available, quitting.")
        exit(100)

    circs = []

    for fpath in filepaths:
        # Get file
        verbosity("File path is " + ("stdin" if fpath is sys.stdin else fpath), 2)
        ifh = fpath if fpath is sys.stdin else open(fpath, "r")
        verbosity("File handle is " + str(ifh), 3)

        # Read source
        qasm_source = ifh.read()
        ifh.close()
        verbosity("qasm source:\n" + qasm_source, 1)

        # Create circuit
        circ = QuantumCircuit.from_qasm_str(qasm_source)
        verbosity(circ.draw(), 2)

        # Transpile if requested and available and show transpiled circuit
        # ################################################################

        if xpile:
            try:
                print(transpile(circ, backend=backend))
            except NameError:
                print('Transpiler not available this Qiskit level.', file=sys.stderr)

        circs.append(circ)

    # Prepare job
    # ###########

    # Maximum number of credits to spend on executions.
    max_credits = ARGS.credits

    # Execute
    job_exp = execute(circs, backend=backend, shots=shots,
                      max_credits=max_credits, memory=memory)
    if j_b:
        print(job_exp)

    job_monitor(job_exp)
    result_exp = job_exp.result()

    if res:
        print(result_exp)

    # Open outfile
    verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2)
    ofh = outfile if outfile is sys.stdout else open(outfile, "a")
    verbosity("File handle is " + str(ofh), 3)

    for circ in circs:
        process_result(result_exp, circ, memory, backend, qasm_source, ofh)

    if outfile is not sys.stdout:
        ofh.close()


def get_statuses(provider, backend):
    """Return backend status tuple(s)"""
    stat = ''
    if backend:
        stat = backend.status()
    else:
        for b_e in provider.backends():
            stat += str(b_e.status())
    return stat


# ####
# Main
# ####

# Informational queries
# #####################

ARGS = PARSER.parse_args()
API_PROVIDER = ARGS.api_provider.upper()
PROPERTIES = ARGS.properties
TOKEN = ARGS.token
URL = ARGS.url
QISKIT_VERSION = ARGS.qiskit_version
AER = ARGS.aer
QASM_SIMULATOR = ARGS.qasm_simulator
SIM = ARGS.sim
QUBITS = ARGS.qubits
FILEPATH = ARGS.filepath
OUTFILE = ARGS.outfile
TRANSPILE = ARGS.transpile
SHOTS = ARGS.shots
MEMORY = ARGS.memory
JOB = ARGS.job
RESULT = ARGS.result
BACKEND_NAME = ARGS.backend
PLOT_STATE_CITY = ARGS.plot_state_city
FIGURE_BASENAME = ARGS.figure_basename
HISTOGRAM = ARGS.histogram
STATUS = ARGS.status
BACKENDS = ARGS.backends

if PLOT_STATE_CITY:
    from qiskit.visualization import plot_state_city

if HISTOGRAM:
    from qiskit.tools.visualization import plot_histogram

if API_PROVIDER == "IBMQ" and ((TOKEN and not URL) or (URL and not TOKEN)):
    print('--token and --url must be used together for IBMQ provider or not at all',
          file=sys.stderr)
    exit(1)

if PROPERTIES:
    PROVIDER = account_fu(TOKEN, URL)
    BACKEND = PROVIDER.get_backend(PROPERTIES)
    PP = pprint.PrettyPrinter(indent=4, stream=sys.stdout)
    PP.pprint(BACKEND.properties())
    exit(0)

elif BACKENDS:
    PROVIDER = account_fu(TOKEN, URL)
    PP = pprint.PrettyPrinter(indent=4, stream=sys.stdout)
    PP.pprint(PROVIDER.backends())
    exit(0)

elif STATUS:
    PROVIDER = account_fu(TOKEN, URL)
    BACKEND = PROVIDER.get_backend(BACKEND_NAME) if BACKEND_NAME else None
    PP = pprint.PrettyPrinter(indent=4, stream=sys.stdout)
    PP.pprint(get_statuses(PROVIDER, BACKEND))
    exit(0)

else:
    BACKEND = choose_backend(AER, TOKEN, URL,
                             BACKEND_NAME, SIM, QUBITS)

if QISKIT_VERSION:
    try:
        __qiskit_version__
    except NameError:
        print("__qiskit_version__ not present in this Qiskit level.")
        exit(1)
    PP = pprint.PrettyPrinter(indent=4, stream=sys.stdout)
    PP.pprint(__qiskit_version__)
    exit(0)

if not FILEPATH:
    one_exp(None, BACKEND, OUTFILE, TRANSPILE,
            SHOTS, MEMORY, JOB, RESULT)
else:
    if ARGS.one_job:
        multi_exps(FILEPATH, BACKEND, OUTFILE, TRANSPILE,
                   SHOTS, MEMORY, JOB, RESULT)
    else:
        for f_path in FILEPATH:
            one_exp(f_path, BACKEND, OUTFILE, TRANSPILE,
                    SHOTS, MEMORY, JOB, RESULT)

verbosity('Done!', 1)

# End
