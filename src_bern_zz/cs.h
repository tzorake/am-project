#ifndef _CS_H_
#define _CS_H_

#include <cone.h> /* for parameters_t & SERVER_VER */

#include <string.h> /* for NULL */
#include <signal.h> /* signal functions */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif /* HAVE_CONFIG_H */

#ifndef SD_BOTH
#define SD_BOTH (2)
#endif /* SD_BOTH */
#ifndef __MINGW32__
#define closesocket close
#endif /* __MINGW32__ */

typedef struct {
  int version;
  int tasks_in_progress;
  parameters_t current_params;
} server_info_t;

#define SERVER_VER_ SERVER_VER(SERVER_VER_MAJOR, SERVER_VER_MINOR, SERVER_VER_MICRO)

#define STRUCT_TMPLT "\n{A: %lg, size: %d}\n"
#define HEADER_TMPLT "[Distributed calculation server ver: 0x%x Header size: %d]\n"

int run_server (parameters_t*);
int server_collect (parameters_t*);
int run_client (parameters_t*);

static __inline__ int
blocksig (int sig)
{
#ifdef HAVE_SIGNALS
  sigset_t block_mask;
  sigemptyset (&block_mask);
  sigaddset (&block_mask, sig);
  return sigprocmask (SIG_BLOCK, &block_mask, NULL);
#else /* ! HAVE_SIGNALS */
  return (SIG_ERR != signal (sig, SIG_IGN));
#endif /* HAVE_SIGNALS */
}

#endif /* _CS_H_ */
