// entangle.qasm
//
// Demonstrates entanglement in quantum computing
//
// This file is free software no warranty no guarantee copy as you will.
// jack woehr jwoehr@softwoehr.com https://github.com/jwoehr/qisjob


OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[3];

h q[0];
h q[1];
h q[2];
cx q[0],q[1];
cx q[1],q[2];
barrier q;
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
