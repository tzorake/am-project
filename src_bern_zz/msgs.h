#ifndef _MSGS_H_
#define _MSGS_H_

#include <sys/types.h>
#ifdef HAVE_STDINT_H
#include <stdint.h>
#else /* ! HAVE_STDINT_H */
typedef u_int8_t uint8_t;
typedef u_int16_t uint16_t;
typedef u_int32_t uint32_t;
#endif /* HAVE_STDINT_H */

#define MSG_SIGNATURE 0xF00FC7C8 /* pentium bug */

typedef enum {
  NOP = 0,
  TASK_REQ, /* task request from client to server */
  TASK_TODO, /* task from server to client */
  TASK_RES, /* task results from client to server */
  JOB_END, /* no more tasks for client */
  GET_SERVER_INFO, /* request for misc server information */
  SERVER_INFO, /* returnig misc server information */
  NUM_CMD /* always keep last */
} cmd_t;

typedef struct __attribute__ ((packed)) {
  uint32_t sig;
  uint32_t size;
  cmd_t cmd;
  int8_t data[0];
} msg_header_t;

#endif /* _MSGS_H_ */
