#include "sim.h"

// C library headers
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// Linux headers
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()

static int serial_g = 0;
static bool Debug = true;

bool at_init(char* port, bool enableDebug)
{
    Debug = enableDebug;
    serial_g = open(port, O_RDWR | O_NOCTTY | O_SYNC);
    // Create new termios struc, we call it 'tty' for convention
    struct termios tty;

    // Read in existing settings, and handle any error
    if(tcgetattr(serial_g, &tty) != 0) {
        printf("Error %i from tcgetattr: %s\n", errno, strerror(errno));
        return false;
    }

    tty.c_cflag &= ~PARENB; // Clear parity bit, disabling parity (most common)
    tty.c_cflag &= ~CSTOPB; // Clear stop field, only one stop bit used in communication (most common)
    tty.c_cflag &= ~CSIZE; // Clear all bits that set the data size 
    tty.c_cflag |= CS8; // 8 bits per byte (most common)
    tty.c_cflag &= ~CRTSCTS; // Disable RTS/CTS hardware flow control (most common)
    tty.c_cflag |= CREAD | CLOCAL; // Turn on READ & ignore ctrl lines (CLOCAL = 1)

    tty.c_lflag &= ~ICANON;
    tty.c_lflag &= ~ECHO; // Disable echo
    tty.c_lflag &= ~ECHOE; // Disable erasure
    tty.c_lflag &= ~ECHONL; // Disable new-line echo
    tty.c_lflag &= ~ISIG; // Disable interpretation of INTR, QUIT and SUSP
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // Turn off s/w flow ctrl
    tty.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL); // Disable any special handling of received bytes

    tty.c_oflag &= ~OPOST; // Prevent special interpretation of output bytes (e.g. newline chars)
    tty.c_oflag &= ~ONLCR; // Prevent conversion of newline to carriage return/line feed
    // tty.c_oflag &= ~OXTABS; // Prevent conversion of tabs to spaces (NOT PRESENT ON LINUX)
    // tty.c_oflag &= ~ONOEOT; // Prevent removal of C-d chars (0x004) in output (NOT PRESENT ON LINUX)

    tty.c_cc[VTIME] = 1;    // Wait for up to 0.1s (10 deciseconds), returning as soon as any data is received.
    tty.c_cc[VMIN] = 0;

    // Set in/out baud rate to be baud
    cfsetispeed(&tty, BAUD);
    cfsetospeed(&tty, BAUD);

    // Save tty settings, also checking for error
    if (tcsetattr(serial_g, TCSANOW, &tty) != 0) {
        printf("Error %i from tcsetattr: %s\n", errno, strerror(errno));
        return false;
    }
    if (Debug) printf("init AT success\n");
    return true;
}

void at_close()
{
    close(serial_g);
}

bool _at_send(const char* ATcommand, const char* expected_answer, char* response, unsigned int timeout, unsigned int step_check)
{   
    char _response[256];
    char buff[256];    

    tcflush(serial_g,TCIOFLUSH);
        
    memset(_response, '\0', 256);    // Initialize the string    
    memset(buff, '\0', 256);

    // Send AT command
    if (ATcommand != NULL)
    {             
        write(serial_g, ATcommand, strlen(ATcommand)); 
        write(serial_g, "\r\n", strlen("\r\n"));
        if (Debug) printf("%s\r\n", ATcommand);
    }
    
    // Read response
    int num_bytes1, num_bytes2;
    for (unsigned int i = 0; i < (timeout / step_check); i++)
    {   
        // printf("sleep");        
        usleep(step_check*1000);
        // printf("sleep done");

        num_bytes1 = read(serial_g, buff, sizeof(buff));
        if (num_bytes1 > 0)
        {
            if (num_bytes1 > 255 )
            {
                // byte 256 = '\0'
                strncpy(_response, buff, 255);
                break;
            }
            // else
            strncpy(_response, buff, num_bytes1);

            memset(buff, '\0', 256);
            usleep(step_check*1000);

            num_bytes2 = read(serial_g, buff, sizeof(buff));
            if (num_bytes2 > 0)
            {
                // byte 256 = '\0'
                strncpy(_response + num_bytes1, buff, 255 - num_bytes1);
            }
            break;
        }
    }
    if (Debug) printf("%s", _response);

    if (response != NULL)
    {
        strcpy(response, _response);
    }
    
    if (strstr(_response, expected_answer) != NULL)
    {        
        return true;
    }
    
    return false;
}

bool sim_check_network()
{
    // Check AT service
    if (_at_send("AT", "OK", NULL, 1000, 10) != true) return false;

    // SIM Card Status
    if (_at_send("AT+CPIN?", "READY", NULL, 1000, 10) != true) return false;

    // Check signal quality
    if (_at_send("AT+CSQ", "OK", NULL, 1000, 10) != true) return false;

    // GPRS network status
    if (_at_send("AT+CREG?", "+CREG: 0,1", NULL, 1000, 10) != true) return false;
    if (_at_send("AT+CGREG?", "+CGREG: 0,1", NULL, 1000, 10) != true) return false;

    // end the previous http session if any
    _at_send("AT+HTTPTERM", "OK", NULL, 120000, 10);

    return true;
}

bool _http_config_param(const char* url, const char* contentType, const char* connTimeout, const char* recvTimeout)
{       
    char str[256];
    // config param: url
    sprintf(str, "AT+HTTPPARA=\"URL\",\"%s\"", url);
    if (_at_send(str, "OK", NULL, 1000, 10) != true) return false;

    // config param: content type
    sprintf(str, "AT+HTTPPARA=\"CONTENT\",\"%s\"", contentType);
    if (_at_send(str, "OK", NULL, 1000, 10) != true) return false;

    // config param: connect timeout
    sprintf(str, "AT+HTTPPARA=\"CONNECTTO\",%s", connTimeout);
    if (_at_send(str, "OK", NULL, 1000, 10) != true) return false;

    // config param: recive timeout
    sprintf(str, "AT+HTTPPARA=\"RECVTO\",%s", connTimeout);
    if (_at_send(str, "OK", NULL, 1000, 10) != true) return false;

    return true;
}

bool sim_http_post(const char* url, const char* contentType, const char* data, \
                const char* connTimeout, const char* recvTimeout)
{
    bool ok = true;
    char str[256];

    // Start HTTP session
    _at_send("AT+HTTPINIT", "OK", NULL, 120000, 10);

    // Config HTTP session
    if (_http_config_param(url, contentType, connTimeout, recvTimeout) != true)
    {
        // End HTTP session
        _at_send("AT+HTTPTERM", "OK", NULL, 120000, 10);
        return false;
    }

    // POST data
    sprintf(str, "AT+HTTPDATA=%d,10000", strlen(data));
    ok = _at_send(str, "DOWNLOAD", NULL ,1000, 10);
    if (ok)
    {
        ok = _at_send(data, "OK", NULL, 1000, 10);
        if (ok)
        {
            ok = _at_send("AT+HTTPACTION=1", "OK", NULL, 1000, 10);
            if (ok)
            {
                // "1,200" <-> Action = 1 = POST; Status =  200 = success
                ok = _at_send(NULL, "1,200", NULL, 120000, 10);
            }       
        }
    }
        
    // End HTTP session
    _at_send("AT+HTTPTERM", "OK", NULL, 120000, 10);
    return ok;
}                

bool sim_gps_get_position(char result[])
{
    bool ok = true;
    // Start GPS session
    _at_send("AT+CGPS=1", "OK", NULL, 1000, 10);

    // Get GPS info
    ok = _at_send("AT+CGPSINFO", "OK", result, 1000, 10);
    // End GPS session
    _at_send("AT+CGPS=0", "+CGPS:0", NULL, 1000, 10);

    if (ok != true) return false;
    if (strstr(result, ",,,,") != NULL) return false;

    return true;
}

void sim_time(char result[])
{
    _at_send("AT+CCLK?", "OK", result, 1000, 10);
}