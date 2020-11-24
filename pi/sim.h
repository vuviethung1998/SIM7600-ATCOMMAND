// C library headers
#ifndef __SIM_H__
#define __SIM_H__
#include <termios.h> // Contains POSIX terminal control definitions
#include <stdint.h>
#include <stdbool.h>

#define GPIO_ENABLE

#define BAUD B115200

#ifdef GPIO_ENABLE
#include <wiringPi.h>

#define POWER_PIN 1

void sim_power_on();
void sim_power_off();
#endif

bool at_init(char* port, bool enableDebug);
void at_close();
bool sim_check_network();

bool sim_http_post(const char* url, const char* contentType, const char* data, \
                const char* connTimeout, const char* recvTimeout);

void sim_gps_start();
bool sim_gps_get_position(char result[]);
void sim_gps_stop();

void sim_time(char result[]);

#endif