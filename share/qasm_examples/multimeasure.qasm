// multimeasure.qasm
//
// Demonstrates multimeasure on backends which support multimeasure
//
// `qisjob --backend _whatever_ --configuration` and look for:
//
//          'multi_meas_enabled': True
//
// to determine whether a backend supports multimeasure.
//
// This program's canonical outcome is 00111.
//
// This file is free software no warranty no guarantee copy as you will.
// jack woehr jwoehr@softwoehr.com https://github.com/jwoehr/qisjob


OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
creg c[5];

x q[0];
x q[1];
x q[2];
cx q[0],q[3];
cx q[1],q[4];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
barrier q;
x q[3];
x q[4];
measure q[3] -> c[3];
measure q[4] -> c[4];