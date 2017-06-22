import dancemat

mat = dancemat.DanceMat()


def listener(button):
    print "{} pressed".format(button)


mat.set_button_listener(listener)


while 1:
     mat.read()

