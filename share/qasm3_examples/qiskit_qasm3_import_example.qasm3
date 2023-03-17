OPENQASM 3.0;
// This example from the qiskit-qasm3-import repository https://github.com/Qiskit/qiskit-qasm3-import
// licenced under the Apache License 2.0 https://www.apache.org/licenses/LICENSE-2.0
// The 'stdgates.inc' include is supported, and the gates are only available
// if it has correctly been included.
include "stdgates.inc";

// Parametrised inputs are supported.
input float[64] a;

qubit[3] q;
bit[2] mid;
bit[3] out;

// Aliasing and re-aliasing are supported.
let aliased = q[0:1];

// Parametrised gates that make use of the stdlib.
gate my_gate(a) c, t {
  gphase(a / 2);
  ry(a) c;
  cx c, t;
}

// Gate modifiers work as well; this gate is equivalent to `p(-a) c;`.
gate my_phase(a) c {
  ctrl @ inv @ gphase(a) c;
}

// We handle mathematical expressions on gate creation and complex indexing
// of temporary collections.
my_gate(a * 2) aliased[0], q[{1, 2}][0];
measure q[0] -> mid[0];
measure q[1] -> mid[1];

while (mid == "00") {
  reset q[0];
  reset q[1];
  my_gate(a) q[0], q[1];
  // We support the builtin mathematical symbols.
  my_phase(a - pi/2) q[1];
  mid[0] = measure q[0];
  mid[1] = measure q[1];
}

// The condition resolver can also handle simple cases that don't look
// _exactly_ like equality conditions.
if (mid[0]) {
  // There is limited support for aliasing within nested scopes.
  let inner_alias = q[{0, 1}];
  reset inner_alias;
}

out = measure q;

