# test file to test methods of aer simulator
# use
# python -m unittest Test/test_aer.py
# in qisjob directoory to run


import unittest
import os
from qisjob import QisJob

qj = QisJob()
qj.filepaths = ["share/qasm_examples/entangle.qasm"]
counts1 = {
    "01111": 128,
    "01101": 128,
    "01100": 128,
    "01000": 128,
    "01001": 128,
    "01010": 128,
    "01110": 128,
    "01011": 128,
}
test_number = 0


class TestAERMethods(unittest.TestCase):

    """
    Test class to test all functions of aer.
    """

    def test_aer(self):
        global test_number
        print(test_number, "Testing AER SIMULATOR ")
        qj.filepaths = ["share/qasm_examples/entangle.qasm"]
        qj.use_aer = True
        qj.do_it()
        self.assertTrue(
            within_error(
                counts1,
                qj.test_results[test_number].get_counts(qj.circuit[test_number]),
            )
        )
        test_number += 1

    def test_qasm(self):
        global test_number
        print(test_number, "Testing QASM SIMULATOR ")
        qj.filepaths = ["share/qasm_examples/entangle.qasm"]
        qj.use_aer = True
        qj.use_qasm_simulator = True
        qj.do_it()
        self.assertTrue(
            within_error(
                counts1,
                qj.test_results[test_number].get_counts(qj.circuit[test_number]),
            )
        )
        test_number += 1

    def test_statevector_sim(self):
        global test_number
        print(test_number, "Testing STATE VECOTR SIMULATOR ")
        qj.filepaths = ["share/qasm_examples/entanglecircuit.qasm"]
        qj.use_aer = True
        qj.use_statevector_simulator = True
        qj.do_it()
        self.assertTrue(qj.test_results[2])
        test_number += 1

    def test_unitary_sim(self):
        global test_number
        print(test_number, "Testing UNITARY SIMULATOR ")
        qj.filepaths = ["share/qasm_examples/entanglecircuit.qasm"]
        qj.use_aer = True
        qj.use_unitary_simulator = True
        qj.do_it()
        self.assertTrue(qj.test_results[3])
        test_number += 1

    def test_densitymatrix_sim(self):
        global test_number
        print(test_number, "Testing DENSITY MATRIX SIMULATOR ")
        qj.filepaths = ["share/qasm_examples/onebitcircuit.qasm"]
        qj.use_aer = True
        qj.use_aer_simulator_density_matrix = True
        qj.do_it()
        self.assertTrue(qj.use_aer and qj.local_simulator_type)
        test_number += 1

    def test_aer_noise(self):
        global test_number
        print(test_number, "Testing NOISY AER SIMULATOR ")
        qj.filepaths = ["share/qasm_examples/entangle.qasm"]
        qj.use_aer = True
        qj.fake_noise = "FakeVigo"
        qj.do_it()
        self.assertTrue(
            within_error(
                counts1,
                qj.test_results[test_number].get_counts(qj.circuit[test_number]),
            )
        )
        test_number += 1
        qj.fake_noise = False


def within_error(
    counts1, counts2
):  # Returns boolean, checks if the given counts match in a determined error range
    for state in counts1:
        error = 10
        if int(counts1[state]) <= error:
            continue
        if int(counts1[state]) * 20 / 100 > error:
            error = int(counts1[state]) * 20 / 100
        if int(counts1[state]) + error < int(counts2[state]) or int(
            counts1[state]
        ) - error > int(counts2[state]):
            print("c1=", counts1)
            print("c2=", counts2)
            return False
        return True
