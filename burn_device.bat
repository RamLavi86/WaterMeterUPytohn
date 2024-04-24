esptool --chip esp32 --port COM4 erase_flash
esptool --chip esp32 --port COM4 --baud 115200 write_flash -z 0x1000 ESP32_GENERIC-20240222-v1.22.2.bin
ampy --port COM4 put umail.py
ampy --port COM4 put main.py /main.py