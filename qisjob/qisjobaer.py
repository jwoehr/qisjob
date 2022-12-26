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


class QisJobAer:
    """
    Class to manage the Qiskit AerSimulator for QisJob
    """

    def __init__(self, **kwargs):
        self.configuration = None
        self.properties = None
        self.provider = None
        self.method = None
        self.backend = None
        self.from_backend_named = None
        self.process_kwargs(**kwargs)
        self.aer_simulator = AerSimulator()

    def process_kwargs(self, kwargs):
        if "noise_model" in kwargs and "noise_model_backend" in kwargs:
            raise QisJobArgumentException(
                "noise_model and noise_model_backend are mutually exclusive"
            )
        if "method" in kwargs:
            self.method = kwargs["method"]
