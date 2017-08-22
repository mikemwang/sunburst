"""python file to create a sunburst diagram using most used words in English,
each layer represents the letter at that index in the word"""

from math import sin, cos, pi
from pyx import path, style, color, text, trafo
from .colormap import color_map
from .code_parser import CodeParser


text.set(text.LatexRunner)  #'
text.preamble(r"\usepackage{courier}")  #'


def generate_diagrams(data, shape_canvas, text_canvas, settings, path):
    diagrams = {}
    for entry in data:
        name = entry[0]
        origin = entry[1]
        data_source = entry[2]
        print(origin)
        diagrams[name] = Sunburst(shape_canvas,
                                  text_canvas,
                                  settings,
                                  path,
                                  name,
                                  origin,
                                  data_source)
        diagrams[name].draw()
        stop_trace()
    return diagrams


def stop_trace():
    """a function that, when called, tells trace to stop tracing"""
    pass


def output(file_name, shape_canvas, text_canvas):
    shape_canvas.insert(text_canvas)
    shape_canvas.writePDFfile(file_name)  #'


class TextLayer(object):
    """class to create all the text and format it appropriately"""

    def __init__(self, canvas, origin, alphabet, numbers):
        self.canvas = canvas
        self.sectors = {}  # info from the sector
        self.color_map = color_map(alphabet, numbers)
        self.xo = origin[0]
        self.yo = origin[1]
        # set the font

    def draw(self):
        """draw the text!!"""

        for layer in self.sectors:
            radius = self.sectors[layer]['radius']
            original_radius = radius

            prev_radian = 0
            for radian in self.sectors[layer]['letters']:
                # check if the sector is too small
                if (radian-prev_radian)*original_radius < 0.2:
                    radius += .2
                else:
                    radius = original_radius
                centroid_x = radius*cos(radian)+self.xo
                centroid_y = radius*sin(radian)+self.yo
                letter = self.sectors[layer]['letters'][radian]
                # rotate the text accordingly
                transform = trafo.rotate(radian*180/pi)

                if radian > pi/2 and radian < (3*pi/2):
                    transform = trafo.rotate(180+radian*180/pi)

                self.canvas.text(centroid_x, centroid_y,
                                 r"\texttt{"+letter+'}',
                                 [text.halign.center, text.valign.middle,
                                  transform])
                prev_radian = radian

    def update(self, layer, letter, centroid):
        """sectors will call this to update the text info

        layer: the layer number of the sector
        letter: the letter of the sector
        centroid: a tule of (radians, radius)

        """
        if layer not in self.sectors.keys():
            self.sectors[layer] = {'radius': centroid[1],
                                   'letters':
                                       {centroid[0]: letter}}
        else:
            self.sectors[layer]['letters'][centroid[0]] = letter


class Sunburst(object):
    """An object that describes the entire sunburst diagram, initializes global
    settings"""

    def __init__(self,
                 shape_canvas,
                 text_canvas,
                 settings,
                 source,
                 name,
                 origin,
                 data_source):

        self.shape_canvas = shape_canvas
        self.text_canvas = text_canvas
        # data properties
        self.text_object = None
        self.alphabet = None
        self.numbers = None
        self.color_map = None
        self.settings = settings  # to be parsed later
        self.data = None  # from the settings file
        self.layer = None  # from the settings file
        self.source = source

        self.name = name
        self.origin = origin
        self.origin_x = origin[0]
        self.origin_y = origin[1]

        self.data_source = data_source

    def import_settings(self):
        """import settings in the config file and assign them"""

        # open the config file for parsing
        self.data = self.settings['data']
        self.layer = self.settings['layer']
        self.alphabet = self.data['alphabet']
        self.numbers = self.data['numbers']
        self.text_object = TextLayer(self.text_canvas, self.origin, self.alphabet,
                                     self.numbers)
        self.color_map = color_map(self.alphabet, self.numbers)

    def extents(self, layers):
        """draw bounding box so the file is the right size and shape"""
        # +2 for some boarder padding
        box_length = (layers+2)*self.layer['layer_width']
        self.shape_canvas.stroke(path.rect(self.origin_x-box_length,
                                           self.origin_y-box_length,
                                           2*box_length, 2*box_length),
                               [color.rgb.white])

    def draw(self):
        """begin calculating the diagram"""
        # get the settings from the config file
        self.import_settings()
        words = None
        code_parse = CodeParser(self.source, self.alphabet, self.numbers)
        if self.data_source[0] == 'raw':
            words = code_parse.parse()
        elif self.data_source[0] == 'trace':
            print(self.data_source[1])
            words = code_parse.parse_trace(self.data_source[1])
        # find how big the bounding box needs to be
        max_len = 0
        for word in words:
            if len(word) > max_len:
                max_len = len(word)

        # draw the bounding box
        self.extents(max_len)
        # instantiate the very first layer
        origin = Sector(self, words)
        # recursively draw all other layers
        origin.create_child_segments()
        self.text_object.draw()


class Sector(object):
    """A slice of the sunburst graph, should have a parent sector and children
    sectors"""

    # these defaults create the root sector
    def __init__(self,
                 sunburst,
                 parent_list,
                 level=0,
                 letter='ORIGIN',
                 start_percent=0,  # decimal 0-1
                 end_percent=1,  # decimal 0-1
                 inner_r=0,
                 parent_angle=0,  # degrees
                 parent_arc=360,  # degrees
                 parent_centroid_radian=0,  # radians
                 parent_outer_radius=0,
                 parent_color=color.rgb.white,
                 path=''):

        # assigned by constructor
        self.sunburst = sunburst
        self.parent_list = parent_list  # the list the parent sector passes on
        self.level = level  # to stop recursion
        self.letter = letter  # what letter is it?
        # after truncating the parent sector letter
        self.inner_r = inner_r
        self.parent_centroid_radian = parent_centroid_radian  # rad
        self.parent_outer_radius = parent_outer_radius
        self.parent_color = parent_color

        # calculated using constructor
        self.start_angle = start_percent*parent_arc + parent_angle  # deg
        self.end_angle = end_percent*parent_arc + parent_angle  # deg

        # assigned from sunburst class
        self.max_level = self.sunburst.data['max_recursion']
        self.shape_canvas = self.sunburst.shape_canvas
        self.layer_width = self.sunburst.layer['layer_width']
        self.sector_width = self.sunburst.layer['sector_width']

        self.centroid_radians = 0.5*(self.end_angle+self.start_angle)*pi/180.0

        self.path = path

        self.xo = self.sunburst.origin_x
        self.yo = self.sunburst.origin_y

        if self.level > 0:
            self.sector_color = self.sunburst.color_map[self.letter]
        else:
            self.sector_color = color.rgb.white

    def draw_sector(self, end):
        """draw the sector"""
        print(self.xo,self.yo)
        segment = path.path(path.arc(self.xo, self.yo,
                                     self.inner_r,
                                     self.start_angle, self.end_angle),
                            path.arcn(self.xo, self.yo,
                                      self.sector_width+self.inner_r,
                                      self.end_angle, self.start_angle),
                            path.closepath())
        self.shape_canvas.fill(segment, [self.sector_color])

        # draw a delimiting line between sectors
        r = self.inner_r + self.sector_width
        start_radians = self.start_angle*pi/180.0
        end_radians = self.end_angle*pi/180.0
        x0 = self.inner_r*cos(start_radians)+self.xo
        y0 = self.inner_r*sin(start_radians)+self.yo
        x1 = r*cos(start_radians)+self.xo
        y1 = r*sin(start_radians)+self.yo

        self.shape_canvas.stroke(path.line(x0, y0, x1, y1),
                [style.linewidth(0.01), color.gray(0.15)])

        x0 = self.inner_r*cos(end_radians)+self.xo
        y0 = self.inner_r*sin(end_radians)+self.yo
        x1 = r*cos(end_radians)+self.xo
        y1 = r*sin(end_radians)+self.yo

        self.shape_canvas.stroke(path.line(x0, y0, x1, y1),
                [style.linewidth(0.01), color.gray(0.15)])

    def display(self):
        """method to display the sector"""

        # draw the segment
        if self.level == 0:
            # don't draw anything in the center
            return

        if self.letter == '':
            self.sunburst.text_object.update(self.level, self.path[6:],
                                             (self.centroid_radians,
                                              self.inner_r +
                                              0.5*self.sector_width))
        else:
            self.sunburst.text_object.update(self.level, self.letter,
                                             (self.centroid_radians,
                                              self.inner_r +
                                              0.5*self.sector_width))

        if self.letter == '':
            self.draw_sector(True)
        else:
            self.draw_sector(False)

        # draw the bezier
        x0 = (self.inner_r+0.05)*cos(self.centroid_radians)+self.xo
        y0 = (self.inner_r+0.05)*sin(self.centroid_radians)+self.yo

        r = self.parent_outer_radius
        x1 = r*cos(self.centroid_radians)+self.xo
        y1 = r*sin(self.centroid_radians)+self.yo

        r = self.inner_r
        x2 = r*cos(self.parent_centroid_radian)+self.xo
        y2 = r*sin(self.parent_centroid_radian)+self.yo

        x3 = self.parent_outer_radius*cos(self.parent_centroid_radian)+self.xo
        y3 = self.parent_outer_radius*sin(self.parent_centroid_radian)+self.yo

        self.shape_canvas.stroke(path.curve(x0, y0, x1, y1, x2, y2, x3, y3),
                                 [style.linewidth(0.035), self.sector_color])

    def create_child_segment_lists(self):
        """a method to create child segment lists. returns in the following
        format:

        [{'letter': a, 'freq': 1234, 'words': [{word: freq}, {word, freq}]}...]

        }


        """
        child_sector_lists = {}
        sorted_child_lists = []

        for word in self.parent_list:
            # if the first letter of the word - word[0][0] is not already a key
            # in the dict, start a new key
            freq = self.parent_list[word]
            if not word:
                # if word is an empty string, continue
                child_sector_lists[word] = {'freq': freq,
                                            'words': {}}
                continue
            letter = word[0]
            if letter not in child_sector_lists.keys():
                # word[1] is the frequency, word[0][1:] removes the first
                # letter
                if len(word) == 1:
                    # if removing the first character yields an empty string:
                    child_sector_lists[letter] = {'freq': freq,
                                                  'words': {'': freq}}
                    continue

                child_sector_lists[letter] = {'freq': freq,
                                              'words': {word[1:]: freq}}
            else:
                # increment frequency accordingly
                child_sector_lists[letter]['freq'] += freq
                # if removing the first character yields an empty string:
                if len(word) == 1:
                    # add tuple to that list of words, removing first letter
                    child_sector_lists[letter]['words'][''] = freq
                    continue
                child_sector_lists[letter]['words'][word[1:]] = freq

        # commence sorting by frequncy
        # we do this since having the frequency as the key in the above
        # dict will lead to lost data if 2 letters have the same freq

        # first populate a list of all letter frequencies
        freqlist = []

        for letter in child_sector_lists:
            freqlist.append(child_sector_lists[letter]['freq'])
        # then sort this list in descending order
        freqlist.sort(reverse=True)

        # now add the dicts into sorted_child_lists in the right order
        for freq in freqlist:
            for letter in child_sector_lists:
                if child_sector_lists[letter]['freq'] == freq:
                    sorted_child_lists.append({'letter': letter,
                                               'freq': freq,
                                               'words': child_sector_lists[
                                                   letter]['words']})
                    child_sector_lists.pop(letter)
                    break
        return sorted_child_lists
        # this will look like:
        # [{'letter': a, 'freq': 1234, 'words': {'ble': 123, 'ss': 432}}, ...]

    def create_child_segments(self):
        """initialize the child sector objects"""

        # NOTE if this sector is an edofword, dont' create child segment

        if self.level > self.max_level:
            return

        self.display()
        if self.letter == '':
            return

        child_lists = self.create_child_segment_lists()

        total_freq = 0
        for child in child_lists:
            total_freq += child['freq']

        cur_percent = 0
        for child in child_lists:
            percent = float(child['freq'])/float(total_freq)
            child_sector = Sector(self.sunburst,
                                  child['words'],
                                  self.level + 1,
                                  child['letter'],
                                  cur_percent,
                                  cur_percent+percent,
                                  self.inner_r + self.layer_width,
                                  self.start_angle,
                                  self.end_angle - self.start_angle,
                                  self.centroid_radians,
                                  self.inner_r+self.sector_width,
                                  self.sector_color,
                                  self.path + self.letter
                                  )

            child_sector.create_child_segments()
            cur_percent += percent
