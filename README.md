# qis_job
QISKit Job Control

**`qis_job`** is an [IBM Q Experience](https://quantumexperience.ng.bluemix.net/qx) argument-parsing job and experiment execution script.

* `qasm_job` contains those based on later full [QISKit](https://github.com/Qiskit) setup.
  * For this project you will need to install
    * [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
    * [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
    * An [IBM Q Experience API token](https://quantumexperience.ng.bluemix.net/qx/account/advanced)
* *DEPRECATED* `ibmqe` contains those based on QISKit's now-deprecated [`IBMQuantumExperience`](https://github.com/Qiskit/qiskit-api-py).
  * You will need to install the latest version of [Qiskit/qiskit-api-py](https://github.com/Qiskit/qiskit-api-py) to use this.
  * I have found a bug which is patched in [jwoehr/qiskit-api-py forked from Qiskit/qiskit-api-py](https://github.com/jwoehr/qiskit-api-py).
    * A pull request was submitted and withdrawn, as the team has deprecated that portion of the code.
  * You will need an [IBM Q Experience API token](https://quantumexperience.ng.bluemix.net/qx/account/advanced)
  * Additionally, there are example qasm programs in this project.

```
$ python qasm_job.py -h
usage: qasm_job.py [-h] [-i | -s | -a | -b BACKEND] [-c CREDITS] [-j] [-m]
                   [-o OUTFILE] [-p PROPERTIES] [-q QUBITS] [--qiskit_version]
                   [-r] [-t SHOTS] [-v] [-x]
                   [filepath]

qasm_job.py : Load from qasm source and run job with reporting in CSV form.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO
80402-0051. BSD-3 license -- See LICENSE which you should have received with
this code. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

positional arguments:
  filepath              Filepath to .qasm file, default is stdin

optional arguments:
  -h, --help            show this help message and exit
  -i, --ibmq            Use best genuine IBMQ processor (default)
  -s, --sim             Use IBMQ qasm simulator
  -a, --aer             Use QISKit aer simulator
  -b BACKEND, --backend BACKEND
                        Use specified IBM backend
  -c CREDITS, --credits CREDITS
                        Max credits to expend on run, default is 3
  -j, --job             Print job dictionary
  -m, --memory          Print individual results of multishot experiment
  -o OUTFILE, --outfile OUTFILE
                        Write CSV to outfile overwriting silently, default is
                        stdout
  -p PROPERTIES, --properties PROPERTIES
                        Print properties for specified backend to stdout and
                        exit 0
  -q QUBITS, --qubits QUBITS
                        Number of qubits for the experiment, default is 5
  --qiskit_version      Print Qiskit version and exit 0
  -r, --result          Print job result
  -t SHOTS, --shots SHOTS
                        Number of shots for the experiment, default is 1024
  -v, --verbose         Increase verbosity each -v up to 3
  -x, --transpile       Show circuit transpiled for chosen backend
```

Jack Woehr 2019-06-04
