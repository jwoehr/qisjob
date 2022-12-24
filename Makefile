# Makefile for QisJob
#
# This code is part of qisjob.
#
# (C) Copyright Jack J. Woehr 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

DOCDIR = $(shell pwd)/share/doc
PYSRCS = qisjob/qisjob.py scripts/qisjob

.PHONY:	install uninstall clean uninstall_oldname doc testsrc test

install:
	pip install .

uninstall:
	pip uninstall qisjob

clean:
	rm -rf build dist qisjob.egg-info qisjob/__pycache__ share/doc/qisjob

uninstall_oldname:
	pip3 uninstall qis_job

doc:
	echo "DOCDIR is $(DOCDIR)"
	cd /tmp && pdoc3 --skip-errors --html -f -o $(DOCDIR) qisjob

testsrc:
	- pylint $(PYSRCS)
	- pycodestyle --max-line-length=200 $(PYSRCS)

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
