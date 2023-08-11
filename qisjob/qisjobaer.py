#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`qisjobaer.py`

Class to manage the Qiskit AerSimulator for QisJob
Created on Sat Dec 24 16:47:34 2022

Copyright 2019, 2022 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81023-0082

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
@author: jwoehr
"""


from qiskit.providers.exceptions import QiskitBackendNotFoundError
from .qisjobex import QisJobException, QisJobArgumentException, QisJobRuntimeException
from qiskit import QuantumCircuit
class QisJobAer:
    # """
    # Class to manage the Qiskit AerSimulator for QisJob
    # """

    # def simulator(self) -> Simulator:
    #     """
    #     Take processed kwargs and use them to instance an AerSimulator

    #     Returns
    #     -------
    #     Simulator
    #         The Simulator to process the QisJob

    #     """

    #@staticmethod
    def basic_noise_sim(circ, qj):
        """
        Execute a simulator job with a basic noise model from a known backend.

        Parameters
        ----------
        quantum circuit and the self object from qisjob.py

        Returns
        -------
        Job
            The job which is executing the circuit

        """
        from qiskit import IBMQ
        from qiskit.providers.aer.noise import NoiseModel
        from qiskit_aer.noise import NoiseModel
        try:
            if 'ibm' in qj.fake_noise:
                provider = IBMQ.load_account()
                provider = IBMQ.get_provider(hub='ibm-q', group='open', project='main')
                model_backend=provider.get_backend(qj.fake_noise)
            
            if 'fake' in qj.fake_noise.lower():
                import importlib
                fnoise=qj.fake_noise[4:].lower()
                module=importlib.import_module("qiskit.providers.fake_provider.backends."+fnoise+".fake_"+fnoise)
                model_backend= getattr(module, qj.fake_noise)
                model_backend=model_backend()
            noise_model = NoiseModel.from_backend(model_backend)
            coupling_map = model_backend.configuration().coupling_map
            basis_gates = noise_model.basis_gates

        except QiskitBackendNotFoundError as err:
                raise QisJobRuntimeException(
                    f"Backend {qj.backend_name} not found: {err}"
                ) 
        
        # Perform noisy simulation
        print('simulating noise via '+ qj.fake_noise)
        sim_backend = qj.backend
        from qiskit import execute
        job = execute(
            circ,
            sim_backend,
            coupling_map=coupling_map,
            noise_model=noise_model,
            basis_gates=basis_gates,
        )
        
        return job

    
    
    @staticmethod
    def simulator(
        qj
    ):  
        "returns the simulator and its method asked as string"

        simulator = 'aer_simulator'
        # Choose simulator. We defaulted in __init__() to AerSimulator()
        if qj.use_qasm_simulator:
            simulator = 'qasm_simulator'
        elif qj.use_unitary_simulator:
            simulator = 'unitary_simulator'
        elif qj.use_statevector_simulator:
            simulator = 'statevector_simulator'
        elif qj.use_pulse_simulator:
            simulator = 'pulse_simulator'
        elif qj.use_aer_simulator_density_matrix:
            simulator = 'aer_simulator_density_matrix'
        
        # Choose method kwarg for gpu etc if present
        elif qj.use_statevector_gpu:
            qj.method = "statevector_gpu"
        elif qj.use_unitary_gpu:
            qj.method = "unitary_gpu"
        elif qj.use_density_matrix_gpu:
            qj.method = "density_matrix_gpu"
        return (simulator,qj.method)


    @staticmethod
    def run_aer(self,circ):#self is an object sent by qisjob.py, self name makes it easy move code from qisjob.py        
        "Run the simulations for Aer and return the Job"

        if self.fake_noise:#calling the noise function for fake noise
            job= QisJobAer.basic_noise_sim(circ, self)
        
        elif self.method:
                self.verbosity(f"Using gpu method {self.method}", 2)
                backend_options = {"method": self.method}
                from qiskit import execute
                job = execute(
                    circ,
                    backend=self.backend,
                    backend_options=backend_options,
                    optimization_level=self.optimization_level,
                    shots=self.shots,
                    memory=self.memory,
                )
                '''elif self.use_aer:
                from .qisjobaer import QisJobAer
                simulator=QisJobAer.simulator(self,circ)
                result_exp=QisJobAer.run_aer(simulator,circ)'''    

        else:            
            simulator=self.backend
            # Transpile for simulator
            from qiskit import transpile
            circ = transpile(circ, simulator)
            # Run and get counts
            job = simulator.run(circ)
        return job
    
    


    
    
