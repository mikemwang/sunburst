"""python file to create a sunburst diagram using most used words in English,
each layer represents the letter at that index in the word"""

from pyx import path, canvas, style, color, text
from wordlist import word_list
from colormap import COLOUR_MAPPING
from math import sin, cos, pi
from auxilary_classes import Canvases, Geometric_Properties

# TODO make a class Sector_Constants that has the unchanging variables, then
# make Sector inherit from Sector_Constants so there's no need to pass along
# variables that never change

class Sunburst(object):
    """An object that describes the entire sunburst diagram, initializes global
    settings"""

    def __init__(self,
                 data_source,
                 max_recursion,
                 shape_canvas,
                 text_canvas,
                 layer_thickness,
                 letter_sector_thickness,
                 end_sector_thickness):

        self.data_source = data_source
        self.max_recursion = max_recursion

class Layer(object):
    """An object to store layer properties (since each sector is only aware of
    its vertical slice"""
    pass

class Sector(object):
    """A slice of the sunburst graph, should have a parent sector and children
    sectors"""

    def __init__(self,
                 parent_list=None,
                 level=None,
                 max_level=None,
                 letter=None,
                 shape_canvas=None,
                 start_percent=0,
                 end_percent=None,
                 inner_radius=None,
                 layer_thickness=None,
                 arc_thickness=None,
                 parent_angle=None,
                 parent_arc=None,
                 text_pos=None):

        self.parent_list = parent_list  # the list the parent sector passes on
        self.level = level  # which level of the graph, to stop recursion
        self.max_level = max_level
        self.letter = letter  # what letter is it?
        self.shape_canvas = shape_canvas
        self.text_canvas = text_canvas
        self.start = start_percent  # start where on the parent sector
        self.end = end_percent  # end where on the parent sector
        # after truncating the parent sector letter
        self.inner_r = inner_radius
        self.layer_thickness = layer_thickness
        self.arc_thickness = arc_thickness
        self.start_angle = self.start*parent_arc + parent_angle
        self.end_angle = self.end*parent_arc + parent_angle
        self.text_pos = text_pos

    def dist_from_centroid(self, d_from_centroid):
        """
        a method to calculate points along the ceterline

        args:
             d_from_centroid: distance from the centroid, positive = outward

        returns: tuple of the point's (x,y)
        """
        # find the angle in degrees
        centroid_angle = 0.5*(self.start_angle+self.end_angle)*pi/180.0
        # the radius of the centroid
        centroid_rad = self.inner_r+0.5*self.arc_thickness

        new_x = (centroid_rad + d_from_centroid)*cos(centroid_angle)
        new_y = (centroid_rad + d_from_centroid)*sin(centroid_angle)

        return (new_x, new_y)

    def display(self):
        """method to display the sector"""

        # draw the segment
        end = False
        if self.letter == '':
            end = True

        if self.level == 0:
            # don't draw anything in the center
            return

        if not end:
            # create the arc segment
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.arc_thickness+self.inner_r,
                                          self.end_angle, self.start_angle),
                                path.closepath())
            # render the arc segment onto the canvas
            self.shape_canvas.fill(segment,
                                   [color.gray(COLOUR_MAPPING[self.letter])])

            # write the letter
            #if (self.end_angle-self.start_angle) > (pi/400.0):
            #    text_coord = self.dist_from_centroid(self.text_pos+
            #                                         0.1*self.arc_thickness)
            #    # -0.1 on the x coordinate in order to center the letter better
            #    self.text_canvas.text(text_coord[0]-0.1, text_coord[1],
            #                          self.letter, [text.valign.middle])
            #    # draw dot on corresponding section, for clarity
            #    dot_coord = self.dist_from_centroid(self.text_pos)
            #    self.text_canvas.fill(path.circle(dot_coord[0], dot_coord[1],
            #                                      0.01), [color.rgb.black])

        else:
            segment = path.path(path.arc(0, 0, self.inner_r, self.start_angle,
                                         self.end_angle),
                                path.arcn(0, 0,
                                          self.arc_thickness+self.inner_r,
                                          self.end_angle, self.start_angle),
                                path.closepath())
            self.shape_canvas.fill(segment, [color.rgb.red])

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
        cur_text_pos = -0.5*self.arc_thickness
        if len(sorted_freq) is not 0:
            text_pos_incr = float(self.arc_thickness)/float(len(sorted_freq))
        for freq in sorted_freq:
            percent = float(freq)/float(total_freq)
            child_sector = Sector(child_lists[freq]['words'],
                                  self.level + 1,
                                  self.max_level,
                                  child_lists[freq]['letter'],
                                  self.shape_canvas,
                                  cur_percent,
                                  cur_percent+percent,
                                  self.inner_r + self.layer_thickness,
                                  self.layer_thickness,
                                  self.arc_thickness,
                                  self.start_angle,
                                  self.end_angle - self.start_angle,
                                  cur_text_pos
                                  )

            child_sector.create_child_segments()
            cur_percent += percent
            cur_text_pos += text_pos_incr


if __name__ == "__main__":
    shape_canvas = canvas.canvas()
    text_canvas = canvas.canvas()
    # create bounding box
    shape_canvas.fill(path.rect(-80,-80,160,160), [color.gray(1)])
    test_sector = Sector(word_list,
                         level=0,
                         max_level=17,
                         letter='_',
                         shape_canvas=shape_canvas,
                         start_percent=0,
                         end_percent=1,
                         inner_radius=0,
                         layer_thickness=7,
                         arc_thickness=3,
                         parent_angle=0,
                         parent_arc=360,
                         text_pos=0
                         )
    test_sector.create_child_segments()
    shape_canvas.insert(text_canvas)
    shape_canvas.writePDFfile('test1')
