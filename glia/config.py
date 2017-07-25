import multiprocessing
import logging

logger = logging.getLogger('glia')
logger.setLevel(logging.DEBUG)


class DuplicateFilter(object):
    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv

dup_filter = DuplicateFilter()
logger.addFilter(dup_filter)

processes = multiprocessing.cpu_count()
plot_directory = None

# (x,y) Larry modified this from Tyler's original because there is no channel at position 15 [(0,4) in Tyler's scheme]
#       There are only 59 channels, not 60 (8 x 8 grid missing all 4 corners and 1 more on the left side of the array)
channel_map = {
    1: (3,6),
    2: (3,7),
    3: (3,5),
    4: (3,4),
    5: (2,7),
    6: (2,6),
    7: (1,7),
    8: (2,5),
    9: (1,6),
    10: (0,6),
    11: (1,5),
    12: (0,5),
    13: (2,4),
    14: (1,4),
    15: (0,3),
    16: (1,3),
    17: (2,3),
    18: (0,2),
    19: (1,2),
    20: (0,1),
    21: (1,1),
    22: (2,2),
    23: (1,0),
    24: (2,1),
    25: (2,0),
    26: (3,3),
    27: (3,2),
    28: (3,0),
    29: (3,1),
    30: (4,1),
    31: (4,0),
    32: (4,2),
    33: (4,3),
    34: (5,0),
    35: (5,1),
    36: (6,0),
    37: (5,2),
    38: (6,1),
    39: (7,1),
    40: (6,2),
    41: (7,2),
    42: (5,3),
    43: (6,3),
    44: (7,3),
    45: (7,4),
    46: (6,4),
    47: (5,4),
    48: (7,5),
    49: (6,5),
    50: (7,6),
    51: (6,6),
    52: (5,5),
    53: (6,7),
    54: (5,6),
    55: (5,7),
    56: (4,4),
    57: (4,5),
    58: (4,7),
    59: (4,6),
}

'''
# (x,y)
channel_map = {
    1: (3,6),
    2: (3,7),
    3: (3,5),
    4: (3,4),
    5: (2,7),
    6: (2,6),
    7: (1,7),
    8: (2,5),
    9: (1,6),
    10: (0,6),
    11: (1,5),
    12: (0,5),
    13: (2,4),
    14: (1,4),
    15: (0,4),  # there is no channel (0,4) [15 using the mea numbering system].  This an all following channels were renumbered
    16: (0,3),
    17: (1,3),
    18: (2,3),
    19: (0,2),
    20: (1,2),
    21: (0,1),
    22: (1,1),
    23: (2,2),
    24: (1,0),
    25: (2,1),
    26: (2,0),
    27: (3,3),
    28: (3,2),
    29: (3,0),
    30: (3,1),
    31: (4,1),
    32: (4,0),
    33: (4,2),
    34: (4,3),
    35: (5,0),
    36: (5,1),
    37: (6,0),
    38: (5,2),
    39: (6,1),
    40: (7,1),
    41: (6,2),
    42: (7,2),
    43: (5,3),
    44: (6,3),
    45: (7,3),
    46: (7,4),
    47: (6,4),
    48: (5,4),
    49: (7,5),
    50: (6,5),
    51: (7,6),
    52: (6,6),
    53: (5,5),
    54: (6,7),
    55: (5,6),
    56: (5,7),
    57: (4,4),
    58: (4,5),
    59: (4,7),
    60: (4,6)
}
'''
