import os
from ConfigParser import ConfigParser

directory = os.path.realpath(os.path.dirname(__file__))

parser = ConfigParser()

parser.read("{}/config.ini".format(directory))

MASS = float(parser.get("physics", "MASS"))
DISTANT_MASS = float(parser.get("physics", "DISTANT_MASS"))
COLLISION_RADIUS = float(parser.get("physics", "COLLISION_RADIUS"))
VELOCITY = float(parser.get("physics", "VELOCITY"))
SPEED = float(parser.get("physics", "SPEED"))
ELASTIC_FORCE = float(parser.get("physics", "ELASTIC_FORCE"))
BOOST_SPEED = float(parser.get("physics", "BOOST_SPEED"))
DAMPING_RATE = float(parser.get("physics", "DAMPING_RATE"))
POINTS_PER_NOTE = int(parser.get("physics", "POINTS_PER_NOTE"))
DECAY_RATE = int(parser.get("physics", "DECAY_RATE"))
