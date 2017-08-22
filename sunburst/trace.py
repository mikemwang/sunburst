"""create a tracing function to save lines as they run

example code from:
http://www.dalkescientific.com/writings/diary/archive/2005/04/20/tracing_python_code.html

"""

import sys
import os
import linecache


class Trace(object):
    def __init__(self, sunburst_dir, start_function, end_function):
        self.lines = []
        self.sunburst_dir = sunburst_dir
        # the function at which to start tracing lines
        self.start_function = start_function.__name__
        # the function at which to stop tracing lines
        self.end_function = end_function.__name__
        # are we tracing?
        self.in_trace = False
        # have we finished tracing? only need to trace one runthrough
        self.traced = False

    def line_trace(self, frame, event, arg):
        """a callback to trace lines as they run and save them to a list"""
        if event == "line":
            filename = frame.f_globals["__file__"]
            filedir = os.path.dirname(os.path.abspath(filename))
            # don't trace lines for standard imports and pyx
            if filedir == self.sunburst_dir:
                lineno = frame.f_lineno
                line = linecache.getline(filename, lineno)
                self.lines.append(line)
                print(line)

    def trace(self, frame, event, arg):
        """a callback to trigger line tracing for the appropriate functions"""
        if not self.traced:
            if event == 'call':
                code = frame.f_code
                function = code.co_name
                # start tracing lines if we've reached the start function
                if function == self.start_function:
                    self.in_trace = True
                # stop tracing lines once we've finished
                elif function == self.end_function:
                    self.in_trace = False
                    self.traced = True
                # while tracing, keep calling line_trace
                if self.in_trace:
                    return self.line_trace
        return self.trace

