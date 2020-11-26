// C library headers
#ifndef __SIM_H__
#define __SIM_H__
#include <termios.h> // Contains POSIX terminal control definitions
#include <stdint.h>
#include <stdbool.h>

// Comment neu khong chay tren Pi
#define GPIO_ENABLE

// Baudrate mac dinh
#define BAUD B115200

#ifdef GPIO_ENABLE
#include <wiringPi.h>

// Chan cua Pi noi voi chan nguon cua SIM
#define POWER_PIN 1

// Bat nguon he thong
void sim_power_on();

// Tat nguon he thong
void sim_power_off();
#endif

// Khoi tao UART:
// port: cong UART
// enableDebug: cho phep log ra man hinh, dung trong che do Debug
bool at_init(char* port, bool enableDebug);

// Dung UART
void at_close();

// Kiem tra tinh san sang cua dich vu mang
bool sim_check_network();

// Thuc hien POST HTTP
// url:
// contentType:
// data:
// connTimeout: thoi gian toi da de ket noi toi Server, tu 20-120s, mac dinh 120s
// recvTimeout: thoi gian toi da de nhan phan hoi tu Server, tu 2-120s, mac dinh 10s
bool sim_http_post(const char* url, const char* contentType, const char* data, \
                const char* connTimeout, const char* recvTimeout);

// Bat dau phien dich vu GPS
void sim_gps_start();

// Doc GPS
bool sim_gps_get_position(char result[]);

// Dung phien dich vu GPS
void sim_gps_stop();

// Doc thoi gian
void sim_time(char result[]);

#endif