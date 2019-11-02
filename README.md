# qis_job
QISKit Job Control

**`qis_job`** is the (historical) name of this project which provides an [IBM Q Experience](https://quantum-computing.ibm.com)
argument-parsing [OPENQASM Open Quantum Assembly Language](https://arxiv.org/abs/1707.03429) experiment execution script.

* `qasm_job.py` is the name of the script. The current releases are based on the [QISKit](https://github.com/Qiskit) API 2.
  * See the earlier release [Qis Job v0.7](https://github.com/jwoehr/qis_job/releases/tag/v0.7) for API 1 support.
  * For this project you will need to install
    * [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
    * [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
    * A provider such as [Qiskit/qiskit-ibmq-provider](https://github.com/Qiskit/qiskit-ibmq-provider)
      * If you choose the IBMQ provider, you will need an
      [IBM Q Experience API token](https://quantum-computing.ibm.com/account)
      * If you choose the QI provider you will need to install QuTech-Delft/quantuminspire either
      from [Github QuTech-Delft/quantuminspire](https://github.com/QuTech-Delft/quantuminspire)
      or with the command `pip install quantuminspire`. You will also need a
      [Quantum Inspire token](https://www.quantum-inspire.com/account).
      * **Note**: Currently only IBMQ and QI are supported as providers.
    * To use the qcgpu simulator, install [qiskit-community/qiskit-qcgpu-provider](https://github.com/qiskit-community/qiskit-qcgpu-provider)

* Additionally, there are example qasm programs in the `qasm_examples` directory.

```
usage: qasm_job.py [-h] [-i | -s | -a | --qcgpu | -b BACKEND]
                   [--qasm_simulator | --unitary_simulator]
                   [--api_provider API_PROVIDER] [--backends] [-1]
                   [-c CREDITS] [-g] [-j] [--jobs JOBS] [--job_id JOB_ID]
                   [--job_result JOB_RESULT] [-m] [-o OUTFILE] [-p]
                   [-q QUBITS] [--qiskit_version] [-r] [-t SHOTS] [-v] [-x]
                   [--histogram] [--plot_state_city PLOT_STATE_CITY]
                   [--figure_basename FIGURE_BASENAME] [--qasm] [--status]
                   [--token TOKEN] [--url URL]
                   [filepath [filepath ...]]

qasm_job.py : Loads from one or more qasm source files and runs experiments
with reporting in CSV form. Also can give info on backend properties, qiskit
version, transpilation, etc. Can run as multiple jobs or all as one job.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO
80402-0051. BSD-3 license -- See LICENSE which you should have received with
this code. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

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
                        [IBMQ | QI]. Default is IBMQ.
  --backends            Print list of backends to stdout and exit
  -1, --one_job         Run all experiments as one job
  -c CREDITS, --credits CREDITS
                        Max credits to expend on each job, default is 3
  -g, --configuration   Print configuration for backend specified by -b to
                        stdout and exit 0
  -j, --job             Print your job's dictionary
  --jobs JOBS           Print JOBS jobs and status for -b backend and exit
  --job_id JOB_ID       Print job number JOB_ID for -b backend and exit
  --job_result JOB_RESULT
                        Print result of job number JOB_RESULT for -b backend
                        and exit
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
  --histogram           Write image file of histogram of experiment results
  --plot_state_city PLOT_STATE_CITY
                        Write image file of state city plot of statevector to
                        PLOT_STATE_CITY decimal points
  --figure_basename FIGURE_BASENAME
                        basename including path (if any) for figure output,
                        default='figout', backend name, figure type, and
                        timestamp will be appended
  --qasm                Print qasm file to stdout before running job
  --status              Print status of chosen --backend to stdout (default
                        all backends) of --api_provider (default IBMQ) and
                        exit
  --token TOKEN         Use this token
  --url URL             Use this url
```

It is recommended you download or clone the most recent [release](https://github.com/jwoehr/qis_job/releases).

Please use the [issue tracker](https://github.com/jwoehr/qis_job/issues) to report any issues or feature requests.

Jack Woehr 2019-10-30
