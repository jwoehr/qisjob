# ibmqe_jobmgr.py
# Class to manage jobs loading qasm source and run jobs with reporting in CSV
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

from IBMQuantumExperience import IBMQuantumExperience

class IBMQEJobMgr:
	"""Make it easier to extract info from the job dictionary
	created by IBMQuantumExperience instance"""

	def __init__(self, jobdict):
		self.jobdict = jobdict

	def get_id(self):
		return self.jobdict['executionId']

	def get_status(self):
		return self.jobdict['status']

class IBMQEJobsMgr:
	"""Manage the array of jobs which is returned by
	IBMQuantumExperience.IBMQuantumExperience.run_job()"""

	def __init__(self, ibmqe, jobs):
		self.ibmqe = ibmqe
		self.jobs = jobs
		self.job_mgr_list = parse_jobs()

	def parse_jobs(self):
		l = []
		jobs_dict = self.jobs['qasms'];
		for i in jobs_dict:
			l.append(IBMQEJobMgr(i))
		return l

	# def get_backend(self):
		# return self.jobdict['backend']