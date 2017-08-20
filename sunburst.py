"""python file to create a sunburst diagram using most used words in English,
each layer represents the letter at that index in the word"""

from math import sin, cos, pi
from pyx import path, canvas, style, color, text, trafo
from colormap import COLOR_MAPPING, BEZIER_MAPPING
import yaml
from code_parser import CodeParser

class TextLayer(object):
    """class to create all the text and format it appropraitely"""

    def __init__(self, canvas):
        """
        text_canvas: the canvas object to draw the text

        radial offset: the amount to radially move the text away

        angular spacing: minimum angular distance between letters, degrees?
        """
        self.canvas = canvas
        self.sectors = {}  # info from the sector

    def begin(self):
        """draw the text!!"""

        for layer in self.sectors:
            radius = self.sectors[layer]['radius']

            for angle in self.sectors[layer]['letters']:
                cent_angle = angle*pi/180.0
                centroid_x = radius*cos(cent_angle)
                centroid_y = radius*sin(cent_angle)
                letter = self.sectors[layer]['letters'][angle]
                transform = trafo.rotate(cent_angle*180/pi)

                if cent_angle > pi/2 and cent_angle <(3*pi/2):
                    transform = trafo.rotate(180+cent_angle*180/pi)

                self.canvas.text(centroid_x, centroid_y, r' '+letter,
                        [text.halign.center, text.valign.middle,
                            transform])

    def update(self, layer, letter, centroid):
        """sectors will call this to update the text info"""
        # centroid is a tuple of (angle, radius)
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
                 canvases,
                 config,
                 text_object):

        self.shape_canvas = canvases[0]
        self.text_canvas = canvases[1]
        # data properties
        self.config = config  # path to config file
        self.text_object = text_object
        self.settings = None  # to be parsed later
        self.data = None  # from the settings file
        self.layer = None  # from the settings file

    def import_settings(self):
        """import settings in the config file and assign them"""

        # open the config file for parsing
        self.settings = yaml.load(open(self.config, 'r'))
        self.data = self.settings['data']
        self.layer = self.settings['layer']

    def extents(self, layers):
        """draw bounding box so the file is the right size and shape"""
        # +2 for some boarder padding
        box_length = (layers+1.25)*self.layer['layer_width']
        self.shape_canvas.fill(path.rect(-box_length, -box_length,
                                         2*box_length, 2*box_length),
                               [color.rgb.white])

    def begin(self):
        """begin calculating the diagram"""
        # get the settings from the config file
        self.import_settings()
        words = None
        code_parse = CodeParser('sunburst.py')
        words = code_parse.parse()
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
        self.text_object.begin()


class Sector(object):
    """A slice of the sunburst graph, should have a parent sector and children
    sectors"""

    # these defaults create the root sector
    def __init__(self,
                 sunburst,
                 parent_list,
                 level=0,
                 letter='ORIGIN',
                 start_percent=0,
                 end_percent=1,
                 inner_r=0,
                 parent_angle=0,
                 parent_arc=360,
                 parent_centroid_angle=0,
                 parent_outer_radius=0,
                 path=''):

        # assigned by constructor
        self.sunburst = sunburst
        self.parent_list = parent_list  # the list the parent sector passes on
        self.level = level  # to stop recursion
        self.letter = letter  # what letter is it?
        self.start = start_percent  # start where on the parent sector
        self.end = end_percent  # end where on the parent sector
        # after truncating the parent sector letter
        self.inner_r = inner_r
        self.parent_centroid_angle = parent_centroid_angle
        self.parent_outer_radius = parent_outer_radius

        # calculated using constructor
        self.start_angle = self.start*parent_arc + parent_angle
        self.end_angle = self.end*parent_arc + parent_angle

        # assigned from sunburst class
        self.max_level = self.sunburst.data['max_recursion']
        self.shape_canvas = self.sunburst.shape_canvas
        self.layer_width = self.sunburst.layer['layer_width']
        self.sector_width = self.sunburst.layer['sector_width']

        self.centroid_angle = 0.5*(self.end_angle+self.start_angle)*pi/180.0
        self.path = path

        if self.level > 0:
            self.sector_color = COLOR_MAPPING[self.letter]

    def draw_sector(self, end):
        """draw the sector"""

        if end:
            # to account for rounding errors, make the sectors slightly larger
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.sector_width+self.inner_r,
                                          self.end_angle, self.start_angle),
                                path.closepath())
            self.shape_canvas.fill(segment, [self.sector_color])
        else:
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.sector_width+self.inner_r,
                                          self.end_angle, self.start_angle),
                                path.closepath())
            self.shape_canvas.fill(segment, [self.sector_color])

        # draw a delimiting line between sectors
        bx0 = self.inner_r*cos(self.start_angle*pi/180.0)
        by0 = self.inner_r*sin(self.start_angle*pi/180.0)
        r = self.inner_r + self.sector_width
        bx1 = r*cos(self.start_angle*pi/180.0)
        by1 = r*sin(self.start_angle*pi/180.0)

        self.shape_canvas.stroke(path.line(bx0, by0, bx1, by1),
                [style.linewidth(0.01), color.rgb.black])

        cx0 = self.inner_r*cos(self.end_angle*pi/180.0)
        cy0 = self.inner_r*sin(self.end_angle*pi/180.0)
        cx1 = r*cos(self.end_angle*pi/180.0)
        cy1 = r*sin(self.end_angle*pi/180.0)

        self.shape_canvas.stroke(path.line(cx0, cy0, cx1, cy1),
                [style.linewidth(0.01), color.rgb.black])

    def display(self):
        """method to display the sector"""

        # draw the segment
        if self.level == 0:
            # don't draw anything in the center
            return

        if self.letter == '':
            self.sunburst.text_object.update(self.level, self.path[6:],
                                             (self.centroid_angle*180.0/pi,
                                              self.inner_r+0.5*self.sector_width))
        else:
            self.sunburst.text_object.update(self.level, self.letter,
                                             (self.centroid_angle*180.0/pi,
                                              self.inner_r+0.5*self.sector_width))

        if self.letter == '':
            self.draw_sector(True)
        else:
            self.draw_sector(False)

        # draw the bezier
        x0 = self.inner_r*cos(self.centroid_angle)
        y0 = self.inner_r*sin(self.centroid_angle)

        r1 = self.parent_outer_radius
        x1 = r1*cos(self.centroid_angle)
        y1 = r1*sin(self.centroid_angle)

        r2 = self.inner_r
        x2 = r2*cos(self.parent_centroid_angle)
        y2 = r2*sin(self.parent_centroid_angle)

        x3 = self.parent_outer_radius*cos(self.parent_centroid_angle)
        y3 = self.parent_outer_radius*sin(self.parent_centroid_angle)

        bezier_color = BEZIER_MAPPING[self.letter]

        self.shape_canvas.stroke(path.curve(x0,y0,x1,y1,x2,y2,x3,y3),
                                 [style.linewidth(0.005), bezier_color])

    def create_child_segment_lists(self):
        """a method to create child segment lists. returns in the following
        format:

        {letter_frequency:
            {'letter': x,
             'words' : [list of remaining word segments]},
         letter_frequency:
            {'letter': x,
             'words' : [list of remaining word segments]},
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
        if self.level == 0:
            for entry in child_sector_lists:
                print(entry)

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
                                  self.centroid_angle,
                                  self.inner_r+self.sector_width,
                                  self.path + self.letter
                                  )

            child_sector.create_child_segments()
            cur_percent += percent


if __name__ == "__main__":
    shape_canvas = canvas.canvas()
    text_canvas = canvas.canvas()
    canvases = (shape_canvas, text_canvas)
    text_object = TextLayer(text_canvas)
    # create bounding box
    sunburst = Sunburst(canvases, 'config.yaml', text_object)
    sunburst.begin()
    shape_canvas.insert(text_canvas)
    shape_canvas.writePDFfile('test_meta_170819')
