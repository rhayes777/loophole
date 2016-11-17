import colorsys


HUE_MAX = 65535


def hbs_to_rgb(hue, brightness, saturation):
    return colorsys.hls_to_rgb(hue / HUE_MAX, brightness / 255, saturation / 255)


class Light:
    MASTER_DIMMING = 1
    RED_DIMMING = 2
    GREEN_DIMMING = 3
    BLUE_DIMMING = 4
    STROBE_CONTROL = 5
    MASTER_FUNCTION = 6

    def __init__(self, dmx_connection, address):
        assert 0 < address <= 512
        self.address = address
        self.dmx_connection = dmx_connection

    def set_rgb(self, r, g, b):
        self.set_r(r)
        self.set_g(g)
        self.set_b(b)

    def set_hbs(self, h, b, s):
        self.set_brightness(255)
        self.set_rgb(*hbs_to_rgb(h, b, s))

    def set_r(self, r):
        self.dmx_connection.setChannel(Light.RED_DIMMING, r)

    def set_g(self, g):
        self.dmx_connection.setChannel(Light.GREEN_DIMMING, g)

    def set_b(self, b):
        self.dmx_connection.setChannel(Light.BLUE_DIMMING, b)

    def set_brightness(self, brightness):
        self.dmx_connection.setChannel(Light.MASTER_DIMMING, brightness)

    def set_strobe_speed(self, speed):
        self.dmx_connection.setChannel(Light.STROBE_CONTROL, speed)

    def set_master(self, master):
        self.dmx_connection.setChannel(Light.MASTER_FUNCTION, master)
