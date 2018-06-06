import time, sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
inpt = 26
GPIO.setup(inpt, GPIO.IN)
rate_cnt = 0
tot_cnt = 0
minutes = 0
#constant = 0.58
constant = 10
time_new = 0.0

print('Water Flow - Approximate')
print('Control C to Exit')

while True:
    time_new = time.time() + 1
    rate_cnt = 0
    #while time.time() <= time_new:
    #    if GPIO.input(inpt) != 0:
    #        rate_cnt +=1
    #        tot_cnt += 1
    #    try:
    #        test=0
    #        #print(GPIO.input(inpt), end='')
    #    except KeyboardInterrupt:
    #        print('\nCTRL C - Exiting nicely')
    #        GPIO.cleanup()
    #        sys.exit()

    #minutes +=1
    #print('\nLiters / 1 sec ', round(rate_cnt * constant,4))
    #print('Total Liters ',round(tot_cnt*constant,4))
    #print('Time (min &clock) ', minutes, '\t', time.asctime(time_new))
    
    while time.time() <= time_new:
        try:
            testese=0
        except KeyboardInterrupt:
            print('\nCTRL C - Exiting nicely')
            GPIO.cleanup()
            sys.exit()

    rate_cnt =  constant
    tot_cnt += constant
    print('\nLiters / 1 sec ', rate_cnt)
    print('Total Liters ',tot_cnt)


GPIO.cleanup()
print('Done')   
