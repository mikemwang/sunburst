"""python file to create a sunburst diagram using most used words in English,
each layer represents the letter at that index in the word"""

from math import sin, cos, pi
from pyx import path, canvas, style, color, text
from colormap import COLOUR_MAPPING
import yaml


class Sunburst(object):
    """An object that describes the entire sunburst diagram, initializes global
    settings"""

    def __init__(self,
                 canvases,
                 config_path):

        self.shape_canvas = canvases[0]
        self.text_canvas = canvases[1]
        # data properties
        self.config_path = config_path  # path to config file
        self.config = None  # to be parsed later
        self.data_attrs = None
        self.layer_attrs = None
        # stores text locations, so we can do the text spread later
        self.text_info = {}

    def import_settings(self):
        """import settings in the config file and assign them"""

        # open the config file for parsing
        with open(self.config_path, 'r') as f:
            self.config = yaml.load(f)

        self.data_attrs = self.config['data_properties']
        self.layer_attrs = self.config['layer_properties']

    def sanitize_word_list(self):
        """clean up duplicate words (since the same word may be used as different
        parts of speech) and lowercase everything"""
        word_list = []
        with open(self.config['data_properties']['source']) as f:
            for string in f:
                line = string.split(',')
                word = line[0]
                # strip the newline char
                freq = int(line[1][:-2])
                word_list.append((word, freq))

        sanitized_list = []
        for entry in word_list:
            sanitized_entry = (entry[0].lower(), entry[1])
            present = False
            for item in sanitized_list:
                if sanitized_entry[0] == item[0]:
                    temp = item[1]
                    sanitized_list.remove(item)
                    sanitized_list.append((sanitized_entry[0],
                                           sanitized_entry[1] + temp))
                    present = True
                    break
            if not present:
                sanitized_list.append(sanitized_entry)
        return sanitized_list

    def bounding_box(self, data_max):
        """draw bounding box so the file is the right size and shape"""
        box_length = 1.15*data_max*self.layer_attrs['layer_width']
        self.shape_canvas.fill(path.rect(-box_length, -box_length,
                                         2*box_length, 2*box_length),
                               [color.rgb.white])

    def begin(self):
        """begin calculating the diagram"""
        # get the settings from the config file
        self.import_settings()
        # clean up the word list
        word_list = self.sanitize_word_list()
        # find how big the bounding box needs to be
        data_max = 0
        for word in word_list:
            if len(word[0]) > data_max:
                data_max = len(word[0])
        # draw the bounding box
        self.bounding_box(data_max)
        # instantiate the very first layer
        origin = Sector(self, word_list)
        # recursively draw all other layers
        origin.create_child_segments()


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
                 inner_radius=0,
                 parent_angle=0,
                 parent_arc=360):

        # assigned by constructor
        self.sunburst = sunburst
        self.parent_list = parent_list  # the list the parent sector passes on
        self.level = level  # keep track of which level of the graph, to stop recursion
        self.letter = letter  # what letter is it?
        self.start = start_percent  # start where on the parent sector
        self.end = end_percent  # end where on the parent sector
        # after truncating the parent sector letter
        self.inner_r = inner_radius

        # calculated using constructor
        self.start_angle = self.start*parent_arc + parent_angle
        self.end_angle = self.end*parent_arc + parent_angle

        # assigned from sunburst class
        self.max_level = self.sunburst.data_attrs['max_recursion']
        self.shape_canvas = self.sunburst.shape_canvas
        self.layer_width = self.sunburst.layer_attrs['layer_width']
        self.sector_width = self.sunburst.layer_attrs['sector_width']
        self.end_sector_width = self.sunburst.layer_attrs['end_cap_width']

    def display(self):
        """method to display the sector"""

        # draw the segment
        if self.level == 0:
            # don't draw anything in the center
            return

        if self.letter is '':
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.end_sector_width+self.inner_r,
                                          self.end_angle, self.start_angle),
                                path.closepath())
            self.shape_canvas.fill(segment, [color.rgb.red])
        else:
            # create the arc segment
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.sector_width+self.inner_r,
                                          self.end_angle, self.start_angle),
                                path.closepath())
            # render the arc segment onto the canvas
            self.shape_canvas.fill(segment,
                                   [color.gray(COLOUR_MAPPING[self.letter])])

            centroid_angle = 0.5*(self.end_angle+self.start_angle)

    def create_child_segment_lists(self):
        """a method to create child segments"""
        # TODO: not very elegent but it gets the job done

        child_sector_lists = {}

        while len(self.parent_list) > 0:

            for word_tuple in self.parent_list:
                if len(word_tuple[0]) == 0:
                    child_sector_lists[word_tuple[1]] = {'letter': '',
                                                         'words': []}
                    if len(self.parent_list) == 1:
                        return child_sector_lists
                    continue
                cur_word = word_tuple[0]
                # remove first letter since uneeded for further parsing
                # group words by first letter
                if len(cur_word) > 1:
                    child_list = [(word_tuple[0][1:], word_tuple[1])]
                else:
                    child_list = [('', word_tuple[1])]
                letter_freq = word_tuple[1]
                cur_letter = cur_word[0]
                for other_word_tuple in self.parent_list:
                    check_word = other_word_tuple[0]
                    if len(check_word) == 0:
                        continue
                    if check_word != cur_word:
                        if check_word[0] == cur_word[0]:
                            letter_freq += other_word_tuple[1]
                            if len(check_word) > 1:
                                child_list.append((check_word[1:],
                                                   other_word_tuple[1]))
                            else:
                                child_list.append(('', other_word_tuple[1]))

                child_sector_lists[letter_freq] = {'letter': cur_letter,
                                                   'words': child_list}

                # logic to remove all the words we've already found
                while True:
                    list_clear = True
                    for item in self.parent_list:
                        if len(item[0]) == 0:
                            continue
                        elif item[0][0] == cur_letter:
                            self.parent_list.remove(item)

                    # must do this to ensure all words beginning with cur_letter
                    # have been removed, since if consecutive words start with
                    # cur_letter the second one gets skipped in the above for loop
                    for item in self.parent_list:
                        if len(item[0]) == 0:
                            continue
                        if item[0][0] == cur_letter:
                            list_clear = False
                            break

                    if list_clear:
                        break

        return child_sector_lists

    def create_child_segments(self):
        """initialize the child sector objects"""

        # NOTE if this sector is an edofword, dont' create child segment

        if self.level > self.max_level:
            return

        self.display()
        child_lists = self.create_child_segment_lists()

        sorted_freq = sorted(list(child_lists.keys()), reverse=True)

        total_freq = sum(child_lists.keys())
        cur_percent = 0
        for freq in sorted_freq:
            percent = float(freq)/float(total_freq)
            child_sector = Sector(self.sunburst,
                                  child_lists[freq]['words'],
                                  self.level + 1,
                                  child_lists[freq]['letter'],
                                  cur_percent,
                                  cur_percent+percent,
                                  self.inner_r + self.layer_width,
                                  self.start_angle,
                                  self.end_angle - self.start_angle,
                                  )

            child_sector.create_child_segments()
            cur_percent += percent


if __name__ == "__main__":
    shape_canvas = canvas.canvas()
    text_canvas = canvas.canvas()
    canvases = (shape_canvas, text_canvas)
    # create bounding box
    sunburst = Sunburst(canvases, 'config.yaml')
    sunburst.begin()
    shape_canvas.insert(text_canvas)
    shape_canvas.writePDFfile('test1')
