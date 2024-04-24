esptool and ampy are already installed on my computer

erase flash: esptool --chip esp32 --port COMx erase_flash

write to flash: esptool --chip esp32 --port COMx --baud 115200 write_flash -z 0x1000 <firmware_file_path>
example: esptool --chip esp32 --port COMx --baud 115200 write_flash -z 0x1000 ESP32_GENERIC-20240222-v1.22.2.bin

ampy --port COM4 put umail.py

place file: ampy --port COM4 put main.py /main.py

ERASE THE DATA BEFORE AMPY PUT

https://docs.google.com/spreadsheets/d/1bb7gqN_zQXo1Kv-1fDcrIbNl6G4wWBjFz5TazAkRxYQ/edit?usp=sharing

In order to run REPL (read evaluate print loop) go to PuTTy, connect COMx with baud rate of 115200, when you get a black screen press CTRL+C and then the CLI will work

https://randomnerdtutorials.com/micropython-send-emails-esp32-esp826/

upload umail to device

test