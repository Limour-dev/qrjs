import microcontroller
from storage import disable_usb_drive
from usb_cdc import disable as disable_usb_cdc
from usb_midi import disable as disable_usb_midi
import usb_hid

try:
    from supervisor import set_usb_identification
except ModuleNotFoundError:
    set_usb_identification = lambda **kwargs: print(kwargs)

set_usb_identification(
    manufacturer = 'limour',
    product = 'keyboard',
    vid = 0x1d6b,
    pid = 0x1347
)

microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
if(microcontroller.cpu.reset_reason != microcontroller.ResetReason.RESET_PIN):
    disable_usb_drive()
    disable_usb_cdc()
    disable_usb_midi()
    usb_hid.disable()
    usb_hid.enable((usb_hid.Device.KEYBOARD,))