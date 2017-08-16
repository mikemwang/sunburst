"""classes that group together related properties"""

# NOTE: doing this reduces the number of local variables floating around in any
# given class, as well as making it easy to add more properties later on. For
# instance, if we wanted to add a geometric property we could simply add it to
# the relevant class instead of having to change the object constructor every
# time that object is instantiated

class Canvases(object):
    """container for the necessary canvases"""

    def __init__(self, shape_canvas, text_canvas):
        self.shape = shape_canvas
        self.text = text_canvas

class Layer_Properties(object):
    """container for various geometric properties"""

    def __init__(self,
                 layer_thickness,
                 data_sector_thickness,
                 end_sector_thickness):

        self.thickness = layer_thickness
        self.data_sector_thickness = data_sector_thickness
        self.end_sector_thickness = end_sector_thickness
