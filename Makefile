# Makefile for QisJob
#
# This code is part of qis_job.
#
# (C) Copyright Jack J. Woehr 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

.PHONY:	install uninstall test

install:
	rm -rf build dist qis_job.egg-info
	python3 ./setup.py install

uninstall:
	pip3 uninstall qis_job

test:
ifeq ($(NUQASM2_INCLUDE_PATH),)
	@echo "To make test you need environment var NUQASM2_INCLUDE_PATH"
	@echo "(The test suite qasm source directory is automatically appended.)"
	@echo "Example: NUQASM2_INCLUDE_PATH=/include/path_a:include/path_b make test"
	@echo "Since this variable is not set, we did not make 'test'."
else
	@echo "making 'test'"
	@echo "Current include path setting:"
	@echo "NUQASM2_INCLUDE_PATH=${NUQASM2_INCLUDE_PATH}"
#	python3 -m unittest discover -s test -v
endif