// entangle.qasm
//
// Demonstrates entanglement in quantum computing
//
// This file is free software no warranty no guarantee copy as you will.
// jack woehr jwoehr@softwoehr.com https://github.com/jwoehr/qisjob


OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
creg c[5];

h q[0];
h q[1];
h q[2];
cx q[0],q[1];
cx q[1],q[2];
barrier q;
x q[3];
h q[3];
h q[4];
cx q[3],q[4];
h q[3];
h q[4];
measure q -> c;

