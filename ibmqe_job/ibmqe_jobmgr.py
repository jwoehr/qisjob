# ibmqe_jobmgr.py
# Class to manage jobs loading qasm source and run jobs with reporting in CSV
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

from IBMQuantumExperience import IBMQuantumExperience


class IBMQEJobSpec:
    """
    Job specification for IBMQEJobManager to run and manage
    """

    def __init__(self, qasm=None filepath=None):
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
    Manage jobs based on an IBMQuantumExperience.IBMQuantumExperience instance
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
        self.run_dict = {}  # dict returned by run_job()
        self.jobs_dict = {}  # jobs dict from run_job()
        self.job_list = []  # list of jobs to run
        self.jobs = []		# list of jobs from jobs_dict

    def parse_jobs(self):
        """Extract list of jobs from dictionary hierarchy"""
        self.jobs = []
        self.jobs_dict = self.run_dict['qasms']
        for i in jobs_dict:
            self.jobs.append(i)

    def add_job(self, jobspec):
        """Add a job to run"""
        self.job_list.append(jobspec.job_spec())

    def run_jobs(self):
        """Pass job list and other parameters to the backend"""
        self.run_dict = self.ibmqe.run_job(
            self.job_list, self.backend, self.counts, self, credits)

    def get_jobnum(self, index):
        """Get job number at server from job record at index in jobs"""
        return jobs[index]['executionId']

    def get_status(self, jobnum):
        """Get job status at server from from server job number"""
        return self.ibmqe.get_job(jobnum)

    def get_job_status(self, index):
        """Get job status at server from index in list of jobs running"""
        return self.get_status(self.get_jobnum(index))
