#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

from pyx import canvas
import yaml
import sunburst


def main():
    # set up the line tracing function
    tracer = sunburst.Trace(os.path.dirname(os.path.abspath(sunburst.__file__)),
                            sunburst.generate_diagrams, sunburst.stop_trace)
    #sys.settrace(tracer.trace)
    # where is the sunburst directory?
    path = os.path.dirname(os.path.abspath(sunburst.__file__))
    # instantiate canvases
    shape_canvas = canvas.canvas()
    text_canvas = canvas.canvas()
    # read in settings
    settings = yaml.load(open('config.yaml', 'r'))
    # list of diagrams to create
    data = [('test', (0, 0)), ('test2', (180, 0))]
    sunburst.generate_diagrams(data, shape_canvas, text_canvas, settings,
                               path)
    sunburst.output(settings['output']['name'], shape_canvas, text_canvas)
    print(tracer.traced)


if __name__ == '__main__':
    main()
