#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 19:51:37 2022
Tk interface for QisJob
The main repository is https://github.com/jwoehr/qisjob

Copyright 2022 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81023-0082
Apache License, Version 2.0 -- See LICENSE which you should have received with this code.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: jwoehr
"""

from tkinter import Tk, Text, N, W, E, S
from tkinter import ttk
from qisjob import QisJob


class QisJobTk:
    """
    Provide an interactive GUI interface to QisJob via Tkinter
    """

    def __init__(self, qisjob: QisJob):
        """


        Parameters
        ----------
        qisjob : QisJob
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.qisjob = qisjob
        self.root = Tk()
        self.notebook = ttk.Notebook(self.root)
        self.tab_configure = ttk.Frame(self.notebook)
        self.tab_printself = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_configure, text="Configure")
        self.notebook.add(self.tab_printself, text="Self")
        self.text_configure = Text(self.tab_configure)
        self.text_configure.insert("end", "Configure")
        self.text_printself = Text(self.tab_printself)
        self.text_printself.insert("end", str(self.qisjob))

    def run(self):
        """
        Run the application.

        Returns
        -------
        None.

        """
        self.notebook.grid(sticky=(N, W, E, S))
        self.text_printself.grid()
        self.text_configure.grid()
        self.root.mainloop()
