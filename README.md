# qisjob

## Qiskit Job Control

* [The `qisjob` module](#the-qisjob-module)
* [The `qisjob` command](#the-qisjob-command)
* [The `QisJob` class](#the-qisjob-class)
* [`QisJob` Documentation](#qisjob-documentation)
* [Prerequisites](#prerequisites)
* [Install](#install)
* [Usage](#usage)
* [Notes](#notes)

## The `qisjob` module

The module is `qisjob`. It was formerly named `qis_job`. I'm not sure why, but I have now changed it to `qisjob`.

If you previously installed the module as `qis_job` you can uninstall that older version either by

* `pip3 uninstall qis_job`
* `make uninstall_oldname`

## The `qisjob` command

The `qisjob` command loads and executes [Qiskit](https://qiskit.org) experiments on simulators or on genuine quantum
computing hardware such as that found at [IBM Q Experience](https://quantum-computing.ibm.com). Input is from one or
more OpenQASM 2 source files or Qiskit `QuantumCircuit` Python code or from source provided via standard input in the
absence of file arguments.

The command also provides some utility functions such as:

* enumerating backend platforms
* configuration both current and historical of backend platforms
* status of backend platforms
* status and results of jobs both current and historical

and other useful operations for Qiskit experimentation.

**`qisjob` comes with NO GUARANTEE and NO WARRANTY including as regards correctness nor applicability.
See [LICENSE](https://github.com/jwoehr/qisjob/blob/main/LICENSE.txt).**

`qisjob` can run Qiskit experiments expressed as either:

* [OPENQASM Open Quantum Assembly Language](https://github.com/openqasm/openqasm)
  * Use a well-formed OPENQASM file.
  * Examples are found in the `qasm_examples` [subdirectory](https://github.com/jwoehr/qisjob/tree/master/share/qasm_examples) of the project.
* Qiskit Terra `QuantumCircuit` Python code snippet.
  * To use a code snippet, only import that which is absolutely needed in the snippet and provide no execution code.
  * Pass the name of your `QuantumCircuit` to the `--qc` argument of `qisjob.py`
    * If you have multiple files of this sort, all must have the same name for their `QuantumCircuit` object.
    * An example circuit (very long execution!) is found in the `qc_examples` [subdirectory](https://github.com/jwoehr/qisjob/tree/master/share/qc_examples) of the project.

You can load and run multiple files, but you cannot mix Qasm and `QuantumCircuit` files in the same execution of the `qisjob`.

`QisJob` is compatible with the experimental [NuQasm2](https://github.com/jwoehr/nuqasm2) project, that you can use to compile and run your OPENQASM2.0 source code.
Given that you have `NuQasm2` installed, you can use `qisjob`'s `-n` _include-path:include-path:..._ switch

## The `QisJob` class

The `qisjob` script works by instancing an object of the class `qisjob.QisJob`.

You can use an object instance of the class `qisjob.QisJob` in your own program for its utility functions or the execute
experiments on real quantum hardware and/or simulators either using OpenQASM source or Qiskit `QuantumCircuit` source code.

### `QisJob` Documentation

The `qisjob.QisJob` object that underlies the `qisjob` script that can be used in your own programs has many args/kwargs.

The documentation for `qisjob.QisJob` is installed with the module in the site library's `share/doc`.

You can also read the [QisJob Documentation Online](http://www.softwoehr.com/softwoehr/oss/qisjob/)

## Prerequisites

* [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
* [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
* A provider such as [Qiskit/qiskit-ibmq-provider](https://github.com/Qiskit/qiskit-ibmq-provider)
* Currently supported backend providers are:
  * IBMQ (required)
    * For the local Aer simulator you only need qiskit-aer installed.
      * For genuine QPU or cloud simulator you will need an [IBM Q Experience API token](https://quantum-computing.ibm.com/account).
  * Forest (optional; a warning message may appear if absent)
    * You need [quantastic/qiskit-forest](https://github.com/quantastica/qiskit-forest)
      * `pip install quantastica-qiskit-forest`
    * For Rigetti QPU you will need [access](https://qcs.rigetti.com/request-access)
  * MQT (optional; a warning message may appear if absent)
    * You need [cda-tum/ddsim](https://github.com/cda-tum/ddsim)
    * This was formerly the JKU simulator
  * QI (optional; a warning message may appear if absent)
    * Install QuTech-Delft/quantuminspire from either
      * [Github QuTech-Delft/quantuminspire](https://github.com/QuTech-Delft/quantuminspire)
        * `pip install quantuminspire`.
      * You will also need a [Quantum Inspire token](https://www.quantum-inspire.com/account).

## Install

Do one of the following in the source directory (preferably in a Python virtual environment set up for Qiskit)

* `make # gnu make, we have provided a Makefile`
* `./setup.py install`
* `pip3 install .`

**Note** that the module name has recently (2021-02-16) changed from `qis_job` to `qisjob`. If you previously installed the module as `qis_job` you can uninstall that older version either by

* `pip3 uninstall qis_job`
* `make uninstall_oldname`

## Uninstall

Do one of the following in the source directory

* `make uninstall`
* `pip3 uninstall qisjob`

## Usage

The `qisjob` script has helpful help.

```text
$ qisjob -h
usage: qisjob [-h] [-i | -s | -a | --aersimulator AERSIMULATOR | -b BACKEND] [--qasm_simulator | --unitary_simulator]
              [--statevector_gpu | --unitary_gpu | --density_matrix_gpu] [--version] [--api_provider API_PROVIDER] [--hub HUB] [--group GROUP]
              [--project PROJECT] [--providers] [--noisy_sim] [--qvm] [--qvm_as] [--backends] [-1] [-d DATETIME] [-g] [-j] [--jobs JOBS] [--job_id JOB_ID]
              [--job_result JOB_RESULT] [-m] [-n NUQASM2] [-o OUTFILE] [-p] [-q QUBITS] [--qiskit_version] [-r] [-t SHOTS] [-v] [-x] [--showsched]
              [--circuit_layout] [--optimization_level OPTIMIZATION_LEVEL] [--histogram] [--plot_state_city PLOT_STATE_CITY]
              [--figure_basename FIGURE_BASENAME] [--qasm] [--qc QC] [--status] [--token TOKEN] [--url URL] [--use_job_monitor]
              [--job_monitor_line JOB_MONITOR_LINE] [--job_monitor_filepath JOB_MONITOR_FILEPATH] [-w] [--use_qasm3]
              [filepath ...]

Qisjob loads from one or more OpenQASM source files or from a file containing a Qiskit QuantumCircuit definition in Python and runs as experiments with
reporting in CSV form. Can graph results as histogram or state-city plot. Also can give info on backend properties, qiskit version, show circuit
transpilation, etc. Can run as multiple jobs or all as one job. Exits 0 on success, 1 on argument error, 100 on runtime error, 200 on QiskitError. Copyright
2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051. Apache License, Version 2.0 -- See LICENSE which you should have received with this
code. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the
License.

positional arguments:
  filepath              Filepath(s) to 0 or more .qasm files, default is stdin

options:
  -h, --help            show this help message and exit
  -i, --ibmq            Use best genuine IBMQ processor (default)
  -s, --sim             Use IBMQ qasm simulator
  -a, --aer             Use QISKit Aer simulator. Default is Aer statevector simulator. Use -a --qasm-simulator to get Aer qasm simulator. Use -a --unitary-
                        simulator to get Aer unitary simulator.
  --aersimulator AERSIMULATOR
                        Use Qiskit AerSimulator. Can be invoked multiple times. Each invocation should be an argument pair, e.g., '--aersimulator
                        backend=ibmq_lima'
  -b BACKEND, --backend BACKEND
                        Use specified IBMQ backend
  --qasm_simulator      With -a use qasm simulator instead of statevector simulator
  --unitary_simulator   With -a use unitary simulator instead of statevector simulator
  --statevector_gpu     With -a and --qasm_simulator use gpu statevector simulator
  --unitary_gpu         With -a and --qasm_simulator use gpu unitary simulator
  --density_matrix_gpu  With -a and --qasm_simulator use gpu density matrix simulator
  --version             Announce QisJob version
  --api_provider API_PROVIDER
                        Backend remote api provider, currently supported are [IBMQ | Forest | MQT | QI]. Default is IBMQ.
  --hub HUB             Provider hub, default is 'ibm-q'
  --group GROUP         Provider group, default is 'open'
  --project PROJECT     Provider project, default is 'main'
  --providers           List hub/group/project providers for IBMQ
  --noisy_sim           Perform circuit(s) as Aer simulation using the designated backend (see --backend) as the model backend.
  --qvm                 Use Forest local qvm simulator described by -b backend, generally one of qasm_simulator or statevector_simulator. Use --qvm_as to
                        instruct the simulator to emulate a specific Rigetti QPU
  --qvm_as              Use Forest local qvm simulator to emulate the specific Rigetti QPU described by -b backend. Use --qvm to run the Forest local qvm
                        simulator described by -b backend.
  --backends            Print list of backends to stdout and exit 0
  -1, --one_job         Run all experiments as one job
  -d DATETIME, --datetime DATETIME
                        Datetime 'year,month,day[,hour,min,sec]' for -p,--properties
  -g, --configuration   Print configuration for backend specified by -b to stdout and exit 0
  -j, --job             Print your job's dictionary
  --jobs JOBS           Print JOBS number of jobs and status for -b backend and exit 0
  --job_id JOB_ID       Print job number JOB_ID for -b backend and exit 0
  --job_result JOB_RESULT
                        Print result of job number JOB_RESULT for -b backend and exit 0
  -m, --memory          Print individual results of multishot experiment
  -n NUQASM2, --nuqasm2 NUQASM2
                        Use nuqasm2 to translate OPENQASM2 source, providing include path for any include directives
  -o OUTFILE, --outfile OUTFILE
                        Write appending CSV to outfile, default is stdout
  -p, --properties      Print properties for backend specified by -b to stdout and exit 0
  -q QUBITS, --qubits QUBITS
                        Number of qubits for the experiment, default is 5
  --qiskit_version      Print Qiskit version and exit 0
  -r, --result          Print job result
  -t SHOTS, --shots SHOTS
                        Number of shots for the experiment, default 1024, max 8192
  -v, --verbose         Increase runtime verbosity each -v up to 3. If precisely 4, prettyprint QisJob's data dictionary and return (good for debugging
                        script arguments)
  -x, --transpile       Print circuit transpiled for chosen backend to stdout before running job
  --showsched           In conjuction with -x, show schedule for transpiled circuit for chosen backend to stdout before running job
  --circuit_layout      With -x, write image file of circuit layout after transpile (see --figure_basename)
  --optimization_level OPTIMIZATION_LEVEL
                        Set optimization level for transpilation before run, valid values 0-3, default is 1
  --histogram           Write image file of histogram of experiment results (see --figure_basename)
  --plot_state_city PLOT_STATE_CITY
                        Write image file of state city plot of statevector to PLOT_STATE_CITY decimal points (see --figure_basename)
  --figure_basename FIGURE_BASENAME
                        basename including path (if any) for figure output, default='figout', backend name, figure type, and timestamp will be appended
  --qasm                Print qasm file to stdout before running job
  --qc QC               Indicate variable name of Python-coded QuantumCircuit
  --status              Print status of chosen --backend to stdout (default all backends) of --api_provider (default IBMQ) and exit 0
  --token TOKEN         Use this token
  --url URL             Use this url
  --use_job_monitor     Display job monitor instead of just waiting for job result
  --job_monitor_line JOB_MONITOR_LINE
                        Comma-separated list of hex values for character(s) to emit at the head of each line of job monitor output, default is '0x0d'
  --job_monitor_filepath JOB_MONITOR_FILEPATH
                        Filepath for Job Monitor output if Job Monitor requested by --use_job_monitor, default is sys.stdout
  -w, --warnings        Don't print warnings on missing optional modules
  --use_qasm3           Use experimental qiskit-terra OpenQASM 3 implementation
```

## Notes

* It is recommended you download or clone the most recent [release](https://github.com/jwoehr/qisjob/releases).
  * Version v4.1.1 is the current version.
* This document always reflects the latest checkins and may be ahead of the release versions.
  * See the README.md in the release version itself for contemporary information.
* Please use the [issue tracker](https://github.com/jwoehr/qisjob/issues) to report any issues or feature requests.
* If Python complains about the certs, you could try setting an env variable, like this:
  * `export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")`

Jack Woehr 2023-03-02
