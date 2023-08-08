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

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit.providers import BackendV2
from .qisjobex import QisJobArgumentException
from qiskit import Aer, transpile


class QisJobAer:
    """
    Class to manage the Qiskit AerSimulator for QisJob
    """

    simulator_kwargs = [
        "backend_named",
        "configuration",
        "method",
        "noise_model",
        "noise_model_backend",
        "properties",
    ]

    def __init__(self, **kwargs):
        """
        Instance this Aer Simulator manager

        Parameters
        ----------
        **kwargs :
            Arguments passed in from QisJob to be processed into valid
            arguments for instancing an Aer Simulator.

        Returns
        -------
        None.

        """
        self.configuration = None
        self.properties = None
        self.provider = None
        self.method = None
        self.backend = None
        self.backend_named = None
        self.process_kwargs(**kwargs)
        self.aer_simulator = self.instance_aer_simulator()

    def process_kwargs(self, kwargs):
        """
        Process string kwargs from QisJob to formulate valid arguments to
        instance an AerSimulator.

        Parameters
        ----------
        kwargs : dict
            kwargs as passed in from QisJob to be translated to valid args/kwargs
            to instance an AerSimulator.

        Raises
        ------
        QisJobArgumentException
            If any kwargs aren't recognized.

        Returns
        -------
        None.

        """
        for kwarg in kwargs:
            if not kwarg in self.simulator_kwargs:
                raise QisJobArgumentException(
                    f"Unknown kwarg {kwarg} for Aer Simulator"
                )
        if "noise_model" in kwargs and "noise_model_backend" in kwargs:
            raise QisJobArgumentException(
                "noise_model and noise_model_backend are mutually exclusive"
            )
        if "method" in kwargs:
            self.method = kwargs["method"]

    def instance_aer_simulator(self) -> AerSimulator:
        """
        Take processed kwargs and use them to instance an AerSimulator

        Returns
        -------
        AerSimulator
            The AerSimulator to process the QisJob

        """
        the_args = []
        return AerSimulator(**the_args)
    


    def run_aer(simulator,circ):        
        # Transpile for simulator
        circ = transpile(circ, simulator)
        # Run and get counts
        job = simulator.run(circ)
        print(simulator)
        return job
    

    def simulator(
        self
    ):  # pylint: disable-msg=too-many-branches, too-many-statements
        """Instance self with backend selected by user if account will
        activate and allow."""

        from qiskit_aer import AerSimulator
        self.backend = AerSimulator()
        from qiskit import Aer, transpile
        simulator = 'aer_simulator'

        # Choose simulator. We defaulted in __init__() to AerSimulator()
        if self.use_qasm_simulator:
            simulator = 'qasm_simulator'
        elif self.use_unitary_simulator:
            simulator = 'unitary_simulator'
        elif self.use_statevector_simulator:
            simulator = 'statevector_simulator'
        elif self.use_pulse_simulator:
            simulator = 'pulse_simulator'
        elif self.use_aer_simulator_density_matrix:
            simulator = 'aer_simulator_density_matrix'
        
        # Choose method kwarg for gpu etc if present
        elif self.use_statevector_gpu:
            self.method = "statevector_gpu"
        elif self.use_unitary_gpu:
            self.method = "unitary_gpu"
        elif self.use_density_matrix_gpu:
            self.method = "density_matrix_gpu"
        return (simulator,self.method)
    


    
    
