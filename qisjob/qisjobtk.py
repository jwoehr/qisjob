#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 19:51:37 2022

@author: jwoehr
"""

from tkinter import *
from tkinter import ttk
from qisjob import QisJob


class QisJobTk:
    """ """

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
        self.frame = ttk.Frame(self.root)
        self.notebook = ttk.Notebook(self.frame)
        self.tab_printself = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_printself, text="Self")
        self.text_printself = Text(self.tab_printself)
        self.text_printself.insert("end", str(self.qisjob))

    def run(self):
        """


        Returns
        -------
        None.

        """
        self.root.grid()
        self.frame.grid(sticky=(N, W, E, S))
        self.notebook.grid(sticky=(N, W, E, S))
        self.tab_printself.grid(sticky=(N, W, E, S))
        self.text_printself.grid(sticky=(N, W, E, S))
        self.root.mainloop()
