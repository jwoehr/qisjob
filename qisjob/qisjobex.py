#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qisjobex.py
QisJob exceptions

Created on Sat Dec 24 17:03:55 2022

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


class QisJobException(Exception):
    """Base class for QisJob exceptions"""

    def __init__(self, message: str, retval: int):
        """


        Parameters
        ----------
        message : str
            programmer-supplied message
        retval : int
            suggested return val for an encapsulating function or script

        Returns
        -------
        None.

        """
        super().__init__()
        self.message = message
        self.retval = retval


class QisJobArgumentException(QisJobException):
    """
    Invalid Argument passed to one of QisJob's classes or function.
    """

    def __init__(self, message: str):
        """


        Parameters
        ----------
        message : str
            programmer-supplied message

        Returns
        -------
        None.

        """
        super().__init__(message, 1)


class QisJobRuntimeException(QisJobException):
    """
    QisJob encountered an unrecoverable runtime error.
    """

    def __init__(self, message: str):
        """


        Parameters
        ----------
        message : str
            programmer-supplied message

        Returns
        -------
        None.

        """
        super().__init__(message, 100)
