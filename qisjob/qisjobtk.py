#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 19:51:37 2022

@author: jwoehr
"""

import tkinter
from tkinter import ttk
from qisjob import QisJob

class QisJobTk:
    def __init__(self, qisjob: QisJob ):
        self.qisjob = qisjob
        self.root = tkinter.Tk()
        self.frame = ttk.Frame(self.root)
        self.notebook = ttk.Notebook(self.frame)
        self.tab_printself = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_printself, text="Self")
        self.text_printself = tkinter.Text(self.tab_printself)
        self.text_printself.insert('end', str(self.qisjob))
    def run(self):
        self.root.grid()
        self.frame.grid()
        self.notebook.grid()
        self.tab_printself.grid()
        self.text_printself.grid()
        self.root.mainloop()
    