# qis_job
QISKit Job Control

The `qis_job.py` script (or, if the setup is run, the `qisjob` command) loads and executes [Qiskit](https://qiskit.org)
experiments on simulators or on genuine quantum computing hardware such as that found at [IBM Q Experience](https://quantum-computing.ibm.com).

The script/command also provides some utility functions such as:

* enumerating backend platforms
* checking on status of backend platforms
* checking on status of jobs

etc.

`qis_job.py`/`qisjob` can run Qiskit experiments expressed as either:
* [OPENQASM Open Quantum Assembly Language](https://arxiv.org/abs/1707.03429)
  * Use a well-formed OPENQASM2 file.
  * Examples are found in the `qasm_examples` subdirectory of the project.
* a Qiskit Terra `QuantumCircuit` Python code snippet.
  * To use a code snippet, only import that which is absolutely needed in the snippet and provide no execution code.
  * Pass the name of your `QuantumCircuit` to the `--qc` argument of `qis_job.py`
    * If you have multiple files of this sort, all must have the same name for their `QuantumCircuit` object.
  * An example circuit (very long execution!) is found in the `qc_examples` subdirectory of the project.
  
You can load and run multiple files, but you cannot mix Qasm and `QuantumCircuit` files in the same execution of the `qis_job.py` script.

For this project you will need to install
* [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
* [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
* A provider such as [Qiskit/qiskit-ibmq-provider](https://github.com/Qiskit/qiskit-ibmq-provider)
* Currently supported backend providers are:
  * IBMQ
    * For the local Aer simulator you only need qiskit-aer installed.
    * For genuine QPU or cloud simulator you will need an [IBM Q Experience API token](https://quantum-computing.ibm.com/account).
  * Forest
    * For local simulator or Rigetti QPU you will need
      * [Rigetti qvm](https://github.com/rigetti/qvm)
      * [Rigetti pyQuil](https://github.com/rigetti/pyquil)
      * [quantastica/qiskit-forest](https://github.com/quantastica/qiskit-forest)
    * For Rigetti QPU you will need [access](https://qcs.rigetti.com/request-access)
  * QI
    * Install QuTech-Delft/quantuminspire from either
      * [Github QuTech-Delft/quantuminspire](https://github.com/QuTech-Delft/quantuminspire)
      * `pip install quantuminspire`.
    * You will also need a [Quantum Inspire token](https://www.quantum-inspire.com/account).
  * qcgpu
    * To use the qcgpu simulator, install [qiskit-community/qiskit-qcgpu-provider](https://github.com/qiskit-community/qiskit-qcgpu-provider)


```
$ qisjob -h
usage: qisjob [-h] [-i | -s | -a | --qcgpu | -b BACKEND]
              [--qasm_simulator | --unitary_simulator]
              [--api_provider API_PROVIDER] [--qvm] [--qvm_as] [--backends]
              [-1] [-c CREDITS] [-d DATETIME] [-g] [-j] [--jobs JOBS]
              [--job_id JOB_ID] [--job_result JOB_RESULT] [-m] [-o OUTFILE]
              [-p] [-q QUBITS] [--qiskit_version] [-r] [-t SHOTS] [-v] [-x]
              [--circuit_layout] [--histogram]
              [--plot_state_city PLOT_STATE_CITY]
              [--figure_basename FIGURE_BASENAME] [--qasm] [--qc QC]
              [--status] [--token TOKEN] [--url URL]
              [filepath [filepath ...]]

qis_job.py : Loads from one or more qasm source files or from a file
containing a Qiskit QuantumCircuit definition in Python and runs as
experiments with reporting in CSV form. Can graph results as histogram or
state-city plot. Also can give info on backend properties, qiskit version,
show circuit transpilation, etc. Can run as multiple jobs or all as one job.
Exits 0 on success, 1 on argument error, 100 on runtime error. Copyright 2019
Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051. BSD-3
license -- See LICENSE which you should have received with this code. THIS
SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

positional arguments:
  filepath              Filepath(s) to 0 or more .qasm files, default is stdin

optional arguments:
  -h, --help            show this help message and exit
  -i, --ibmq            Use best genuine IBMQ processor (default)
  -s, --sim             Use IBMQ qasm simulator
  -a, --aer             Use QISKit Aer simulator. Default is Aer statevector
                        simulator. Use -a --qasm-simulator to get Aer qasm
                        simulator. Use -a --unitary-simulator to get Aer
                        unitary simulator.
  --qcgpu               Use qcgpu simulator. Default is statevector simulator.
                        Use --qcgpu --qasm-simulator to get qcgpu qasm
                        simulator.
  -b BACKEND, --backend BACKEND
                        Use specified IBMQ backend
  --qasm_simulator      With -a or --qcgpu use qasm simulator instead of
                        statevector simulator
  --unitary_simulator   With -a use unitary simulator instead of statevector
                        simulator
  --api_provider API_PROVIDER
                        Backend remote api provider, currently supported are
                        [IBMQ | QI | Forest]. Default is IBMQ.
  --qvm                 Use Forest local qvm simulator described by -b
                        backend, generally one of qasm_simulator or
                        statevector_simulator. Use --qvm_as to instruct the
                        simulator to emulate a specific Rigetti QPU
  --qvm_as              Use Forest local qvm simulator to emulate the specific
                        Rigetti QPU described by -b backend. Use --qvm to run
                        the Forest local qvm simulator described by -b
                        backend.
  --backends            Print list of backends to stdout and exit 0
  -1, --one_job         Run all experiments as one job
  -c CREDITS, --credits CREDITS
                        Max credits to expend on each job, default is 3
  -d DATETIME, --datetime DATETIME
                        Datetime 'year,month,day[,hour,min,sec]' for -p,--
                        properties
  -g, --configuration   Print configuration for backend specified by -b to
                        stdout and exit 0
  -j, --job             Print your job's dictionary
  --jobs JOBS           Print JOBS jobs and status for -b backend and exit 0
  --job_id JOB_ID       Print job number JOB_ID for -b backend and exit 0
  --job_result JOB_RESULT
                        "Print result of job number JOB_RESULT for -b backend
                        and exit 0
  -m, --memory          Print individual results of multishot experiment
  -o OUTFILE, --outfile OUTFILE
                        Write appending CSV to outfile, default is stdout
  -p, --properties      Print properties for backend specified by -b to stdout
                        and exit 0
  -q QUBITS, --qubits QUBITS
                        Number of qubits for the experiment, default is 5
  --qiskit_version      Print Qiskit version and exit 0
  -r, --result          Print job result
  -t SHOTS, --shots SHOTS
                        Number of shots for the experiment, default 1024, max
                        8192
  -v, --verbose         Increase verbosity each -v up to 3
  -x, --transpile       Print circuit transpiled for chosen backend to stdout
                        before running job
  --circuit_layout      With -x, write image file of circuit layout after
                        transpile (see --figure_basename)
  --histogram           Write image file of histogram of experiment results
                        (see --figure_basename)
  --plot_state_city PLOT_STATE_CITY
                        Write image file of state city plot of statevector to
                        PLOT_STATE_CITY decimal points (see --figure_basename)
  --figure_basename FIGURE_BASENAME
                        basename including path (if any) for figure output,
                        default='figout', backend name, figure type, and
                        timestamp will be appended
  --qasm                Print qasm file to stdout before running job
  --qc QC               Indicate circuit name of python-coded QuantumCircuit
  --status              Print status of chosen --backend to stdout (default
                        all backends) of --api_provider (default IBMQ) and
                        exit 0
  --token TOKEN         Use this token
  --url URL             Use this url
```

It is recommended you download or clone the most recent [release](https://github.com/jwoehr/qis_job/releases).

Please use the [issue tracker](https://github.com/jwoehr/qis_job/issues) to report any issues or feature requests.

Jack Woehr 2019-12-26
