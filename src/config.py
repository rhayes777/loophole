import os
from ConfigParser import ConfigParser
from sys import argv

directory = os.path.realpath(os.path.dirname(__file__))

parser = ConfigParser()

if len(argv) > 1:
    parser.read(argv[1])
else:
    parser.read("{}/config.ini".format(directory))

MASS = float(parser.get("physics", "MASS"))
DISTANT_MASS = float(parser.get("physics", "DISTANT_MASS"))
COLLISION_RADIUS = float(parser.get("physics", "COLLISION_RADIUS"))
SPEED = float(parser.get("physics", "SPEED"))
ELASTIC_FORCE = float(parser.get("physics", "ELASTIC_FORCE"))
BOOST_SPEED = float(parser.get("physics", "BOOST_SPEED"))
DAMPING_RATE = float(parser.get("physics", "DAMPING_RATE"))
POINTS_PER_NOTE = int(parser.get("physics", "POINTS_PER_NOTE"))
DECAY_RATE = int(parser.get("physics", "DECAY_RATE"))

TRACK_NAME = parser.get("music", "TRACK_NAME")

MINIM = parser.get("visual", "MINIM")
CROTCHET = parser.get("visual", "CROTCHET")
QUAVER = parser.get("visual", "QUAVER")
SEMIQUAVER = parser.get("visual", "SEMIQUAVER")
CROTCHET_GLOW_ROTATION = parser.get("visual", "CROTCHET_GLOW_ROTATION")
ENERGY_GLOW = parser.get("visual", "ENERGY_GLOW")
PLAYER_CURSOR = parser.get("visual", "PLAYER_CURSOR")
INDENT = int(parser.get("visual", "INDENT"))

screen_shape = tuple(map(int, parser.get("visual", "screen_shape").split(",")))
FULLSCREEN = "t" in parser.get("visual", "FULLSCREEN").lower()
DOUBLEBUF = "t" in parser.get("visual", "DOUBLEBUF").lower()

mido_backend = parser.get("interface", "mido_backend")


SPACE_FIGHTER_PLAYER_VELOCITY = float(parser.get("space_fighter", "PLAYER_VELOCITY"))

NOTES_PER_SIDE = int(parser.get("space_fighter", "NOTES_PER_SIDE"))
