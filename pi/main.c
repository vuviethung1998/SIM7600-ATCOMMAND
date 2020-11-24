// gcc -Wall -o main main.c sim.c
// gcc -Wall -o main main.c sim.c -lwiringPi

#include "sim.h"
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> 

int main() { 
    #ifdef GPIO_ENABLE
    sim_power_on();
    #endif

    // Open the serial port. Change device path as needed (currently set to an standard FTDI USB-UART cable type device)        
    if (at_init("/dev/ttyS0", true) == false)
    {
        printf("Error at_init()");
        exit(-1);
    }
    
    while( sim_check_network() != true)
    {
        printf("Error sim_check_network()\n");
        printf("Retry\n");
        sleep(2);
    }

    // Start GPS session
    sim_gps_start();
    
    char result[256];
    for(int i = 0; i < 5; i++)
    {
        // Get time
        sim_time(result);

        // Get GPS
        if (sim_gps_get_position(result) != true)
        {
            printf("Error sim_gps_get_position()\n");
        }

        // POST HTTP
        if (sim_http_post("http://httpbin.org/post", "application/json", "{\"hello\":123}", "20", "5") != true)
        {
            printf("Error sim_http_post()\n");
        }
    }
        
    // Stop GPS session
    sim_gps_stop();
    
    at_close();

    #ifdef GPIO_ENABLE
    sim_power_off();
    #endif

    return 0; // success
}