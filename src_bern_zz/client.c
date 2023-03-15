/* -*- C -*- */
/* I hate this bloody country. Smash. */
/* This file is part of INFINITE PLATE OSCILLATIONS project */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <signal.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#ifdef __MINGW32__
#include <winsock2.h>
#else /* ! __MINGW32__ */
#include <netdb.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#endif /* __MINGW32__ */

#include <cone.h>
#include <msgs.h>
#include <cs.h>

#define FILENAME_TMPLT "dataXXXXXX"
static volatile sig_atomic_t interrupt_flag;
static int client_retry_period;
static int sock;

static int
send_to_server (int fd, cmd_t cmd, int size, int8_t data[])
{
  msg_header_t msg_h;
  
  msg_h.sig = MSG_SIGNATURE;
  msg_h.size = size + sizeof (msg_header_t);
  msg_h.cmd = cmd;

  if ((int)sizeof (msg_h) > send (fd, (const char*)&msg_h, sizeof (msg_h), 0))
    {
      ERROR_ ("Failed to send message header to sockect: '%s'.\n",
	      strerror (errno));
      return 0;
    }

  if (size > 0)
    if (size > send (fd, (const char*)data, size, 0))
      {
	ERROR_ ("Failed to send message body to sockect.\n");
	return 0;
      }

  return msg_h.size;
}

static msg_header_t *
read_from_server (int fd)
{
  msg_header_t msg_h;
  msg_header_t * msg;
  int size, read_size;
  char * data;
  fd_set read_fd_set;
  
  FD_ZERO (&read_fd_set);
  FD_SET (fd, &read_fd_set);

  if ((int)sizeof (msg_h) > recv (fd, (char*)&msg_h, sizeof (msg_h), 0))
    {
      ERROR_ ("Failed to receive message header.\n");
      return NULL;
    }
  
  if (msg_h.sig != MSG_SIGNATURE)
    {
      ERROR_ ("Message signature failed (read 0x%08x should be 0x%08x).\n",
	     msg_h.sig, MSG_SIGNATURE);
      return NULL;
    }
  
  if (!(msg = (msg_header_t*)malloc (msg_h.size)))
    {
      /* FIXME: all further data should be readed and discarded
	 but after such error client will shutdown and no need
	 to prepare socket for reading next message */
      ERROR_ ("Failed to malloc() for message.\n");
      return NULL;
    }

  memcpy (msg, &msg_h, sizeof (msg_h));
  size = msg_h.size - sizeof (msg_header_t);
  data = ((char*)msg) + sizeof (msg_header_t);
  while (size > 0)
    {
      /* wait until new chunk can be readed */
      if (0 > select (FD_SETSIZE, &read_fd_set, NULL, NULL, NULL))
	{
	  ERROR_ ("Failed in select for message reading.\n");
	  free (msg);
	  return NULL;
	}      

      if (0 >= (read_size = recv (fd, (char*)data, size, 0)))
	{
	  ERROR_ ("Failed to receive from sockect : %s\n", strerror (errno));
	  free (msg);
	  return NULL;
	}
      
      data += read_size;
      size -= read_size;
    }

  return msg;
}

static int
do_1_task (int fd)
{
  msg_header_t * task_msg;
  FILE * output_fd = NULL;
  char * buf = NULL;
  int size = 0;
  int status;
  
  if (!(send_to_server (fd, TASK_REQ, 0, NULL)))
    {
      ERROR_ ("Failed to request task.\n");
      return EXIT_FAILURE;
    }
  
  if (!(task_msg = read_from_server (fd)))
    {
      ERROR_ ("Failed to read the task.\n");
      return EXIT_FAILURE;
    }

  if ((task_msg->cmd == JOB_END)
      && (task_msg->size == sizeof (msg_header_t)))
    {
      fprintf (logfd, "JOB_END message received - closing connection.\n");
      fflush (logfd);
      free (task_msg);
      return EXIT_FAILURE; /* no errors just exit */
    }
  
  if ((task_msg->cmd != TASK_TODO)
      || (task_msg->size != sizeof (parameters_t) + sizeof (msg_header_t)))
    {
      ERROR_ ("Wrong answer from server.\n");
      free (task_msg);
      return EXIT_FAILURE;
    }

  fprintf (logfd, "Start new task: a0_1 %g\n",
	   ((parameters_t*)(task_msg->data))->a0_1);
  fflush (logfd);

  interrupt_flag = FALSE;
  memcpy (((parameters_t*)(task_msg->data))->output_file,
	  FILENAME_TMPLT, sizeof (FILENAME_TMPLT));
  mktemp (((parameters_t*)(task_msg->data))->output_file);

#ifdef HAVE_SIGNALS
  fcntl (fd, F_SETFL, FASYNC | fcntl (fd, F_GETFL, 0));
#endif /* HAVE_SIGNALS */
  status = run_method ((parameters_t*)(task_msg->data));
#ifdef HAVE_SIGNALS
  fcntl (fd, F_SETFL, ~FASYNC & fcntl (fd, F_GETFL, 0));
#endif /* HAVE_SIGNALS */

  if (interrupt_flag)
    {
      fprintf (logfd, "\rServer shutdown the socket.\n");
      if (0 > unlink (((parameters_t*)(task_msg->data))->output_file))
	ERROR_ ("unlink for file `%s` failed : %s\n",
	       ((parameters_t*)(task_msg->data))->output_file,
	       strerror (errno));
      free (task_msg);
      return EXIT_FAILURE;
    }

  output_fd = fopen (((parameters_t*)(task_msg->data))->output_file, "rb");

  if (NULL == output_fd)
    {
      ERROR_ ("Failed to open output file for reading\n");
      free (task_msg);
      exit (EXIT_FAILURE);
    }
  
  if (!fseek (output_fd, 0, SEEK_END))
    {
      if (0 > (size = ftell (output_fd)))
	{
	  ERROR_ ("Failed in ftell for retunning result.\n");
	  size = 0;
	}
      else if (!(buf = (char*)malloc (size)))
	{
	  ERROR_ ("Failed in malloc for retunning result.\n");
	  size = 0;
	}
      else if (fseek (output_fd, 0, SEEK_SET))
	{
	  ERROR_ ("Failed in fseek for retunning result.\n");
	  size = 0;
	}
      else if (0 > (size = fread (buf, 1, size, output_fd)))
	{
	  ERROR_ ("Failed in read retunning result.\n");
	  size = 0;
	}      
    }

  /* close and delete temporary file */
  if (output_fd)
    fclose (output_fd);
  if (0 > unlink (((parameters_t*)(task_msg->data))->output_file))
    ERROR_ ("unlink for file `%s` failed : %s\n",
	   ((parameters_t*)(task_msg->data))->output_file,
	   strerror (errno));
  
  free (task_msg);
  
  if (!(send_to_server (fd, TASK_RES, size, buf)))
    {
      ERROR_ ("Failed to return results to server.\n");
      status = EXIT_FAILURE;
    }

  if (buf)
    free (buf);
  
  return status;
}

static int
check_server_version (int fd)
{
  msg_header_t * info;

  if (!(send_to_server (fd, GET_SERVER_INFO, 0, NULL)))
    {
      ERROR_ ("Failed to get server info.\n");
      return EXIT_FAILURE;
    }
  
  if (!(info = read_from_server (fd)))
    {
      ERROR_ ("Failed to read the server info.\n");
      return EXIT_FAILURE;
    }

  if ((info->cmd != SERVER_INFO)
      || (info->size != sizeof (msg_header_t) + sizeof (server_info_t)))
    {
      ERROR_ ("Failed to get server info. Wrong answer from server.\n");
      free (info);
      return EXIT_FAILURE;
    }
  
  if (((server_info_t*)(info->data))->version != SERVER_VER_)
    {
      ERROR_ ("Server version mismatch"
	     " (get 0x%08x should be 0x%08x).\n",
	     ((server_info_t*)(info->data))->version, SERVER_VER_);
      free (info);
      return EXIT_FAILURE;
    }
  free (info);
  
  return EXIT_SUCCESS;
}

static unsigned int
my_sleep (unsigned int sec)
{
  struct timeval timeout = { .tv_sec = sec, .tv_usec = 0, };
  return select (FD_SETSIZE, NULL, NULL, NULL, &timeout);
}

static int
time_to_sleep (int start_min, int stop_min)
{
  char buffer[16];
  time_t curtime;
  struct tm * loctime;
  int hours, minutes;
     
  /* Get the current time. */
  curtime = time (NULL);
     
  /* Convert it to local time representation. */
  loctime = localtime (&curtime);
     
  /* Print it out in a nice format. */
  strftime (buffer, sizeof (buffer), "%H:%M", loctime);
  sscanf (buffer, "%d:%d", &hours, &minutes);
  minutes += hours * 60;
  
  return ((minutes < start_min) != (minutes < stop_min))
    != (start_min < stop_min);
}

#ifdef HAVE_SIGNALS
volatile static int
client_interrupt_handler (void)
{
  return interrupt_flag;
}

static void
io_handler (int signum)
{
  interrupt_flag = TRUE;
}
     
static void
set_sigio_handler (void)
{
  struct sigaction new_action, old_action;
     
  /* Set up the structure to specify the new action. */
  new_action.sa_handler = io_handler;
  sigemptyset (&new_action.sa_mask);
  new_action.sa_flags = 0;
     
  sigaction (SIGIO, NULL, &old_action);
  if (old_action.sa_handler != SIG_IGN)
    sigaction (SIGIO, &new_action, NULL);
}

#else /* ! HAVE_SIGNALS */

volatile static int
client_interrupt_handler (void)
{
  static time_t last_enter_time = 0;
  time_t new_enter_time = time (NULL);

  if (difftime (new_enter_time, last_enter_time) > client_retry_period)
    {
      static struct timeval timeout = {.tv_sec = 0, .tv_usec = 0,};
      fd_set poll_fd_set;
      
      /* Initialize the set of poll sockets. */
      FD_ZERO (&poll_fd_set);
      FD_SET (sock, &poll_fd_set);

      select (sock + 1, &poll_fd_set, NULL, NULL, &timeout);
      /* Even if select failed sock will be marked */
      interrupt_flag = FD_ISSET (sock, &poll_fd_set);
      last_enter_time = new_enter_time;
    }
      
  return interrupt_flag;
}

#endif /* HAVE_SIGNALS */

int
run_client (parameters_t * params_)
{
  struct sockaddr_in host;
  int connection_attempt = 0;

  /* if server unexpectedly terminates client should stay alive */
#ifdef HAVE_SIGNALS
  blocksig (SIGPIPE); /* BSD style: sigblock (sigmask (SIGPIPE)); */
  set_sigio_handler ();
#endif /* HAVE_SIGNALS */
  interrupt_handler = client_interrupt_handler;
  client_retry_period = params_->client_retry_period;
     
  host.sin_family = AF_INET;
  host.sin_port = htons (params_->server_port);
  
  if (!strlen (params_->host_name))
    host.sin_addr.s_addr = htonl (INADDR_ANY);
  else
    {
      struct hostent *hostinfo = gethostbyname (params_->host_name);
      if (hostinfo == NULL)
	{
	  ERROR_ ("Unknown host %s.\n", params_->host_name);
	  return (EXIT_FAILURE);
	}
      host.sin_addr = *(struct in_addr *) hostinfo->h_addr;
    }

  /* Create the socket. */
  if (0 > (sock = socket (PF_INET, SOCK_STREAM, 0)))
    {
      ERROR_ ("Failed to create socket.\n");
      return (EXIT_FAILURE);
    }
#ifdef HAVE_FCNTL
  fcntl (sock, F_SETOWN, getpid ());
#endif /* HAVE_FCNTL */
    
  fprintf (logfd, "Try to connect to the server.\r");
  fflush (logfd);
  for (;;)
    {
      /* Connect to the server. */
      if (0 > connect (sock, (struct sockaddr *)&host, sizeof (host)))
	{
	  if (client_retry_period > 0)
	    {
	      fprintf (logfd, "Attempt %d connect to the server failed."
		       " Retry after %d sec.\r",
		       ++connection_attempt, client_retry_period);
	      fflush (logfd);
	      my_sleep (client_retry_period);
	      continue;
	    }
	  fprintf (logfd, "Failed connect to the server. Exiting.\n");
	  fflush (logfd);
	  return (EXIT_FAILURE);
	}
      
      fprintf (logfd, "\nClient: connect to host %s, port %hd.\n",
	       inet_ntoa (host.sin_addr), ntohs (host.sin_port));
      fflush (logfd);

      if (EXIT_SUCCESS == check_server_version (sock))
	for (;;)
	  {
	    while (time_to_sleep (params_->start_m, params_->stop_m))
	      if (client_retry_period > 0)
		my_sleep (client_retry_period);
	      else
		break;
	    if (EXIT_SUCCESS != do_1_task (sock))
	      break;
	  }
      
      shutdown (sock, SD_BOTH); /* Close the socket */
      closesocket (sock);

      /* if client is persistent it should sleep a while and do
	 not reconnect immediately. If JOB_END message was received
	 immediate reconnection will be undersirable */
      if (client_retry_period > 0)
	my_sleep (client_retry_period);
      else
	break;

      /* Create the new socket. */
      if (0 > (sock = socket (PF_INET, SOCK_STREAM, 0)))
	{
	  ERROR_ ("Failed to create socket.\n");
	  return (EXIT_FAILURE);
	}
#ifdef HAVE_FCNTL
      fcntl (sock, F_SETOWN, getpid ());
#endif /* HAVE_FCNTL */
      
      fprintf (logfd, "Try to reconnect to the server.\r");
    }

  return (EXIT_SUCCESS);
}
