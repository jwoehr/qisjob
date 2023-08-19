import unittest
import os
class TestAERMethods(unittest.TestCase):

'''
Test class to test all functions of aer.
'''

def test simulator():
    myCmd = os.popen(qisjob -a --fakenoise FakeVigo share/qasm_examples/entangle.qasm share/qasm_examples/onebit.qasm).read()
    