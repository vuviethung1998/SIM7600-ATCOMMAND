// gcc -o main main.c sim.c

#include "sim.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> 

int main() { 
    // Open the serial port. Change device path as needed (currently set to an standard FTDI USB-UART cable type device)        
    if (at_init("/dev/ttyS0", true) == false)
    {
        printf("Error at_init()");
        exit(-1);
    }

    char result[256];
    if (sim_check_network() != true)
    {
        printf("Error sim_check_network()");
        at_close();
        exit(-1);
    }

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
    
    at_close();
    return 0; // success
}