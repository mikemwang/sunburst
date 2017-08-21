#!/usr/bin/env python
# -*- coding: utf-8 -*-
import trace
import sys
import os

from pyx import canvas
import yaml
from sunburst.sunburst import Sunburst

def main():
    shape_canvas = canvas.canvas()
    text_canvas = canvas.canvas()
    settings = yaml.load(open('config.yaml', 'r'))
    sunburst = Sunburst(shape_canvas, text_canvas, settings)
    sunburst.draw()
    shape_canvas.insert(text_canvas)
    shape_canvas.writePDFfile(settings['output']['name'])  #'

tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=1,
    count=0)
tracer.run(main.__code__)
r = tracer.results()
r.write_results(show_missing=True,
                coverdir=os.path.dirname(os.path.abspath(__file__)+'/code_metadata'))
