import unittest
import os
class TestAERMethods(unittest.TestCase):

    '''
    Test class to test all functions of aer.
    '''

    def test_aer(self):
        from qisjob import QisJob
        qj = QisJob()
        qj.use_aer=True
        qj.filepaths=['Qisj/share/qisjob/qasm_examples/entangle.qasm']
        qj.do_it()
        #print('result= ',qj.test_results)
        self.assertTrue(len(qj.test_results)==1)
        qj.filepaths=['Qisj/share/qisjob/qasm_examples/ghzstate3q.qasm','Qisj/share/qisjob/qasm_examples/multimeasure.qasm','Qisj/share/qisjob/qasm_examples/mermin_inequality_a.qasm','Qisj/share/qisjob/qasm_examples/entangle.qasm']
        qj.do_it()
        self.assertTrue(len(qj.test_results)==5)
        counts1= {'01111': 128, '01101': 128, '01100': 128, '01000': 128, '01001': 128, '01010': 128, '01110': 128, '01011': 128}
        self.assertTrue(within_error(qj.test_results[0].get_counts(qj.circuit[0]),counts1))


     

    '''def test_Parser():
        test_a = os.popen(qisjob -a share/qasm_examples/entangle.qasm share/qasm_examples/onebit.qasm).read()
        self.assertTrue(test_a)

        myCmd = os.popen(qisjob -a --fakenoise FakeVigo share/qasm_examples/entangle.qasm share/qasm_examples/onebit.qasm).read()'''



def within_error(counts1,counts2):#Returns boolean, checks if the given counts match in a determined error range 
    for state in counts1:
        error=5
        if int(counts1[state])<=error:
            continue
        if int(counts1[state])*20/100>error:
            error=int(counts1[state])*20/100
        if int(counts1[state])+error<int(counts2[state]) or int(counts1[state])-error>int(counts2[state]):
            print('c1',counts1)
            print('c2',counts2)
            return False
        return True
        