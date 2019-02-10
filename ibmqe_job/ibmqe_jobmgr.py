# ibmqe_jobmgr.py
# Class to manage jobs loading qasm source and run jobs with reporting in CSV
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

# https://github.com/Qiskit/qiskit-api-py
from IBMQuantumExperience import IBMQuantumExperience


class IBMQEJobSpec:
    """
    Job specification for IBMQEJobMgr to run and manage
    """

    def __init__(self, qasm=None, filepath=None):
        self.qasm = qasm
        if filepath is not None:
            self.load_qasm(filepath)

    def load_qasm(self, filepath):
        fh = open(filepath, 'r')
        self.qasm = fh.read()
        fh.close()

    def job_spec(self):
        return {'qasm': self.qasm}


class IBMQEJobMgr:
    """
    Manage job executed by IBMQuantumExperience.IBMQuantumExperience instance
    Using as closely as possible the terminology of qiskit-api-py
    job ...	the overall job which owns the backend/counts/credits etc. attribs
    execution (exec) ... one body of qasm code (out of many) run in job
    """

    def __init__(self, ibmqe, backend='ibmq_qasm_simulator',
                 counts=1024, credits=3):
        """
        ibmqe	...	the IBMQuantumExperience instance
        backend	...	name of backend
        counts	...	times to run
        credits	...	max credits to expend
        """
        self.ibmqe = ibmqe
        self.backend = backend
        self.counts = counts
        self.credits = credits
        self.job_dict = {}  # dict returned by run_job()
        self.exec_dict = {}  # exec dict from job_dict
        self.exec_list = []  # list of execs to run
        self.execs = []		# list of jobs from exec_dict

    def parse_execs(self):
        """Extract list of executions from execution dictionary"""
        self.execs = []
        self.exec_dict = self.job_dict['qasms']
        for i in self.exec_dict:
            self.execs.append(i)

    def add_exec(self, jobspec):
        """Add an exec to run in job"""
        self.exec_list.append(jobspec.job_spec())

    def run_job(self):
        """Pass exec list and other parameters to the backend to run job"""
        self.job_dict = self.ibmqe.run_job(
            self.exec_list, self.backend, self.counts, self.credits)

    def get_job_num(self):
        "Get job number of the job"
        return self.job_dict['id']

    def get_job(self):
        "Get the job dict from the Q server"
        return self.ibmqe.get_job(self.get_job_num())

    def get_job_status(self):
        "Get the job status from the dict returned by the Q server"
        return self.get_job()['status']

    def get_execution_id(self, index):
        """Get execution id for exec found at index in execs[]"""
        return self.execs[index]['executionId']

    def get_execution(self, index):
        """Get execution at server from index in list of execs in job_dict"""
        return self.ibmqe.get_execution(self.get_execution_id(index))

    def get_execution_status(self, index):
        """Get execution status  for exec found at index in execs[]"""
        return self.get_execution(index)['status']

    def get_execution_result(self, index):
        """Get execution result  for exec found at index in execs[]"""
        return self.get_execution(index)['result']
