#include "mbed.h"

/* Motor Pins for IC in sequence - green, black, blue, red */
/* mBed pins for IC in sequence - p24, p23, p22, p21 */

DigitalOut a(p24);
DigitalOut a_(p23);
DigitalOut b(p22);
DigitalOut b_(p21);

char state_array[] = {0x06, 0x02, 0x0A, 0x08, 0x09, 0x01, 0x05, 0x04};

int main() {
            int idx = 0;
            a = state_array[idx] & (1<<0);
            a_ = state_array[idx] & (1<<1);
            b = state_array[idx] & (1<<2);
            b_ = state_array[idx] & (1<<3);    
    
    while(1) {
        for(int cycle = 0; cycle < 50; cycle++)
        {
            for(int idx=0; idx<8; idx++)
            {
                a = state_array[idx] & (1<<0);
                a_ = state_array[idx] & (1<<1);
                b = state_array[idx] & (1<<2);
                b_ = state_array[idx] & (1<<3);                
                wait(0.01);
            }
        }
        wait(1);
    }
}
