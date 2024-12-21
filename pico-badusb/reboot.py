import microcontroller
print(microcontroller.cpu.reset_reason)
microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
microcontroller.reset()