"""
ibmqe_jobmgr.py
Class to manage jobs loading qasm source and run jobs with reporting in CSV
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

https://github.com/Qiskit/qiskit-api-py
pip install qiskit-api-py
"""
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
    job ...    the overall job which owns the backend/counts/credits etc. attribs
    execution (exec) ... one body of qasm code (out of many) run in job
    """

    def __init__(self, ibmqe, backend='ibmq_qasm_simulator',
                 counts=1024, credits=3):
        """
        ibmqe    ...    the IBMQuantumExperience instance
        backend    ...    name of backend
        counts    ...    times to run
        credits    ...    max credits to expend
        """
        self.ibmqe = ibmqe
        self.backend = backend
        self.counts = counts
        self.credits = credits
        self.job_dict = {}  # dict returned by run_job()
        self.exec_dict = {}  # exec dict from job_dict
        self.exec_list = []  # list of execs to run
        self.execs = []        # list of jobs from exec_dict

    def add_exec(self, jobspec):
        """Add an exec to run in job"""
        self.exec_list.append(jobspec.job_spec())

    def parse_execs(self):
        """Extract list of executions from execution dictionary"""
        self.execs = []
        self.exec_dict = self.job_dict['qasms']
        for i in self.exec_dict:
            self.execs.append(i)

    def run_job(self):
        """Pass exec list and other parameters to the backend to run job"""
        self.job_dict = self.ibmqe.run_job(
            self.exec_list, self.backend, self.counts, self.credits)
        self.parse_execs()

    def get_job_id(self):
        """Get job number of the job"""
        return self.job_dict['id']

    def get_job(self):
        """Get the job dict from the Q server and refresh local copy"""
        self.job_dict = self.ibmqe.get_job(self.get_job_id())
        self.parse_execs()
        return self.job_dict

    def get_job_status(self):
        """
        Get the job status from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job()
        if 'status' in d:
            return d['status']
        else:
            return None

    def get_job_qasms(self):
        """
        Get the job qasms from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['qasms']

    def get_job_qasms_qasm(self, index):
        """
        Get job qasms qasm text for indexed job  from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job_qasms()[index]['qasm']

    def get_job_qasms_data(self, index):
        """
        Get the job qasms data for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms()[index]
        if d and 'data' in d:
            return self.get_job_qasms()[index]['data']
        else:
            return None

    def get_job_qasms_data_creg_labels(self, index):
        """
        Get job qasms data creg_labels for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms_data(index)
        if d:
            return self.get_job_qasms_data(index)['creg_labels']
        else:
            return None

    def get_job_qasms_data_additionalData(self, index):
        """
        Get job qasms data additionalData for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms_data(index)
        if d:
            return self.get_job_qasms_data(index)['additionalData']
        else:
            return None

    def get_job_qasms_data_versionSimulationRun(self, index):
        """
        Get job qasms data versionSimulationRun for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms_data(index)
        if d:
            return self.get_job_qasms_data(index)['versionSimulationRun']
        else:
            return None

    def get_job_qasms_data_time(self, index):
        """
        Get job qasms data time for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms_data(index)
        if d:
            return self.get_job_qasms_data(index)['time']
        else:
            return None

    def get_job_qasms_data_counts(self, index):
        """
        Get job qasms data counts for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms_data(index)
        if d:
            return self.get_job_qasms_data(index)['counts']
        else:
            return None

    def get_job_qasms_data_date(self, index):
        """
        Get the job qasms data date for indexed job from dict returned by Q server
        Implicitly refreshes local job dict from Q server
        """
        d = self.get_job_qasms_data(index)
        if d:
            return self.get_job_qasms_data(index)['date']
        else:
            return None

    def get_job_shots(self):
        """
        Get the job shots from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['shots']

    def get_job_backend(self):
        """
        Get the job backend from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['backend']

    def get_job_maxCredits(self):
        """
        Get the job maxCredits from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['maxCredits']

    def get_job_usedCredits(self):
        """
        Get the job usedCredits from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['usedCredits']

    def get_job_creationDate(self):
        """
        Get the job creationDate from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['creationDate']

    def get_job_deleted(self):
        """
        Get the job deleted from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['deleted']

    def get_job_userId(self):
        """
        Get the job userId from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['userId']

    def get_job_calibration(self):
        """
        Get the job calibration from the dict returned by the Q server
        Implicitly refreshes local job dict from Q server
        """
        return self.get_job()['calibration']

    def get_execution_id(self, index):
        """Get execution id for exec found at index in execs[]"""
        return self.execs[index]['executionId']

    def get_execution(self, index):
        """Get execution at server from index in list of execs in job_dict"""
        return self.ibmqe.get_execution(self.get_execution_id(index))

    def get_execution_status(self, index):
        """Get execution status for exec found at index in execs[]"""
        return self.get_execution(index)['status']

    def get_execution_result(self, index):
        """Get execution result for exec found at index in execs[]"""
        return self.get_execution(index)['result']

    def get_execution_result_date(self, index):
        """Get execution result entry date for indexed execution"""
        return self.get_execution_result(index)['date']

    def get_execution_result_data(self, index):
        """Get execution result entry data for indexed execution"""
        return self.get_execution_result(index)['data']

    def get_execution_result_creg_labels(self, index):
        """Get execution result entry creg_labels for indexed execution"""
        return self.get_execution_result_data(index)['creg_labels']

    def get_execution_result_p(self, index):
        """Get execution result entry p for indexed execution"""
        return self.get_execution_result_data(index)['p']

    def get_execution_result_qubits(self, index):
        """Get execution result entry qubits for indexed execution"""
        return self.get_execution_result_p(index)['qubits']

    def get_execution_result_labels(self, index):
        """Get execution result entry labels for indexed execution"""
        return self.get_execution_result_p(index)['labels']

    def get_execution_result_values(self, index):
        """Get execution result entry values for indexed execution"""
        return self.get_execution_result_p(index)['values']

    def get_execution_result_additionalData(self, index):
        """Get execution result entry additionalData for indexed execution"""
        return self.get_execution_result_data(index)['additionalData']

    def get_execution_result_seed(self, index):
        """Get execution result entry seed for indexed execution"""
        return self.get_execution_result_additionalData(index)['seed']

    def get_execution_result_qasm(self, index):
        """Get execution result entry qasm for indexed execution"""
        return self.get_execution_result_data(index)['qasm']

    def get_execution_result_serialNumberDevice(self, index):
        """Get execution result entry serialNumberDevice for indexed execution"""
        return self.get_execution_result_data(index)['serialNumberDevice']

    def get_execution_result_versionSimulationRun(self, index):
        """Get execution result entry versionSimulationRun for indexed execution"""
        return self.get_execution_result_data(index)['versionSimulationRun']

    def get_execution_result_time(self, index):
        """Get execution result entry time for indexed execution"""
        return self.get_execution_result_data(index)['time']

    def csv_execution(self, description, index):
        """Express one execution as CSV with description, labels and values."""
        csv = []
        csv.append(description)
        labels = ""
        for i in self.get_execution_result_labels(index):
            labels += str(i) + ';'
        csv.append(labels)
        values = ""
        for i in self.get_execution_result_values(index):
            values += str(i) + ';'
        csv.append(values)
        return csv

    @staticmethod
    def test(ibmqe_token, qasmfile):
        """Run a comprehensive test give a server token and a qasm filepath"""
        import time
        api = IBMQuantumExperience(ibmqe_token)
        jx = IBMQEJobMgr(api)
        js = IBMQEJobSpec(filepath=qasmfile)
        jx.add_exec(js)
        jx.add_exec(js)
        jx.add_exec(js)
        jx.run_job()
        print(jx.get_job_id())
        print(jx.get_job())
        # time.sleep(4)
        while jx.get_job_status() != 'COMPLETED':
            print(jx.get_job_status())
            time.sleep(4)
        print(jx.get_job_qasms())
        print(jx.get_job_qasms_qasm(0))
        print(jx.get_job_qasms_qasm(1))
        print(jx.get_job_qasms_qasm(2))
        print(jx.get_job_qasms_data(0))
        print(jx.get_job_qasms_data(1))
        print(jx.get_job_qasms_data(2))
        print(jx.get_job_qasms_data_creg_labels(0))
        print(jx.get_job_qasms_data_creg_labels(1))
        print(jx.get_job_qasms_data_creg_labels(2))
        print(jx.get_job_qasms_data_additionalData(0))
        print(jx.get_job_qasms_data_additionalData(1))
        print(jx.get_job_qasms_data_additionalData(2))
        print(jx.get_job_qasms_data_versionSimulationRun(0))
        print(jx.get_job_qasms_data_versionSimulationRun(1))
        print(jx.get_job_qasms_data_versionSimulationRun(2))
        print(jx.get_job_qasms_data_time(0))
        print(jx.get_job_qasms_data_time(1))
        print(jx.get_job_qasms_data_time(2))
        print(jx.get_job_qasms_data_counts(0))
        print(jx.get_job_qasms_data_counts(1))
        print(jx.get_job_qasms_data_counts(2))
        print(jx.get_job_qasms_data_date(0))
        print(jx.get_job_qasms_data_date(1))
        print(jx.get_job_qasms_data_date(2))
        print(jx.get_job_shots())
        print(jx.get_job_backend())
        print(jx.get_job_maxCredits())
        print(jx.get_job_usedCredits())
        print(jx.get_job_creationDate())
        print(jx.get_job_deleted())
        print(jx.get_job_userId())
        print(jx.get_job_calibration())
        print(jx.get_execution_id(0))
        print(jx.get_execution_id(1))
        print(jx.get_execution_id(2))
        print(jx.get_execution(0))
        print(jx.get_execution(1))
        print(jx.get_execution(2))
        print(jx.get_execution_status(0))
        print(jx.get_execution_status(1))
        print(jx.get_execution_status(2))
        print(jx.get_execution_result(0))
        print(jx.get_execution_result(1))
        print(jx.get_execution_result(2))
        print(jx.get_execution_result_date(0))
        print(jx.get_execution_result_date(1))
        print(jx.get_execution_result_date(2))
        print(jx.get_execution_result_data(0))
        print(jx.get_execution_result_data(1))
        print(jx.get_execution_result_data(2))
        print(jx.get_execution_result_creg_labels(0))
        print(jx.get_execution_result_creg_labels(1))
        print(jx.get_execution_result_creg_labels(2))
        print(jx.get_execution_result_p(0))
        print(jx.get_execution_result_p(1))
        print(jx.get_execution_result_p(2))
        print(jx.get_execution_result_qubits(0))
        print(jx.get_execution_result_qubits(1))
        print(jx.get_execution_result_qubits(2))
        print(jx.get_execution_result_labels(0))
        print(jx.get_execution_result_labels(1))
        print(jx.get_execution_result_labels(2))
        print(jx.get_execution_result_values(0))
        print(jx.get_execution_result_values(1))
        print(jx.get_execution_result_values(2))
        print(jx.get_execution_result_additionalData(0))
        print(jx.get_execution_result_additionalData(1))
        print(jx.get_execution_result_additionalData(2))
        print(jx.get_execution_result_seed(0))
        print(jx.get_execution_result_seed(1))
        print(jx.get_execution_result_seed(2))
        print(jx.get_execution_result_qasm(0))
        print(jx.get_execution_result_qasm(1))
        print(jx.get_execution_result_qasm(2))
        print(jx.get_execution_result_serialNumberDevice(0))
        print(jx.get_execution_result_serialNumberDevice(1))
        print(jx.get_execution_result_serialNumberDevice(2))
        print(jx.get_execution_result_versionSimulationRun(0))
        print(jx.get_execution_result_versionSimulationRun(1))
        print(jx.get_execution_result_versionSimulationRun(2))
        print(jx.get_execution_result_time(0))
        print(jx.get_execution_result_time(1))
        print(jx.get_execution_result_time(2))
        print(jx.csv_execution("test 0", 0))
        print(jx.csv_execution("test 1", 1))
        print(jx.csv_execution("test 2", 2))


if __name__ == "__main__":

    explanation = """ibmqe_jobmgr.py :
Class to manage jobs loading qasm source and run jobs with reporting in CSV
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
Exits (1) on status error.
Exits (2) on device error.
Exits (200) on no backend chosen.
Exits (300) on no filepaths given.
"""
    import argparse
    import sys
    import time
    import datetime

    now = datetime.datetime.now().isoformat()

    parser = argparse.ArgumentParser(description=explanation)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--sim", action="store_true",
                       help="Use IBMQ qasm simulator")
    group.add_argument("-b", "--backend", action="store",
                       help="Use specified IBM backend")
    parser.add_argument("-c", "--credits", type=int, action="store", default=3,
                        help="Max credits to expend on run, default is 3")
    parser.add_argument("-n", "--name", action="store",
                        default=now,
                        help="Your name for this experiment, default is timestamp")
    parser.add_argument("-m", "--timeout", type=int, action="store", default=60,
                        help="Timeout in seconds, default is 60")
    parser.add_argument("-o", "--outfile", action="store",
                        help="Write CSV to outfile overwriting silently, default is stdout")
    parser.add_argument("-q", "--qubits", type=int, action="store", default=5,
                        help="Number of qubits for the experiment, default is 5")
    parser.add_argument("-t", "--shots", type=int, action="store", default=1024,
                        help="Number of shots for the experiment, default is 1024")
    parser.add_argument("-u", "--url",  action="store", default='https://quantumexperience.ng.bluemix.net/api',
                        help="URL, default is https://quantumexperience.ng.bluemix.net/api")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity each -v up to 3")
    parser.add_argument("token", help="""IBM Q Experience API token
                    (See https://quantumexperience.ng.bluemix.net/qx/account/advanced)""")
    parser.add_argument("filepaths", nargs=argparse.REMAINDER,
                        help="Filepaths to 1 or more .qasm files")

    args = parser.parse_args()

    # print(args)

    def verbosity(text, count):
        if args.verbose >= count:
            print(text)

    # Connect to IBMQE
    api = IBMQuantumExperience(args.token, config={
        "url": args.url}, verify=True)

    # Choose backend
    if args.backend:
        backend = args.backend
    elif args.sim:
        backend = 'ibmq_qasm_simulator'
    else:
        print("No backend chosen, exiting.")
        exit(200)

    # Check for filepath(s)
    if args.filepaths == []:
        print("No filepath(s) for qasm file(s) given, exiting.")
        exit(300)

    jx = IBMQEJobMgr(api, backend=backend,
                     counts=args.shots, credits=args.credits)

    for filepath in args.filepaths:
        jx.add_exec(IBMQEJobSpec(filepath=filepath))

    jx.run_job()

    while jx.get_job_status() != 'COMPLETED':
        print(jx.get_job_status())
        time.sleep(4)

    print(jx.get_job())

    for i in range(0, len(jx.execs)):
        csv = jx.csv_execution(args.filepaths[i], i)
        for c in csv:
            print(c)

    exit()

# Fin
