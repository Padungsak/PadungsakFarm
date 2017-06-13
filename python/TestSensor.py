import time, sys
import spidev               # use the 'spidev' Python module
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

spi = spidev.SpiDev()
spi.open(0,0)               # use the SPI device '/dev/spi0.0'
spi.mode = 0                # use SPI mode 0
spi.bits_per_word = 8       # 8 bits 
spi.max_speed_hz = 1000000  # set SCK speed to 1MHz

def read_adc_3208( chan ):
    cmd_seq = [0x00,0x00,0x00]  # define 3-byte test data
    # use single-ended and MSB first settings
    chan = chan & 0b00000111
    cmd_seq[0] = (1 << 2) | (1 << 1) | (chan >> 2)
    cmd_seq[1] = (chan << 6)
    buf = list( cmd_seq )
    resp = spi.xfer2( buf )    # send/receive data through the SPI
    value = (int(resp[1]) & 0x0f)
    value = (value << 8) + (int(resp[2]))
    return value

try:
    vcc = 3.300  # Vref for the ADC
    while True:
        for chan in range(1):  # read only four ADC channels 
            x = read_adc_3208( chan )   # read analog value from channel 0
            print  'Ch%d: %d GPIO: %d' % (chan,x, GPIO.input(4)),
        print ''
        time.sleep( 0.5 )      # wait for 0.2 seconds

except KeyboardInterrupt as ex:
    sys.stdout.write( 'Stopped...\n' )
    sys.stdout.flush()
finally:
    spi.close()
