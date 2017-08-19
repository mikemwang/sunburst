"""python file to create a sunburst diagram using most used words in English,
each layer represents the letter at that index in the word"""

from math import sin, cos, pi
from pyx import path, canvas, style, color, text, trafo
from colormap import COLOUR_MAPPING
import yaml
from code_parser import CodeParser

MAX = 25
NAME = 'test_self'+str(MAX)


class TextLayer(object):
    """class to create all the text and format it appropraitely"""

    def __init__(self, text_canvas, radial_offset, angular_spacing):
        """
        text_canvas: the canvas object to draw the text

        radial offset: the amount to radially move the text away

        angular spacing: minimum angular distance between letters, degrees?
        """
        self.text_canvas = text_canvas
        self.radial_offset = radial_offset
        self.angular_spacing = angular_spacing
        self.sector_info = {}  # info from the sector

    def begin(self):
        """draw the text!!"""
        text_info = self.apply_angular_offset()
        for layer in text_info:
            cent_rad = text_info[layer]['radius']
            for angle in text_info[layer]['letters']:
                cent_angle = angle*pi/180.0
                cent_x = cent_rad*cos(cent_angle)
                cent_y = cent_rad*sin(cent_angle)

                letter = text_info[layer]['letters'][angle][0]
                percent = text_info[layer]['letters'][angle][2]
                word_settings = trafo.rotate(cent_angle*180/pi)
                if cent_angle > pi/2 and cent_angle <(3*pi/2):
                    word_settings = trafo.rotate(180+cent_angle*180/pi)

                #if len(letter) > 1:
                #    disp = ' ['+str(percent)+']'
                #    letter += disp

                self.text_canvas.text(cent_x, cent_y, r' '+letter,
                        [text.halign.center, text.valign.middle,
                            word_settings])

    def update(self, layer, letter, centroid, percent):
        """sectors will call this to update the text info"""
        # centroid is a tuple of (angle, radius)
        if layer not in self.sector_info.keys():
            self.sector_info[layer] = {'radius': centroid[1],
                                       'letters':
                                       {centroid[0]: (letter, percent)}}
        else:
            self.sector_info[layer]['letters'][centroid[0]] = (letter, percent)

    def apply_angular_offset(self):
        """apply the angular offset
        {layer:
            letters:{
                a:(centroid_angle, text_angle)
                b:(centroid_angle, text_angle)
            },
            centroid_radius: some_number
        }
        """
        text_info = {}
        for layer in self.sector_info:
            ordered_angles = sorted(list(self.sector_info[layer]['letters'].keys()))
            ordered_new_angles = []
            text_info[layer] = {'radius': self.sector_info[layer]['radius'],
                                     'letters': {}}
            for index in range(len(ordered_angles)):
                letter = self.sector_info[layer]['letters'][ordered_angles[index]][0]
                percent = self.sector_info[layer]['letters'][ordered_angles[index]][1]
                cur_angle = ordered_angles[index]
                if index == 0:
                    text_info[layer]['letters'][cur_angle] = (letter,
                            cur_angle, percent)
                    ordered_new_angles.append(cur_angle)
                else:
                    target_angle = ordered_new_angles[index-1]+self.angular_spacing
                    if cur_angle < target_angle:
                        if target_angle - cur_angle < (pi/100.0):
                            text_info[layer]['letters'][cur_angle] = (letter,
                                                                   target_angle,
                                                                   percent)
                            ordered_new_angles.append(target_angle)
                        else:
                            ordered_new_angles.append(cur_angle)
                    else:
                        text_info[layer]['letters'][cur_angle] = (letter,
                                                               cur_angle,
                                                               percent)
                        ordered_new_angles.append(cur_angle)
        return text_info


class Sunburst(object):
    """An object that describes the entire sunburst diagram, initializes global
    settings"""

    def __init__(self,
                 canvases,
                 config_path,
                 text_object):

        self.shape_canvas = canvases[0]
        self.text_canvas = canvases[1]
        # data properties
        self.config_path = config_path  # path to config file
        self.text_object = text_object
        self.config = None  # to be parsed later
        self.data_attrs = None
        self.layer_attrs = None

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

            if len(sanitized_list) > MAX:
                break
        return sanitized_list

    def bounding_box(self, data_max):
        """draw bounding box so the file is the right size and shape"""
        box_length = (data_max+2)*self.layer_attrs['layer_width']
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
        code_parse = CodeParser('sunburst.py')
        word_list = code_parse.parse()
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
                 inner_radius=0,
                 parent_angle=0,
                 parent_arc=360,
                 parent_centroid_angle=0,
                 parent_outer_radius=0,
                 parent_color=None,
                 path=''):

        # assigned by constructor
        self.sunburst = sunburst
        self.parent_list = parent_list  # the list the parent sector passes on
        self.level = level  # to stop recursion
        self.letter = letter  # what letter is it?
        self.start = start_percent  # start where on the parent sector
        self.end = end_percent  # end where on the parent sector
        # after truncating the parent sector letter
        self.inner_r = inner_radius
        self.parent_centroid_angle = parent_centroid_angle
        self.parent_outer_radius = parent_outer_radius

        # calculated using constructor
        self.start_angle = self.start*parent_arc + parent_angle
        self.end_angle = self.end*parent_arc + parent_angle

        # assigned from sunburst class
        self.max_level = self.sunburst.data_attrs['max_recursion']
        self.shape_canvas = self.sunburst.shape_canvas
        self.layer_width = self.sunburst.layer_attrs['layer_width']
        self.sector_width = self.sunburst.layer_attrs['sector_width']
        self.end_sector_width = self.sunburst.layer_attrs['end_cap_width']

        self.centroid_angle = 0.5*(self.end_angle+self.start_angle)*pi/180.0
        self.parent_color = parent_color

        self.sector_color = None
        self.path = path

        if self.level == 0:
            return
        if self.letter == '':
            self.sector_color = color.rgb.red
        else:
            self.sector_color = color.gray(COLOUR_MAPPING[self.letter])

    def draw_sector(self, end):
        """draw the sector"""

        if end:
            # to account for rounding errors, make the sectors slightly larger
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.end_sector_width+self.inner_r,
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

        percent = int(10000*(self.end_angle-self.start_angle)/360.0)/100.0

        if self.letter == '':
            self.sunburst.text_object.update(self.level, self.path[6:],
                                             (self.centroid_angle*180.0/pi,
                                              self.inner_r+0.5*self.sector_width),
                                             percent)
        else:
            self.sunburst.text_object.update(self.level, self.letter,
                                             (self.centroid_angle*180.0/pi,
                                              self.inner_r+0.5*self.sector_width),
                                             percent)

        if len(self.parent_list) == 1:
            remaining_letters = self.parent_list[0][0]
            if remaining_letters == '':
                pass
            else:
                for letter in remaining_letters:
                    pass

        bezier_color = None
        if self.level == 1:
            bezier_color = self.sector_color
        else:
            bezier_color = self.parent_color

        if self.letter == '':
            self.draw_sector(True)
        else:
            self.draw_sector(False)

        # draw the bezier
        x0 = self.inner_r*cos(self.centroid_angle)
        y0 = self.inner_r*sin(self.centroid_angle)
        r1 =  0.5*(self.parent_outer_radius+self.inner_r)
        x1 = r1*cos(self.centroid_angle)
        y1 = r1*sin(self.centroid_angle)
        x2 = r1*cos(self.parent_centroid_angle)
        y2 = r1*sin(self.parent_centroid_angle)
        x3 = self.parent_outer_radius*cos(self.parent_centroid_angle)
        y3 = self.parent_outer_radius*sin(self.parent_centroid_angle)

        bezier_color = self.sector_color

        self.shape_canvas.stroke(path.curve(x0,y0,x1,y1,x2,y2,x3,y3),
                                 [style.linewidth(0.005), bezier_color])

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
                                  self.centroid_angle,
                                  self.inner_r+self.sector_width,
                                  self.sector_color,
                                  self.path + self.letter
                                  )

            child_sector.create_child_segments()
            cur_percent += percent


if __name__ == "__main__":
    shape_canvas = canvas.canvas()
    text_canvas = canvas.canvas()
    canvases = (shape_canvas, text_canvas)
    text_object = TextLayer(text_canvas, 0.75, 0.25)
    # create bounding box
    sunburst = Sunburst(canvases, 'config.yaml', text_object)
    sunburst.begin()
    shape_canvas.insert(text_canvas)
    shape_canvas.writePDFfile(NAME)
