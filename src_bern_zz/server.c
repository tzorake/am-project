/* -*- C -*- */
/* I hate this bloody country. Smash. */
/* This file is part of INFINITE PLATE OSCILLATIONS project */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
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

typedef struct {
  int size; /* size to read/write */
  char * ptr; /* curent position in buffer */
  msg_header_t * msg; /* beginning of buffer */
} pending_t;

typedef struct {
  int fd;
  pending_t snd_pen; /* writing pending */
  pending_t rcv_pen; /* reading pending */
  parameters_t * params; /* scheduled task */
} client_t;

typedef struct _plist plist_t;
struct _plist {
  parameters_t * params;
  plist_t * next;
};

typedef struct {
  double val;
  int size;
  long int fpos;
} log_des_t;

typedef struct {
  int cnt;
  log_des_t des[0];
} darray_t;

typedef int (*msg_handler_t) (int fd);

#define RELATIVE_EPS (0.0001)
#define PENDING_QUEUE_SIZE    (5)
#define MAXMSG_SIZE  4096

static volatile sig_atomic_t termination_flag = FALSE;
static FILE * output_fd = NULL;
static int tasks_in_progress = 0;
static plist_t * pending_tasks_queue = NULL;
static parameters_t params;
static int num_clients = 0;
static client_t clients[FD_SETSIZE];
static msg_handler_t msg_handlers[NUM_CMD] =
{
  [0 ... NUM_CMD - 1] = NULL
};

#ifdef HAVE_LIBRESLIB
#define RL_MAKE_DESCRIPTORS
#include <resource.h>
#endif /* HAVE_LIBRESLIB */

static void
print_time (void)
{
  time_t curtime;
  struct tm * loctime;
  
  /* Get the current time. */
  curtime = time (NULL);
  /* Convert it to local time representation. */
  loctime = localtime (&curtime);
  fprintf (logfd, "Local time: %s", asctime (loctime));
  fflush (logfd);
}

static void
change_params_for_1_client (parameters_t * params_)
{
  params_->a0_step = 0;
}

static int
send_to_client (int cid, cmd_t cmd, int size, int8_t data[])
{
  msg_header_t msg_h;
  int write_size;
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }
  
  if (clients[cid].snd_pen.size > 0)
    {
      ERROR_ ("Error in send_to_client:"
	      " sending already in progress for client %d.\n", clients[cid].fd);
      return -1;
    }
  
  msg_h.sig = MSG_SIGNATURE;
  msg_h.size = size + sizeof (msg_header_t);
  msg_h.cmd = cmd;

  if ((int)sizeof (msg_h) >
      send (clients[cid].fd, (const char*)&msg_h, sizeof (msg_h), 0))
    {
      ERROR_ ("Failed to write message header to sockect"
	      " for client %d.\n", clients[cid].fd);
      return -1;
    }

  /* Zero length messages */
  if (size <= 0)
    return size;

  /* start message body transmition */
  if (0 > (write_size = send (clients[cid].fd, (const char *)data, size, 0)))
    {
      ERROR_ ("Failed to write message to sockect for client %d."
	      " For command : %d.\n", clients[cid].fd, cmd);
      return -1;
    }

  clients[cid].snd_pen.msg = (msg_header_t*)data;
  clients[cid].snd_pen.ptr = data + write_size;
  clients[cid].snd_pen.size = size - write_size;

  return write_size;
}

static int
register_mh (cmd_t cmd, msg_handler_t mh)
{
  if (cmd >= NUM_CMD)
    {
      ERROR_ ("Trying register message handler"
	      " with wrong command code: %d.\n", cmd);
      return -1;
    }
  if (msg_handlers[cmd])
    fprintf (logfd, "Warrning: redefine message handler for command %d.\n",
	     cmd);
  fflush (logfd);
  msg_handlers[cmd] = mh;
  return 0;
}

/* message handler returning server information */
static int
mh_get_server_info (int cid)
{
  server_info_t info = {
    version: SERVER_VER_,
    tasks_in_progress: tasks_in_progress,
    current_params: params,
  };
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }

  if (clients[cid].rcv_pen.msg->size != sizeof (msg_header_t))
    {
      ERROR_ ("Wrong task request message size: %d (should be %d)"
	      " from client %d.\n",
	      clients[cid].rcv_pen.msg->size, sizeof (msg_header_t),
	      clients[cid].fd);
      return EXIT_FAILURE;
    }

  send_to_client (cid, SERVER_INFO, sizeof (server_info_t), (int8_t*)&info);
  clients[cid].snd_pen.msg = NULL; /* do not free data buffer after seding */
  
  return EXIT_SUCCESS;
}

/* Task request message handler */
static int
mh_task_req (int cid)
{
  parameters_t * task = NULL;
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }

  if (clients[cid].rcv_pen.msg->size != sizeof (msg_header_t))
    {
      ERROR_ ("Wrong task request message size: %d from client %d.\n",
	      clients[cid].rcv_pen.msg->size, clients[cid].fd);
      return EXIT_FAILURE;
    }

  /* set up new task from pending_tasks_queue or params */
  if (pending_tasks_queue)
    {
      plist_t * tmp = pending_tasks_queue;
      task = pending_tasks_queue->params;
      pending_tasks_queue = pending_tasks_queue->next;
      free (tmp);
    }
  else
    {
      if (params.a0_1 < params.a0_up)
	{
	  if (!(task = (parameters_t*)malloc (sizeof (parameters_t))))
	    {
	      ERROR_ ("Error: malloc() for new task failed."
		      " Shuting down client %d.\n", clients[cid].fd);
	    }
	  else
	    {
	      ++tasks_in_progress;
	      *task = params;
	      change_params_for_1_client (task);
	      params.a0_1 += params.a0_step;
	    }
	}
    }
  
  clients[cid].params = task;
  if (task)
    send_to_client (cid, TASK_TODO, sizeof (parameters_t), (int8_t*)task);
  else /* socket should closed but from here active_fd_set can't be accessed */
    {
      fprintf (logfd, "Send JOB_END to client %d.\n", clients[cid].fd);
      fflush (logfd);
      send_to_client (cid, JOB_END, 0, NULL);
    }
    
  clients[cid].snd_pen.msg = NULL; /* do not free data buffer after seding */
  return EXIT_SUCCESS;
}

/* getting task results */
static int
mh_task_res (int cid)
{
  --tasks_in_progress;
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }
  
  if (clients[cid].params)
    {
      fprintf (output_fd, STRUCT_TMPLT,
	       clients[cid].params->a0_1,
	       clients[cid].rcv_pen.msg->size - sizeof (msg_header_t));
      free (clients[cid].params);
      clients[cid].params = NULL;
    }
  else
    {
      ERROR_ ("Assert failed: (clients[cid].params != NULL)"
	      " for client %d.\n", clients[cid].fd);
      return EXIT_FAILURE;
    }
  
  fwrite (clients[cid].rcv_pen.msg->data,
	  1, clients[cid].rcv_pen.msg->size - sizeof (msg_header_t),
	  output_fd);
  fflush (output_fd);
  return EXIT_SUCCESS;
}

static int
msg_handler (int cid)
{
  int cmd = clients[cid].rcv_pen.msg->cmd;
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }
  
  if ((cmd < NUM_CMD) && msg_handlers[cmd])
    return msg_handlers[cmd] (cid);
  return -1;
}

int
read_from_client (int cid)
{
  pending_t * pend = &clients[cid].rcv_pen;
  char buffer[MAXMSG_SIZE];
  int msg_size;
  int size;
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }

  if (pend->size > 0)
    size = recv (clients[cid].fd, (char*)buffer,
		 MIN(pend->size, MAXMSG_SIZE), 0);
  else
    size = recv (clients[cid].fd, (char*)buffer, sizeof (msg_header_t), 0);
  
  if (size < 0)
    {
      /* Read error. */
      ERROR_ ("Failed to read from socket for client %d.\n", clients[cid].fd);
      return size;
    }
  else if (size == 0)
    return 0; /* End-of-file. */
  else
    {
      /* pending receiving in progress */
      if (pend->size > 0)
	{
	  /* maybe malloc failed so we need just to drop message */
	  pend->size -= size;
	  if (pend->ptr)
	    {
	      /* NB: size < pend->size guaranteed by read() 
		 if not - will be pend->msg buffer overflow */
	      memcpy (pend->ptr, buffer, size);
	      pend->ptr += size;
	      if (0 >= pend->size)
		{
		  msg_handler (cid);
		  free (pend->msg);
		}
	    }
	}
      else
	{
	  /* Check message header */
	  if (size < sizeof (msg_header_t))
	    {
	      ERROR_ ("Error: incoming message too small"
		      " (client %d).\n", clients[cid].fd);
	      return -size; /* force to close this connection */
	    }

	  if (((msg_header_t*)&buffer)->sig != MSG_SIGNATURE)
	    {
	      ERROR_ ("Wrong incoming message signature"
		      " (read 0x%08x should be 0x%08x) from client %d.\n",
		      ((msg_header_t*)&buffer)->sig, MSG_SIGNATURE,
		      clients[cid].fd);
	      return -size; /* force to close this connection */
	    }
	  
	  msg_size = ((msg_header_t*)&buffer)->size;
	  /* if some of further operations fail
	     this fields should be initialized */
	  pend->msg = (void*)pend->ptr = NULL;
	      
	  if (sizeof (msg_header_t) > msg_size)
	    {
	      ERROR_ ("Bad message size: %d from client %d.\n",
		      msg_size, clients[cid].fd);
	      return -size; /* force to close this connection */
	    }
	    
	  if (!(pend->msg = (msg_header_t*)malloc (msg_size)))
	    {
	      ERROR_ ("Failed to allocate memory for new message"
		      " from client %d.\n", clients[cid].fd);
	      return -size; /* force client to reconnect */
	    }

	  memcpy (pend->msg, buffer, size);
	  pend->ptr = ((char*)(pend->msg)) + size;
	  if (0 >= (pend->size = msg_size - size))
	    {
	      /* no pending receiving */
	      msg_handler (cid);
	      free (pend->msg);
	    }
	}
      return size;
    }
}

static void
set_fd_nonblock (int fd)
{
#ifdef HAVE_FCNTL
  int flags = fcntl (fd, F_GETFL, 0);
  if (0 > flags)
    ERROR_ ("Failed in fcntl for socket %d.\n", fd);
  else if (0 > fcntl (fd, F_SETFL, O_NONBLOCK | flags))
    ERROR_ ("Failed in fcntl for socket %d.\n", fd);
#else /* ! HAVE_FCNTL */
  ioctlsocket (fd, FIONBIO, NULL);
#endif /* HAVE_FCNTL */
}

static int
create_new_socket (int sock)
{
  /* Connection request on original socket. */
  int fd;
  struct sockaddr_in clientname;
  size_t size = sizeof (clientname);
		
  if (0 > (fd = accept (sock, (struct sockaddr *) &clientname, &size)))
    {
      ERROR_ ("Failed to create socket for new client.\n");
      return fd;
    }

  set_fd_nonblock (fd);
  memset (&clients[num_clients], 0, sizeof (client_t));
  clients[num_clients++].fd = fd;
		
  print_time ();
  fprintf (logfd,
	   "Server: connect from host %s, port %hd. Socket %d\n",
	   inet_ntoa (clientname.sin_addr), ntohs (clientname.sin_port), fd);
  fflush (logfd);

  return fd;
}

static int
shutdown_client (int cid)
{
  int status = EXIT_SUCCESS;
  
  if (cid >= num_clients)
    {
      ERROR_ ("Wrong client id: %d.\n", cid);
      return EXIT_FAILURE;
    }
  
  print_time ();
  fprintf (logfd, "Closing connection with socket %d.\n", clients[cid].fd);
  fflush (logfd);
  
  shutdown (clients[cid].fd, SD_BOTH);
  closesocket (clients[cid].fd);
  
  /* free pending buffers */
  if ((clients[cid].rcv_pen.size > 0) && clients[cid].rcv_pen.msg)
    free (clients[cid].rcv_pen.msg);
  if ((clients[cid].snd_pen.size > 0) && clients[cid].snd_pen.msg)
    free (clients[cid].snd_pen.msg);

  /* save client task to pending_tasks_queue */
  if (clients[cid].params)
    {
      plist_t * new = (plist_t*)malloc (sizeof (plist_t));
      if (new)
	{
	  new->next = pending_tasks_queue;
	  new->params = clients[cid].params;
	  pending_tasks_queue = new;
	}
      else
	{
	  ERROR_ ("malloc() for pending_tasks_queue failed"
		  " while shuting down client %d.\n"
		  "Task a0: %g is lost.\n",
		  clients[cid].fd, clients[cid].params->a0_1);
	  free (clients[cid].params);
	  --tasks_in_progress;
	  status = EXIT_FAILURE;
	}
    }
  clients[cid] = clients[--num_clients];
  return status;
}     

static int
server (int port)
{
  fd_set active_fd_set, read_fd_set, write_fd_set;
  int num_pending_operations = 0;
  struct sockaddr_in name;
  int sock;
  int i;

  /* Create the socket and set it up to accept connections. */
  if (0 > (sock = socket (PF_INET, SOCK_STREAM, 0)))
    {
      ERROR_ ("Failed to create socket: '%s'.\n", strerror (errno));
      return (EXIT_FAILURE);
    }
     
  /* Give the socket a name. */
  name.sin_family = AF_INET;
  name.sin_port = htons (port);
  name.sin_addr.s_addr = htonl (INADDR_ANY);

  if (0 > bind (sock, (struct sockaddr *) &name, sizeof (name)))
    {
      ERROR_ ("Failed to bind socket.\n");
      return (EXIT_FAILURE);
    }
  
  /* all operations should be nonblocking */
  set_fd_nonblock (sock);
  
  if (listen (sock, PENDING_QUEUE_SIZE) < 0)
    {
      ERROR_ ("Failed in listen.\n");
      return (EXIT_FAILURE);
    }
     
  /* Initialize the set of active sockets. */
  FD_ZERO (&active_fd_set);
  FD_SET (sock, &active_fd_set);

  num_clients = 0;
  memset (&clients[num_clients], 0, sizeof (client_t));
  clients[num_clients++].fd = sock;

  /* main loop */
  while (!termination_flag &&
	 ((tasks_in_progress > 0)
	  || (params.a0_1 < params.a0_up)
	  || (num_pending_operations > 0)))
    {
      read_fd_set = write_fd_set = active_fd_set;
      /* select active sockets with pending writing */
      for (i = 0; i < num_clients; ++i)
	if (FD_ISSET (clients[i].fd, &write_fd_set) &&
	    (clients[i].snd_pen.size <= 0))
	  FD_CLR (clients[i].fd, &write_fd_set);

      /* Block until input arrives on one or more active sockets. */
      if (0 > select (FD_SETSIZE, &read_fd_set, &write_fd_set, NULL, NULL))
	{
	  ERROR_ ("Failed in select.\n");
	  break;
	}
      
      /* Service all the sockets with input pending. */
      for (i = 0; i < num_clients; ++i)
	if (FD_ISSET (clients[i].fd, &read_fd_set))
	  {
	    if (clients[i].fd == sock)
	      {
		int new = create_new_socket (sock);
		/* argumet for FD_SET should be variable not function call */
		if (new > 0)
		  FD_SET (new, &active_fd_set);
	      }
	    else
	      {
		/* Data arriving on an already-connected socket. */
		if (0 >= read_from_client (i))
		  {
		    FD_CLR (clients[i].fd, &active_fd_set);
		    shutdown_client (i);
		  }
	      }
	  }
      
      /* do pending writing */
      for (i = 0; i < num_clients; ++i)
	if (FD_ISSET (clients[i].fd, &write_fd_set))
	  {
	    pending_t * pend = &clients[i].snd_pen;
	    int size = send (clients[i].fd, (const char *)pend->ptr,
			     pend->size, 0);
	    if (size > 0)
	      {
		pend->ptr += size;
		if ((0 >= (pend->size -= size)) && pend->msg)
		  free (pend->msg);
	      }
	    else
	      {
		ERROR_ ("Failed to write to socket: %d\n", clients[i].fd);
		pend->size = 0;
		if (pend->msg)
		  free (pend->msg);
	      }
	  }

      /* count number of pending operations */
      num_pending_operations = 0;
      for (i = 0; i < num_clients; ++i)
	if (FD_ISSET (clients[i].fd, &active_fd_set) &&
	    ((clients[i].snd_pen.size > 0) || (clients[i].rcv_pen.size > 0)))
	  ++num_pending_operations;
    }

  /* closing all sockets and shutting down clients */
  for (i = num_clients - 1; i >= 0; --i)
    if ((FD_ISSET (clients[i].fd, &active_fd_set)) && (clients[i].fd != sock))
      {
	fprintf (logfd, "Send JOB_END to client %d.\n", clients[i].fd);
	fflush (logfd);
	send_to_client (i, JOB_END, 0, NULL);
	shutdown_client (i);
      }

  /* all done - shutdown sock */
  shutdown (sock, SD_BOTH);
  closesocket (sock);
  
  --num_clients;
  return EXIT_SUCCESS;
}

/* server log file header save/restore functions */
static __inline__ int
save_data_as_hex_str (uint8_t * ptr, int size, FILE * fd)
{
  while (size--)
    if (0 > fprintf (fd, "0x%02x ", *ptr++))
      return EXIT_FAILURE;
  return EXIT_SUCCESS;
}

static __inline__ int
read_data_as_hex_str (uint8_t * ptr, int size, FILE * fd)
{
  int tmp;
  while (size--)
    if (1 == fscanf (fd, "0x%x ", &tmp))
      *ptr++ = tmp;
    else
      return EXIT_FAILURE;
  
  return EXIT_SUCCESS;
}

static void
save_params (FILE * fd, parameters_t * params_)
{
#ifdef HAVE_LIBRESLIB
  char * str = RL_SAVE_STRUCT (params_, parameters_t);
  if (str)
    {
      fprintf (fd, HEADER_TMPLT "%s", SERVER_VER_, strlen (str), str);
      free (str);
    }
  else ERROR_ ("failed in header saving\n");

#else /* HAVE_LIBRESLIB */

  fprintf (fd, HEADER_TMPLT, SERVER_VER_, sizeof (parameters_t));
  save_data_as_hex_str ((uint8_t*)params_, sizeof (parameters_t), fd);
  
#endif /* HAVE_LIBRESLIB */
}

static int
load_params (FILE * fd, parameters_t * params_, int size)
{
#ifdef HAVE_LIBRESLIB
  char * end;
  char * str = rl_read_object (fd);

  if (!str)
    {
      ERROR_ ("Failed to read header body.\n");
      return EXIT_FAILURE;
    }
  
  if (strlen (str) != size)
    ERROR_ ("Header body length mismatch.\n");

  end = RL_LOAD_STRUCT (params_, parameters_t, str);
  if (!end)
    {
      ERROR_ ("error in header.\n");
      free (str);
      return EXIT_FAILURE;
    }
  
  if (0 != strlen (end))
    {
      ERROR_ ("Part of header remained unparsed '%s'.\n", end);
      free (str);
      return EXIT_FAILURE;
    }
  free (str);

#else /* HAVE_LIBRESLIB */

  if (size != sizeof (parameters_t))
    {
      ERROR_ ("Server header size mismatch (read %d should be %d)\n",
	      size, sizeof (parameters_t));
      return EXIT_FAILURE;
    }

  if (EXIT_SUCCESS !=
      read_data_as_hex_str ((uint8_t*)params_, size, fd))
    {
      ERROR_ ("Failed to read header body.\n");
      return EXIT_FAILURE;
    }
#endif /* HAVE_LIBRESLIB */

  return EXIT_SUCCESS;
}

/* compare rounded value with precise */
static double
relative_deviation (double val, double base)
{
  if (base != 0)
    return ABS((val - base) / base);
  else
    return val;
}

/* read log file and set up new tasks list */
static int
read_server_log (parameters_t * params_,
		 int (*data_handler) (FILE*, darray_t*, parameters_t*))
{
  int status = EXIT_SUCCESS;
  parameters_t tmp_params;
  darray_t * des_list = NULL;
  FILE * in_fd;
  double a0;
  int ver;
  int size;

  if (strlen (params_->output_file) && strcmp ("-", params_->output_file))
    in_fd = fopen (params_->output_file, "rb");
  else
    {
      ERROR_ ("stdin can't be server log file.\n");
      return EXIT_FAILURE;
    }
  
  if (!in_fd)
    {
      fprintf (logfd, "Failed to open server log file `%s`.\n",
	       params_->output_file);
      fflush (logfd);
      return EXIT_FAILURE;
    }

  if (2 != fscanf (in_fd, HEADER_TMPLT, &ver, &size))
    {
      ERROR_ ("Failed to read header parameters"
	      " of server log file `%s`.\n", params_->output_file);
      fclose (in_fd);
      return EXIT_FAILURE;
    }

  if (ver != SERVER_VER_)
    {
      ERROR_ ("Server version mismatch (read 0x%08x should be 0x%08x)"
	      " for server log file `%s`.\n",
	      ver, SERVER_VER_, params_->output_file);
      fclose (in_fd);
      return EXIT_FAILURE;
    }

  if (EXIT_FAILURE == load_params (in_fd, &tmp_params, size))
    {
      ERROR_ ("Closing server log file '%s' and exiting.\n",
	      params_->output_file);
      fclose (in_fd);
      return EXIT_FAILURE;
    }

  if (!(des_list = (darray_t*)calloc (1, sizeof (darray_t))))
    {
      ERROR_ ("Malloc failed.\n");
      fclose (in_fd);
      return EXIT_FAILURE;
    }
  
  /* reading log file */
  while (!feof (in_fd)
	 && (2 == fscanf (in_fd, STRUCT_TMPLT, &a0, &size)))
    {
      darray_t * new;

      if (!(new = (darray_t*)realloc
	    (des_list,
	     sizeof (darray_t) + (des_list->cnt + 1) * sizeof (log_des_t))))
	{
	  ERROR_ ("Server restart: realloc failed.\n");
	  fclose (in_fd);
	  free (des_list);
	  return EXIT_FAILURE;
	}
      
      /* add task to done_list */
      des_list = new;
      des_list->des[des_list->cnt].val = a0;
      des_list->des[des_list->cnt].fpos = ftell (in_fd);
      des_list->des[des_list->cnt].size = size;
      ++des_list->cnt;

      /* skip the data */
      if (fseek (in_fd, size, SEEK_CUR))
	{
	  ERROR_ ("Server restart: fseek failed.\n");
	  fclose (in_fd);
	  free (des_list);
	  return EXIT_FAILURE;
	}
    }

  if (data_handler)
    status = data_handler (in_fd, des_list, &tmp_params);
  
  free (des_list);
  fclose (in_fd);

  /* fixup output_file name */
  strcpy (tmp_params.output_file, params_->output_file);
  *params_ = tmp_params;
  return status;
}

static int
append_notdone_tasks_to_pending_tasks_queue
(FILE * in_fd, darray_t * des_list, parameters_t * tmp_params)
{
  double a0, max_a0;
  
  /* add to pending_tasks_queue not done tasks */
  if (des_list->cnt > 0) /* if log was not empty */
    {
      int i;
      
      max_a0 = des_list->des[0].val;
      for (i = 1; i < des_list->cnt; ++i)
	if (des_list->des[i].val > max_a0)
	  max_a0 = des_list->des[i].val;
      
      for (a0 = tmp_params->a0_1; a0 <= max_a0; a0 += tmp_params->a0_step)
	{
	  /* search for this task in done_list */
	  for (i = 0; i < des_list->cnt; ++i)
	    if (relative_deviation (des_list->des[i].val, a0) < RELATIVE_EPS)
	      break;
      
	  /* task was not done */
	  if (i >= des_list->cnt)
	    {
	      plist_t * new = (plist_t*)malloc (sizeof (plist_t));
	      parameters_t * prm =
		(parameters_t*)malloc (sizeof (parameters_t));
	      if (new && prm)
		{
		  /* add this task to pending_tasks_queue */
		  ++tasks_in_progress;
		  *prm = *tmp_params;
		  change_params_for_1_client (prm);
		  prm->a0_1 = a0;
		  new->params = prm;
		  new->next = pending_tasks_queue;
		  pending_tasks_queue = new;
		}
	      else
		{
		  /* free all allocated memory */
		  if (new)
		    free (new);
		  if (prm)
		    free (prm);
		  while (pending_tasks_queue)
		    {
		      plist_t * tmp = pending_tasks_queue;
		      if (pending_tasks_queue->params)
			free (pending_tasks_queue->params);
		      pending_tasks_queue = pending_tasks_queue->next;
		      free (tmp);
		    }
		  ERROR_ ("Server restart: malloc failed.\n");
		  return EXIT_FAILURE;
		}
	    }
	}
      
      /* params should start from task next to max_a0 */
      if (relative_deviation (max_a0, a0) < RELATIVE_EPS)
	a0 += tmp_params->a0_step;
      tmp_params->a0_1 = a0;
    }

  fprintf (logfd, "Server restart from a0: %g number of pending tasks: %d\n",
	   tmp_params->a0_1, tasks_in_progress);
  fflush (logfd);
  
  return EXIT_SUCCESS;
}

static void
termination_handler (int signum)
{
  termination_flag = TRUE;
}
     
static void
set_termination_handler (void)
{
#ifdef HAVE_SIGACTION
  struct sigaction new_action, old_action;
     
  /* Set up the structure to specify the new action. */
  new_action.sa_handler = termination_handler;
  sigemptyset (&new_action.sa_mask);
  new_action.sa_flags = 0;
     
  sigaction (SIGINT, NULL, &old_action);
  if (old_action.sa_handler != SIG_IGN)
    sigaction (SIGINT, &new_action, NULL);
  sigaction (SIGHUP, NULL, &old_action);
  if (old_action.sa_handler != SIG_IGN)
    sigaction (SIGHUP, &new_action, NULL);
  sigaction (SIGTERM, NULL, &old_action);
  if (old_action.sa_handler != SIG_IGN)
    sigaction (SIGTERM, &new_action, NULL);
#else /* ! HAVE_SIGACTION */
  signal (SIGBREAK, termination_handler);
#endif /* HAVE_SIGACTION */
}

int
run_server (parameters_t * params_)
{
  int status;

#ifdef HAVE_LIBRESLIB
  RL_ADD_TYPE (RL_ENUM, boolean_t, "boolean type");
  RL_ADD_TYPE (RL_ENUM, method_t, "methods enum");
  RL_ADD_TYPE (RL_STRUCT, parameters_t, "parametrs struct");
#endif /* HAVE_LIBRESLIB */
  
  if (!params_->restart_server_flag
      || (EXIT_SUCCESS != read_server_log
	  (params_, append_notdone_tasks_to_pending_tasks_queue)))
    {
      if (strlen (params_->output_file) && strcmp ("-", params_->output_file))
	output_fd = fopen (params_->output_file, "wb");
      if (!output_fd)
	output_fd = stdout;

      save_params (output_fd, params_);
      fflush (output_fd);
    }
  else
    {
      /* open output_file for append */
      if (strlen (params_->output_file) && strcmp ("-", params_->output_file))
	output_fd = fopen (params_->output_file, "ab");
      if (!output_fd)
	output_fd = stdout;
    }

  params = *params_;
  if (params.a0_step <= 0)
    {
      fprintf (logfd, "a0_step for server should be more then 0.\n");
      fflush (logfd);
      return EXIT_FAILURE;
    }
  
  memset (clients, 0, sizeof (clients));
  memset (msg_handlers, 0, sizeof (msg_handlers));
  register_mh (TASK_REQ, mh_task_req);
  register_mh (TASK_RES, mh_task_res);
  register_mh (GET_SERVER_INFO, mh_get_server_info);

  print_time ();
  fprintf (logfd, "Start server version 0x%08x on port: %d\n",
	   SERVER_VER_, params.server_port);
  fflush (logfd);

  /* if one of the clients unexpectedly terminates
     server should ignore SIGPIPE */
#ifdef HAVE_SIGNALS
  blocksig (SIGPIPE); /* BSD style: sigblock (sigmask (SIGPIPE)); */
#endif /* HAVE_SIGNALS */
  set_termination_handler ();
  
  status = server (params.server_port);
  
  fclose (output_fd);
  if (termination_flag)
    fprintf (logfd, "SIGTERM received - exiting.\n");
  else if (EXIT_SUCCESS == status)
    fprintf (logfd, "All tasks completed.\n");
  fprintf (logfd, "Stop server.\n");
  fflush (logfd);
  
  return status;
}

static int
collect_data_from_log_file
(FILE * in_fd, darray_t * des_list, parameters_t * tmp_params)
{
  double a0, max_a0;
  
  /* add to pending_tasks_queue not done tasks */
  if (des_list->cnt > 0) /* if log was not empty */
    {
      int i;
      
      max_a0 = des_list->des[0].val;
      for (i = 1; i < des_list->cnt; ++i)
	if (des_list->des[i].val > max_a0)
	  max_a0 = des_list->des[i].val;

      for (a0 = tmp_params->a0_1; a0 <= max_a0; a0 += tmp_params->a0_step)
	{
	  char * data;
	  /* search for this task in done_list */
	  for (i = 0; i < des_list->cnt; ++i)
	    if (relative_deviation (des_list->des[i].val, a0) < RELATIVE_EPS)
	      break;
      
	  /* task was not done */
	  if (i >= des_list->cnt)
	    {
	      fprintf (logfd, "Warrning: not done task a0 = %g - exiting\n",
		       a0);
	      fflush (logfd);
	      break;
	    }
	  
	  if (0 > fseek (in_fd, des_list->des[i].fpos, SEEK_SET))
	    {
	      ERROR_ ("Failed in fseek"
		      " while reading server log file `%s`.\n",
		      tmp_params->output_file);
	      fclose (output_fd);
	      return EXIT_FAILURE;
	    }
	  
	  if (!(data = (char*)calloc (1, des_list->des[i].size)))
	    {
	      ERROR_ ("malloc failed.\n");
	      return EXIT_FAILURE;
	    }
	  
	  if (des_list->des[i].size >
	      fread (data, 1, des_list->des[i].size, in_fd))
	    {
	      free (data);
	      ERROR_ ("Failed in fread"
		      " while reading server log file `%s`.\n",
		      tmp_params->output_file);
	      fclose (output_fd);
	      return EXIT_FAILURE;
	    }
	  fwrite (data, 1, des_list->des[i].size, output_fd);
	  fputs ("\n", output_fd);
	  free (data);
	}
    }
  fclose (output_fd);
  
  return EXIT_SUCCESS;
}

int
server_collect (parameters_t * params_)
{
  char * output_file = (char*)calloc (1, strlen (params_->output_file) + 5);

  strcpy (output_file, params_->output_file);
  strcat (output_file, ".dat");
  
  fprintf (logfd, "Collecting server data from file `%s` into `%s`.\n",
	   params_->output_file, output_file);
  fflush (logfd);

  if (!(output_fd = fopen (output_file, "wb")))
    {
      fprintf (logfd, "Warrning: can't open file `%s` for output"
	       " - use stdout.\n", output_file);
      fflush (logfd);
      output_fd = stdout;
    }
  free (output_file);
  
#ifdef HAVE_LIBRESLIB
  RL_ADD_TYPE (RL_ENUM, boolean_t, "boolean type");
  RL_ADD_TYPE (RL_ENUM, method_t, "methods enum");
  RL_ADD_TYPE (RL_STRUCT, parameters_t, "parametrs struct");
#endif /* HAVE_LIBRESLIB */

  if (EXIT_FAILURE != read_server_log (params_, collect_data_from_log_file))
    return EXIT_FAILURE;
  fclose (output_fd);
  return EXIT_FAILURE;
}
