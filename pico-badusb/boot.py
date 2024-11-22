import microcontroller
from storage import disable_usb_drive
microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
if(microcontroller.cpu.reset_reason != microcontroller.ResetReason.RESET_PIN):
    disable_usb_drive()