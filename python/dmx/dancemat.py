import sys
import usb.core
import usb.util


class DanceMat:
    def __init__(self, product_id=0x0011, vendor_id=0x0079):
        self.dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

        interface = 0
        self.endpoint = self.dev[0][(0, 0)][0]

        # if the OS kernel already claimed the device, which is most likely true
        # thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
        if self.dev.is_kernel_driver_active(interface) is True:
            self.dev.detach_kernel_driver(interface)
            usb.util.claim_interface(self.dev, interface)

    def read(self):
        self.dev.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)


mat = DanceMat()
print mat.read()
