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

import sys
from tkinter import Tk, Event, Menu, Text, N, W, E, S
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
            The QisJob instance this GUI represents

        Returns
        -------
        None.

        """
        self.qisjob = qisjob
        self.root = Tk()
        self.menu = Menu(self.root)
        self.menu_file = Menu(self.menu)
        self.menu.add_cascade(menu=self.menu_file, label="File")
        self.menu_file.add_command(label="Save")
        self.menu_file.add_command(label="Save As")
        self.menu_file.add_command(
            label="Exit", command=lambda: self.root.event_generate("<<ExitQisjob>>")
        )
        self.menu_run = Menu(self.menu)
        self.menu.add_cascade(menu=self.menu_run, label="Run")
        self.root["menu"] = self.menu
        self.frame = ttk.Frame(self.root)
        self.notebook = ttk.Notebook(self.frame)
        self.tab_providers = ttk.Frame(self.notebook)
        self.tab_jobs = ttk.Frame(self.notebook)
        self.tab_qj = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_providers, text="Providers")
        self.notebook.add(self.tab_jobs, text="Jobs")
        self.notebook.add(self.tab_qj, text="QisJob")
        self.text_qj = Text(self.tab_qj)
        self.text_qj.insert("end", str(self.qisjob))
        self.root.bind("<<ExitQisjob>>", self._exit)

    def run(self):
        """
        Run the application.

        Returns
        -------
        None.

        """
        self.root.columnconfigure(0, weight=1)
        self.frame.grid(sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.notebook.grid(sticky=(N, W, E, S))
        self.notebook.columnconfigure(0, weight=1)
        self.tab_providers.columnconfigure(0, weight=1)
        self.tab_jobs.columnconfigure(0, weight=1)
        self.tab_qj.columnconfigure(0, weight=1)
        self.text_qj.grid(sticky=(N, W, E, S))
        self.text_qj.columnconfigure(0, weight=1)
        self.root.mainloop()

    def _save(self, filename: str):
        """


        Parameters
        ----------
        filename : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        pass

    def _exit(self, e: Event):
        """


        Parameters
        ----------
        e : Event
            DESCRIPTION.

        Returns
        -------
        None.

        """
        print(f"Exiting on event {e}", file=sys.stderr)
        sys.exit()
