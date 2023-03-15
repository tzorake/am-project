#ifndef _CONE_H_
#define _CONE_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif /* HAVE_CONFIG_H */

#include <stdio.h>
#include <stdarg.h>

#undef	MAX
#define MAX(a, b)  (((a) > (b)) ? (a) : (b))

#undef	MIN
#define MIN(a, b)  (((a) < (b)) ? (a) : (b))

#undef	ABS
#define ABS(a)	   (((a) < 0) ? -(a) : (a))

#undef	SQR
#define SQR(a)	   ((a) * (a))

#define FILENAME_MAX_SIZE	(100)

#define DEFAULT_PORT    (31415)
#define SERVER_VER_MAJOR (2)
#define SERVER_VER_MINOR (0)
#define SERVER_VER_MICRO (0)
#define SERVER_VER(MAJOR, MINOR, MICRO) ((((MAJOR) & 0xff) << 16) | (((MINOR) & 0xff) << 8) | (((MICRO) & 0xff) << 0))

typedef char str_t[FILENAME_MAX_SIZE];

#define RL_MAKE_PROTOS
#include <resource.h>

#ifndef	FALSE
#define	FALSE	FALSE
#endif

#ifndef	TRUE
#define	TRUE	TRUE
#endif

#ifndef HAVE_GETTIMEOFDAY
#include <winsock2.h>
#define gettimeofday(x, y) ({ (x)->tv_sec = time (NULL); (x)->tv_usec = 0; })
#endif /* HAVE_GETTIMEOFDAY */

extern volatile int (*interrupt_handler) (void);
extern FILE * logfd;
int run_method (parameters_t*);

static __inline__ void __attribute__ ((format (printf, 4, 5)))
error (const char * file, const char * func, int line, const char *format, ...)
{
  va_list args;
  if (!logfd)
    return;
  va_start (args, format);
  fprintf (logfd, "File %s function %s() line %d: ", file, func, line);
  vfprintf (logfd, format, args);
  fflush (logfd);
  va_end (args);
}

#define ERROR_(MSG...) error(__FILE__, __PRETTY_FUNCTION__, __LINE__, MSG)

#endif /* _CONE_H_ */
