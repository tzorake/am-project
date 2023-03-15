/* -*- C -*- */
/* I hate this bloody country. Smash. */
/* This file is part of INFINITE PLATE OSCILLATIONS project */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <math.h>
#include <ctype.h>
#include <getopt.h>
#if defined(__CYGWIN32__) || defined(__MINGW32__)
#include <windows.h> /* for SetPriorityClass */
#ifdef __MINGW32__
#include <winsock2.h>
#endif /* __MINGW32__ */
#else /* ! (defined(__CYGWIN32__) || defined(__MINGW32__)) */
#include <unistd.h>
#include <sys/resource.h>
#endif /* defined(__CYGWIN32__) || defined(__MINGW32__) */

#include <cone.h>
#include <hsa.h>
#include <cs.h>

enum {
  PARAMETER_NICE = 1,
  PARAMETER_DT,
  PARAMETER_STOP,
  PARAMETER_OD,
  PARAMETER_E1PSILON,
  PARAMETER_E2PSILON,
 PARAMETER_E3PSILON,
 PARAMETER_CAPPA,
 PARAMETER_SK_GR,
 PARAMETER_PX,
 PARAMETER_LYMBDA,
 PARAMETER_P0_0,
 PARAMETER_P0_1,
 PARAMETER_P1_0,
 PARAMETER_P1_1,
 PARAMETER_N,
  PARAMETER_AMPLITUDE,
  PARAMETER_NU,
  PARAMETER_A0_0,
  PARAMETER_A0_1,
  PARAMETER_A0_UP,
  PARAMETER_A0_STEP,
  PARAMETER_OMEGA0,
  PARAMETER_OMEGA1,
  PARAMETER_OMEGA2,
  PARAMETER_OMEGA0_UP,
  PARAMETER_OMEGA0_STEP,
  PARAMETER_WITH,
  PARAMETER_TO,
  PARAMETER_KLUCH,
  PARAMETER_KK,
  PARAMETER_KLEQ,
  PARAMETER_HK,

  HSA_ST,
  HSA_FT,
  CLIENT_RETRY_PERIOD,  
  CLIENT_START_TIME,  
  CLIENT_STOP_TIME,  

};

static char * methods_names[NUM_METHODS] =
{
  [RK2] = "rk2",
  [RK4] = "rk4",
  [RKF45] = "rkf45",
  [RKCK] = "rkck",
  [RK8PD] = "rk8pd",
  [RK2IMP] = "rk2imp",
  [RK4IMP] = "rk4imp",
  [GEAR1] = "gear1",
  [GEAR2] = "gear2",
};

FILE * logfd = NULL;

static boolean_t server_flag = FALSE;
static boolean_t option_c = FALSE;
static boolean_t help_flag = FALSE;
static int nice_val = 0;
static char * option_file = NULL;
static char * log_file = NULL;
static parameters_t params =
{
  .method = RK4,
  .output_divider = 1,
  .stop_time = 178,
  .dt = 0.00390625,
  .e1psilon = 0,
  .e2psilon = 0,
  .e3psilon = 0,
  .cappa = 0,
  .sk_gr = 0,
  .lymbda = 10,
  .p0_0 = 0.,
  .p0_1 = 130.,
  .p1_0 = 0.,
  .p1_1 = 130.,
  .px = 0,
  .n = 20,
  .nu = 0.3,
  .amplitude = 0,
  .a0_0 = 0.,
  .a0_1 = 0.,
  .a0_up = 50.,
  .a0_step = 0.01,
  .omega0 = 3.,
  .omega1 = 3.,
  .omega2 = 3.,
  .omega0_up = 9.,
  .omega0_step = 0.01,
  .with = 1.,
  .to = 1.,
  .kluch = 0,
  .kk = 10,
  .kleq = 30,
  .hk = 0,
  .sp_flag = FALSE,
  .hsa_flag = FALSE,
  .max_flag = FALSE,
  .tm_u_flag = FALSE,
  .tm_w_flag = FALSE,
  .hsa_start_time = 50,
  .hsa_filename_template = "",
  .output_file = "",
  .host_name = "localhost",
  .server_port = DEFAULT_PORT,
  .client_retry_period = 1,
  .start_m = 0,
  .stop_m = 0,
  .restart_server_flag = FALSE,
};

static void
usage (char *progname)
{
  fprintf (stderr, "Infinite Plate Oscillations Runge-Kutt v" VERSION "\n");
}

static void
get_options (int argc, char **argv)
{
  /* `getopt_long' stores the option index here. */
  int option_index = 0;
  int c;
  
  static struct option long_options[] =
  {
    /* These options set a flag. */
    {"help",      0, (int*)&help_flag,   TRUE},
    {"server",    0, (int*)&server_flag, TRUE},
    {"restart",   0, (int*)&params.restart_server_flag, TRUE},
    {"options",   1, 0, '@'},
    {"host",      1, 0, 'h'},
    {"port",      1, 0, 'p'},
    {"method",    1, 0, 'm'},
    {"file",      1, 0, 'o'},
    {"log",       1, 0, 'l'},
    {"nice",      1, 0, PARAMETER_NICE},
    {"dt",        1, 0, PARAMETER_DT},
    {"stop",      1, 0, PARAMETER_STOP},
    {"out_div",   1, 0, PARAMETER_OD},
    {"e1psilon",         1, 0, PARAMETER_E1PSILON},
    {"e2psilon",         1, 0, PARAMETER_E2PSILON},
    {"e3psilon",         1, 0, PARAMETER_E3PSILON},
    {"cappa",         1, 0, PARAMETER_CAPPA},
    {"sk_gr",         1, 0, PARAMETER_SK_GR},
    {"px",         1, 0, PARAMETER_PX},
    {"lymbda",         1, 0, PARAMETER_LYMBDA},
    {"p0_0",         1, 0, PARAMETER_P0_0},
    {"p0_1",         1, 0, PARAMETER_P0_1},
    {"p1_0",         1, 0, PARAMETER_P1_0},
    {"p1_1",         1, 0, PARAMETER_P1_1},
    {"n",         1, 0, PARAMETER_N},
    {"amplitude", 1, 0, PARAMETER_AMPLITUDE},
    {"nu",        1, 0, PARAMETER_NU},
    {"a0_0",      1, 0, PARAMETER_A0_0},
    {"a0_1",      1, 0, PARAMETER_A0_1},
    {"a0_up",     1, 0, PARAMETER_A0_UP},
    {"a0_step",   1, 0, PARAMETER_A0_STEP},
    {"omega0",    1, 0, PARAMETER_OMEGA0},
    {"omega1",    1, 0, PARAMETER_OMEGA1},
    {"omega2",    1, 0, PARAMETER_OMEGA2},
    {"omega0_up",    1, 0, PARAMETER_OMEGA0_UP},
    {"omega0_step",  1, 0, PARAMETER_OMEGA0_STEP},
    {"with", 1, 0, PARAMETER_WITH},
    {"to", 1, 0, PARAMETER_TO},
    {"kluch",  1, 0, PARAMETER_KLUCH},    
    {"kk",  1, 0, PARAMETER_KK},    
    {"kleq",  1, 0, PARAMETER_KLEQ},    
    {"hk",  1, 0, PARAMETER_HK},    

    {"sp",  0, (int*)&params.sp_flag, TRUE},
    {"hsa",       0, (int*)&params.hsa_flag, TRUE},
    {"tm_u",       0, (int*)&params.tm_u_flag, TRUE},
    {"tm_w",       0, (int*)&params.tm_w_flag, TRUE},
    {"max",       0, (int*)&params.max_flag, TRUE},
    {"hsa_st",    1, 0, HSA_ST},
    {"hsa_ft",    1, 0, HSA_FT},
    {"crp",       1, 0, CLIENT_RETRY_PERIOD},
    {"cstart",    1, 0, CLIENT_START_TIME},
    {"cstop",     1, 0, CLIENT_STOP_TIME},

    {0, 0, 0, 0}
  };
  
  optind = 1;
  while ( (c = getopt_long (argc, argv, "scro:l:m:@:h:p:",
          long_options, &option_index)) != -1 )
    {
      switch (c)
  {
  case 0:
    break;
  case '?':
    fprintf (stderr, "Error : can't read argument\n");
    break;
  case 's':
    server_flag = TRUE;
    break;
  case 'c':
    option_c = TRUE;
    break;
  case 'r':
    params.restart_server_flag = TRUE;
    break;
  case 'm':
    {
      int i;
      for (i = 0; i < NUM_METHODS; ++i)
        if (methods_names[i] && (!strcasecmp (optarg, methods_names[i])))
    break;
      if (i < NUM_METHODS)
        params.method = i;
      else
        fprintf (stderr, "Unknown method `%s'\n", optarg);
    }
    break;
  case 'o':
    memcpy (params.output_file, optarg,
      MIN(sizeof (params.output_file), strlen (optarg) + 1));
    break;
  case 'l':
    log_file = strdup (optarg);
    break;
  case '@':
    option_file = strdup (optarg);
    break;
  case 'h':
    memcpy (params.host_name, optarg,
      MIN(sizeof (params.host_name), strlen (optarg) + 1));
    break;
  case 'p':
    if (1 != sscanf (optarg, "%d", &params.server_port))
      fprintf (stderr, "Can't read server port value\n");
    break;
  case PARAMETER_NICE:
    if (1 != sscanf (optarg, "%d", &nice_val))
      fprintf (stderr, "Can't read nice value\n");
    break;
  case PARAMETER_DT:
    if (1 != sscanf (optarg, "%lg", &params.dt))
      fprintf (stderr, "Can't read time step\n");
    break;
  case PARAMETER_STOP:
    if (1 != sscanf (optarg, "%lg", &params.stop_time))
      fprintf (stderr, "Can't read stop time\n");
    break;
  case PARAMETER_OD:
    if (1 != sscanf (optarg, "%d", &params.output_divider))
      fprintf (stderr, "Can't read output divider\n");
    break;
  case PARAMETER_E1PSILON:
    if (1 != sscanf (optarg, "%lg", &params.e1psilon))
      fprintf (stderr, "Can't read e1psilon\n");
    break;
  case PARAMETER_E2PSILON:
    if (1 != sscanf (optarg, "%lg", &params.e2psilon))
      fprintf (stderr, "Can't read e2psilon\n");
    break;
  case PARAMETER_E3PSILON:
    if (1 != sscanf (optarg, "%lg", &params.e3psilon))
      fprintf (stderr, "Can't read e3psilon\n");
    break;
  case PARAMETER_CAPPA:
    if (1 != sscanf (optarg, "%lg", &params.cappa))
      fprintf (stderr, "Can't read cappa\n");
    break;
  case PARAMETER_SK_GR:
    if (1 != sscanf (optarg, "%lg", &params.sk_gr))
      fprintf (stderr, "Can't read sk_gr\n");
    break;
  case PARAMETER_PX:
    if (1 != sscanf (optarg, "%lg", &params.px))
      fprintf (stderr, "Can't read px\n");
    break;
  case PARAMETER_LYMBDA:
    if (1 != sscanf (optarg, "%d", &params.lymbda))
      fprintf (stderr, "Can't read lymbda\n");
    break;
  case PARAMETER_P0_0:
    if (1 != sscanf (optarg, "%lg", &params.p0_0))
      fprintf (stderr, "Can't read p0_0\n");
    break;
  case PARAMETER_P0_1:
    if (1 != sscanf (optarg, "%lg", &params.p0_1))
      fprintf (stderr, "Can't read p0_1\n");
    break;
  case PARAMETER_P1_0:
    if (1 != sscanf (optarg, "%lg", &params.p1_0))
      fprintf (stderr, "Can't read p1_0\n");
    break;
  case PARAMETER_P1_1:
    if (1 != sscanf (optarg, "%lg", &params.p1_1))
      fprintf (stderr, "Can't read p1_1\n");
    break;
  case PARAMETER_N:
    if (1 != sscanf (optarg, "%d", &params.n))
      fprintf (stderr, "Can't read n\n");
    break;
  case PARAMETER_AMPLITUDE:
    if (1 != sscanf (optarg, "%lg", &params.amplitude))
      fprintf (stderr, "Can't read amplitude\n");
    break;
  case PARAMETER_NU:
    if (1 != sscanf (optarg, "%lg", &params.nu))
      fprintf (stderr, "Can't read nu\n");
    break;
  case PARAMETER_A0_0:
    if (1 != sscanf (optarg, "%lg", &params.a0_0))
      fprintf (stderr, "Can't read a0_0\n");
    break;
  case PARAMETER_A0_1:
    if (1 != sscanf (optarg, "%lg", &params.a0_1))
      fprintf (stderr, "Can't read a0_1\n");
    break;
  case PARAMETER_A0_UP:
    if (1 != sscanf (optarg, "%lg", &params.a0_up))
      fprintf (stderr, "Can't read a0_up\n");
    break;
  case PARAMETER_A0_STEP:
    if (1 != sscanf (optarg, "%lg", &params.a0_step))
      fprintf (stderr, "Can't read a0_step\n");
    break;
  case PARAMETER_OMEGA0:
    if (1 != sscanf (optarg, "%lg", &params.omega0))
      fprintf (stderr, "Can't read omega0\n");
    break;
  case PARAMETER_OMEGA1:
    if (1 != sscanf (optarg, "%lg", &params.omega1))
      fprintf (stderr, "Can't read omega1\n");
    break;
  case PARAMETER_OMEGA2:
    if (1 != sscanf (optarg, "%lg", &params.omega2))
      fprintf (stderr, "Can't read omega2\n");
    break;
  case PARAMETER_OMEGA0_UP:
    if (1 != sscanf (optarg, "%lg", &params.omega0_up))
      fprintf (stderr, "Can't read omega0_up\n");
    break;
  case PARAMETER_OMEGA0_STEP:
    if (1 != sscanf (optarg, "%lg", &params.omega0_step))
      fprintf (stderr, "Can't read omega0_step\n");
    break;
        case PARAMETER_WITH:
	  if (1 != sscanf (optarg, "%lg", &params.with))
	   fprintf (stderr, "Can't read with\n");
	  break;
        case PARAMETER_TO:
	  if (1 != sscanf (optarg, "%lg", &params.to))
	   fprintf (stderr, "Can't read to\n");
	  break;
  case PARAMETER_KLUCH:
    if (1 != sscanf (optarg, "%d", &params.kluch))
      fprintf (stderr, "Can't read kluch\n");
    break;
  case PARAMETER_KK:
    if (1 != sscanf (optarg, "%lg", &params.kk))
      fprintf (stderr, "Can't read kk\n");
    break;
  case PARAMETER_KLEQ:
    if (1 != sscanf (optarg, "%lg", &params.kleq))
      fprintf (stderr, "Can't read kleq\n");
    break;
  case PARAMETER_HK:
    if (1 != sscanf (optarg, "%lg", &params.hk))
      fprintf (stderr, "Can't read hk\n");
    break;


  case HSA_ST:
    if (1 != sscanf (optarg, "%lg", &params.hsa_start_time))
      fprintf (stderr, "Can't read hsa start time\n");
    break;
  case HSA_FT:
    memcpy (params.hsa_filename_template, optarg,
      MIN (sizeof (params.hsa_filename_template),
           strlen (optarg) + 1));
    break;

  case CLIENT_RETRY_PERIOD:
    if (1 != sscanf (optarg, "%d", &params.client_retry_period))
      fprintf (stderr, "Can't read client retry period\n");
    break;
  case CLIENT_START_TIME:
    {
      int hours, minutes;
      if (2 != sscanf (optarg, "%d:%d", &hours, &minutes))
        fprintf (stderr, "Can't read client start time\n");
      else
        params.start_m = hours * 60 + minutes;
    }
    break;
  case CLIENT_STOP_TIME:
    {
      int hours, minutes;
      if (2 != sscanf (optarg, "%d:%d", &hours, &minutes))
        fprintf (stderr, "Can't read client start time\n");
      else
        params.stop_m = hours * 60 + minutes;
    }
    
  default:
    fprintf (stderr, "getopt_long failed and returned %d\n", (int)c);
  }
    }
  
  if (optind < argc)
    {
      fprintf (stderr, "Optional parameters :\n");
      while (optind < argc)
  fprintf (stderr, "`%s'\n", argv[optind++]);
    }
}

#define STRING_SIZE (1024)

static void
read_options_from_file (char * filename)
{
  FILE * fd = NULL;

  if (strcmp(filename, "-"))
    fd = fopen (filename, "r");
  else
    fd = stdin;
  
  if (fd)
    {
      int argc = 1;
      char **argv = NULL;

      argv = (char**) malloc (2 * sizeof (char*));
      argv[0] = NULL; /* program name */
      argv[1] = NULL; /* paranoia */

      while (!feof(fd))
  {
    char str[STRING_SIZE];

    if (fgets (str, STRING_SIZE, fd))
      {
        char c;
        char * start, * stop;

        /* \0 - is not white space */
        for (start = str; isspace (*start); ++start);
        
        if (*start != '#') /* shell style comment */
    for (;;)
      {
        for (stop = start; *stop && !isspace (*stop); ++stop);
        c = * stop; /* save char */
        *stop = 0; /* make end of string */
        if (strlen (start)) /* if option exists add it to a list */
          {
      ++argc;
      argv =
        (char**) realloc (argv, (argc + 1) * sizeof(char*));
      argv[argc - 1] = strdup (start);
      argv[argc] = NULL; /* paranoia */
          }
        
        if (!c) /* break if it was end of line */
          break;
        for (start = stop + 1; isspace (*start); ++start);
      }
      }
  }
      fclose (fd);
      get_options (argc, argv);
      while (--argc > 0)
  free (argv[argc]);
      free (argv);
    }
  else
    fprintf (stderr, "Can't open options file\n");
}

int
main (int argc, char **argv)
{
  int status;
#ifdef __MINGW32__
  WSADATA data;
  WSAStartup (MAKEWORD(2,0), &data);
#endif /* __MINGW32__ */
  
  get_options (argc, argv);
  
  if (option_file)
    read_options_from_file (option_file);
      
  if (help_flag)
    {
      usage (argv[0]);
      return EXIT_SUCCESS;
    }
  
  /* set specified priority */
#ifdef HAVE_SETPRIORITY
  setpriority (PRIO_PROCESS, 0, nice_val);
#elif defined (HAVE_SETPRIORITYCLASS)
  SetPriorityClass (GetCurrentProcess (), nice_val);
#endif /* HAVE_SETPRIORITY */

  if (log_file)
    logfd = fopen (log_file, "a");
  if (!logfd)
    logfd = stderr;
  
  fprintf (logfd,
     "Use method %s\n"
     "time step : %g, stop time : %g\n"
     "w0 amplitude : %g, a0_0 : %g, a0_1 : %g, omega0 : %g\n"
     "epsilon : %g, nu : %g\n"
     "kk : %lg, kleq : %lg\n",

     methods_names[params.method],
     params.dt, params.stop_time,
     params.amplitude, params.a0_0, params.a0_1, params.omega0,
     params.e1psilon, params.nu,
     params.kk, params.kleq);

  fflush (logfd);
  if (server_flag)
    {
      if (option_c)
  status = server_collect (&params);
      else
  status = run_server (&params);
    }
  else
    {
      if (option_c)
  status = run_client (&params);
      else
  status = run_method (&params);
    }

#ifdef __MINGW32__
  WSACleanup ();
#endif /* __MINGW32__ */

  fclose (logfd);
  return status;
}
