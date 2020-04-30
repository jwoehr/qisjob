// yiqing_5.qasm
// This is a version of yiqing_simple declared as 5 qubits
// so that it will run on the QuantumInspire Starmon-5 QPU
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[5];
h q[0];
h q[1];
h q[2];
// h q[3];
// h q[4];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
// measure q[3] -> c[3];
// measure q[4] -> c[4];
