# qis_job

**QISKit Job Control**
* [The `qisjob` command](#The-qisjob-command)
* [Prerequisites](#Prerequisites)
* [Install](#Install)
* [Usage](#Usage)
* [Notes](#Notes)

## The `qisjob` command

The `qisjob` command loads and executes [Qiskit](https://qiskit.org) experiments on simulators or on genuine quantum
computing hardware such as that found at [IBM Q Experience](https://quantum-computing.ibm.com). Input is from one or
more OpenQASM 2 source files or from OpenQASM 2 source code provided via standard input (in the absence of file arguments).

The command also provides some utility functions such as:

-   enumerating backend platforms
-   checking on status of backend platforms
-   checking on status of jobs

and other useful operations for Qiskit experimentation.

**`qis_job` comes with NO GUARANTEE and NO WARRANTY including as regards correctness nor applicability. See LICENSE.**

`qisjob` can run Qiskit experiments expressed as either:

* [OPENQASM Open Quantum Assembly Language](https://arxiv.org/abs/1707.03429)
    * Use a well-formed OPENQASM2 file.
    * Examples are found in the `qasm_examples` [subdirectory](https://github.com/jwoehr/qis_job/tree/master/share/qasm_examples) of the project.
* a Qiskit Terra `QuantumCircuit` Python code snippet.

    * To use a code snippet, only import that which is absolutely needed in the snippet and provide no execution code.
    * Pass the name of your `QuantumCircuit` to the `--qc` argument of `qis_job.py`
        * If you have multiple files of this sort, all must have the same name for their `QuantumCircuit` object.
    * An example circuit (very long execution!) is found in the `qc_examples` [subdirectory](https://github.com/jwoehr/qis_job/tree/master/share/qc_examples) of the project.

You can load and run multiple files, but you cannot mix Qasm and `QuantumCircuit` files in the same execution of the `qisjob`.

`QisJob` is compatible with the experimental [NuQasm2](https://github.com/jwoehr/nuqasm2) project, that you can use to compile and run your OPENQASM2.0 source code. Given that you have `NuQasm2` installed, you can use `qisjob`'s `-n` _include-path:include-path:..._ switch

You can use the class `QisJob` in your own program and feed it a string of OPENQASM2.0 source code via the `qasm_src=` kwarg.

## Prerequisites

* [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
* [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
* A provider such as [Qiskit/qiskit-ibmq-provider](https://github.com/Qiskit/qiskit-ibmq-provider)
* Currently supported backend providers are:
   * IBMQ (required)
      * For the local Aer simulator you only need qiskit-aer installed.
      * For genuine QPU or cloud simulator you will need an [IBM Q Experience API token](https://quantum-computing.ibm.com/account).
   * JKU (optional; a warning message may appear if absent)
      * You need [Qiskit/qiskit-jku-provider](https://github.com/Qiskit/qiskit-jku-provider)
      * At the time of this writing, you need to clone from a [fork's pull request](https://github.com/HartwigB/qiskit-jku-provider/tree/clean_history)
    * Forest (optional; a warning message may appear if absent)
       * For local simulator or Rigetti QPU you will need
         * [Rigetti qvm](https://github.com/rigetti/qvm)
         * [Rigetti pyQuil](https://github.com/rigetti/pyquil)
         * [quantastica/qiskit-forest](https://github.com/quantastica/qiskit-forest)
       * For Rigetti QPU you will need [access](https://qcs.rigetti.com/request-access)
    * QI (optional; a warning message may appear if absent)
        * Install QuTech-Delft/quantuminspire from either
            * [Github QuTech-Delft/quantuminspire](https://github.com/QuTech-Delft/quantuminspire)
            * `pip install quantuminspire`.
        * You will also need a [Quantum Inspire token](https://www.quantum-inspire.com/account).

The older `qiskit-community` project `qcgpu` is no longer supported. It has not been updated and does not work with
current Qiskit.

## Install

Do one of the following (preferably in a Python virtual environment set up for Qiskit)

* `./setup.py`
* `pip3 install .` 

## Usage

```
$ qisjob -h
usage: qisjob [-h] [-i | -s | -a | -b BACKEND] [--qasm_simulator | --unitary_simulator] [--statevector_gpu | --unitary_gpu | --density_matrix_gpu] [--qisjob_version]
              [--api_provider API_PROVIDER] [--qvm] [--qvm_as] [--backends] [-1] [-c CREDITS] [-d DATETIME] [-g] [-j] [--jobs JOBS] [--job_id JOB_ID] [--job_result JOB_RESULT] [-m]
              [-n NUQASM2] [-o OUTFILE] [-p] [-q QUBITS] [--qiskit_version] [-r] [-t SHOTS] [-v] [-x] [--showsched] [--circuit_layout] [--optimization_level OPTIMIZATION_LEVEL]
              [--histogram] [--plot_state_city PLOT_STATE_CITY] [--figure_basename FIGURE_BASENAME] [--qasm] [--qc QC] [--status] [--token TOKEN] [--url URL] [--use_job_monitor]
              [filepath [filepath ...]]

Qisjob loads from one or more qasm source files or from a file containing a Qiskit QuantumCircuit definition in Python and runs as experiments with reporting in CSV form. Can graph
results as histogram or state-city plot. Also can give info on backend properties, qiskit version, show circuit transpilation, etc. Can run as multiple jobs or all as one job. Exits 0
on success, 1 on argument error, 100 on runtime error. Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051. BSD-3 license -- See LICENSE which you should
have received with this code. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

positional arguments:
  filepath              Filepath(s) to 0 or more .qasm files, default is stdin

optional arguments:
  -h, --help            show this help message and exit
  -i, --ibmq            Use best genuine IBMQ processor (default)
  -s, --sim             Use IBMQ qasm simulator
  -a, --aer             Use QISKit Aer simulator. Default is Aer statevector simulator. Use -a --qasm-simulator to get Aer qasm simulator. Use -a --unitary-simulator to get Aer
                        unitary simulator.
  -b BACKEND, --backend BACKEND
                        Use specified IBMQ backend
  --qasm_simulator      With -a use qasm simulator instead of statevector simulator
  --unitary_simulator   With -a use unitary simulator instead of statevector simulator
  --statevector_gpu     With -a and --qasm_simulator use gpu statevector simulator
  --unitary_gpu         With -a and --qasm_simulator use gpu unitary simulator
  --density_matrix_gpu  With -a and --qasm_simulator use gpu density matrix simulator
  --qisjob_version      Announce QisJob version
  --api_provider API_PROVIDER
                        Backend remote api provider, currently supported are [IBMQ | QI | Forest | JKU]. Default is IBMQ.
  --qvm                 Use Forest local qvm simulator described by -b backend, generally one of qasm_simulator or statevector_simulator. Use --qvm_as to instruct the simulator to
                        emulate a specific Rigetti QPU
  --qvm_as              Use Forest local qvm simulator to emulate the specific Rigetti QPU described by -b backend. Use --qvm to run the Forest local qvm simulator described by -b
                        backend.
  --backends            Print list of backends to stdout and exit 0
  -1, --one_job         Run all experiments as one job
  -c CREDITS, --credits CREDITS
                        Max credits to expend on each job, default is 3
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
  -v, --verbose         Increase verbosity each -v up to 3
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
  --qc QC               Indicate circuit name of python-coded QuantumCircuit
  --status              Print status of chosen --backend to stdout (default all backends) of --api_provider (default IBMQ) and exit 0
  --token TOKEN         Use this token
  --url URL             Use this url
  --use_job_monitor     Display job monitor instead of just waiting for job result
```

## Notes

* It is recommended you download or clone the most recent [release](https://github.com/jwoehr/qis_job/releases).
* This document always reflects the latest checkins and may be ahead of the release versions.
  * See the README.md in the release version itself for contemporary information.
* Please use the [issue tracker](https://github.com/jwoehr/qis_job/issues) to report any issues or feature requests.
* If Python complains about the certs, you could try setting an env variable, like this:
   `export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")`

Jack Woehr 2020-10-10
