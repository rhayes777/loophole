import pysimpledmx

dmx = pysimpledmx.DMXConnection(3)

dmx.setChannel(1, 255)  # set DMX channel 1 to full
dmx.setChannel(2, 128)  # set DMX channel 2 to 128
dmx.setChannel(3, 0)  # set DMX channel 3 to 0
dmx.render()  # render all of the above changes onto the DMX network

dmx.setChannel(4, 255, autorender=True)  # set channel 4 to full and render to the network
