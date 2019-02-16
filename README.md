# qis_job
QISKit Job Control

**`qis_job`** provides [IBM Q Experience](https://quantumexperience.ng.bluemix.net/qx) argument-parsing job and experiment execution scripts. This project is largely an exercise for demonstrating QISKit on various platforms, particularly the IBM i.

* `ibmqe` contains those based on QISKit's now-deprecated [`IBMQuantumExperience`](https://github.com/Qiskit/qiskit-api-py).
  * The `IBMQuantumExperience` library is the only one which as of this writing (2019-02-15) can be compiled on IBM i.
  * You will need to install the latest version of [Qiskit/qiskit-api-py](https://github.com/Qiskit/qiskit-api-py) to use this.
    * I have found a bug which is patched in [jwoehr/qiskit-api-py forked from Qiskit/qiskit-api-py](https://github.com/jwoehr/qiskit-api-py).
    * A pull request has been submitted.
  * You will need an [IBM Q Experience API token](https://quantumexperience.ng.bluemix.net/qx/account/advanced)    
  * Additionally, there are example qasm programs in this project.   
* `qasm_job` contains those based on later full [QISKit](https://github.com/Qiskit) setup.
  * For this project you will need to install
    * [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
    * [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
    * An [IBM Q Experience API token](https://quantumexperience.ng.bluemix.net/qx/account/advanced)
    
Jack Woehr 2019-02-15
