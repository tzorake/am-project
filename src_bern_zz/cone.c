/* -*- C -*- */
/* Балка Бернулли заделка оба конца */
/* This file is part of INFINITE PLATE OSCILLATIONS project */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <malloc.h>
#include <string.h>
#include <math.h>
#include <signal.h>
#include <time.h>
#include <sys/time.h>
#include <gsl/gsl_sys.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_math.h>
#include <gsl/gsl_odeiv.h>

#define INLINE inline



#include <cone.h>
#include <hsa.h>

#define ma1 (4*params.n)
#define ma2 (8*params.n)
#define m1 (params.n-1)        
#define m2 (2*(params.n-1))
#define m3 (3*(params.n-1))
#define m4 (4*(params.n-1))
#define m5 (5*(params.n-1))
#define c (1./params.n)
#define l (params.lymbda*params.lymbda)
#define c1 (1./(2*c))
#define c2 (1./(c*c))
#define c3 (1./(2*c*c*c))
#define c4 (1./(c*c*c*c))
#define L1 (1./params.lymbda)
#define L2 (1./(params.lymbda*params.lymbda))
#define c6 (1./(params.lymbda*params.lymbda*2*c*c*c))
#define c7 (1./(4*params.lymbda*params.lymbda*c*c*c*c))

#define SYS_DIMENSION (10*(params.n))
typedef double matrix_a [40];

volatile int (*interrupt_handler) (void) = NULL;
static FILE * output_fd = NULL;

/* Local variables */
static parameters_t params;
static double coef;
static double max_w;
double  period, maxt, Max = -1000;
matrix_a PSI;
static INLINE double sqr (double x) {return x * x;}

/* And here goes system definition */
/*-----------------------------------------------------------------*/

static INLINE double q (double t)
{
 return  params.a0_0*(2.0*rand()/(RAND_MAX+1.0)-1.0)+ params.a0_1;// * sin (params.omega0 * t);
}
static INLINE double px1 (double t)
{
 return  params.p0_0 + params.p0_1 * sin (params.omega1 * t);
}
static INLINE double px2 (double t)
{
 return params.p1_0 + params.p1_1 * sin (params.omega2 * t);
}

/* RHS */                               
static int
rhs (double t, const double w[], double w_rhs[], void *f)
{
  //уравнения
double w_1, w_2,  u_1, w1, w2, w4, u1, u2, kk, e, q_st, o, q_;

  //уравнения
int i;
w_1 = 0;
u_1 = 0;
w_2 =  w[0];

 
 for (i=0; i < params.n-1; i++)
  {
   if (i==0) 
    {
     w2 = w[i+1] - 2 * w[i] + w_1;
     w1 = w[i+1] - w_1;
     u1 = w[2*(params.n-1)+i+1] - u_1;
     u2 = w[2*(params.n-1)+i+1] - 2*w[2*(params.n-1)+i] + u_1;
     w4 = w[i+2] - 4 * w[i+1] + 6 * w[i] - 4 * w_1 + w_2;
    }

   if (i==params.n-2)
    {
     w2 = - 2 * w[i] + w[i-1];
     w1 = - w[i-1];
     u1 = - w[2*(params.n-1)+i-1];
     u2 = - 2*w[2*(params.n-1)+i] + w[2*(params.n-1)+i-1];
     w4 = w[i] + 6 * w[i] - 4 * w[i-1] + w[i-2];
    }

   if (i==1)
    {
      w2 = w[i+1] - 2 * w[i] + w[i-1];
      w1 = w[i+1] - w[i-1];
      u1 = w[2*(params.n-1)+i+1] - w[2*(params.n-1)+i-1];
      u2 = w[2*(params.n-1)+i+1] - 2*w[2*(params.n-1)+i] + w[2*(params.n-1)+i-1];
      w4 = w[i+2] - 4 * w[i+1] + 6 * w[i] - 4 * w[i-1] + w_1;

    }

   if (i==params.n-3)
    {
      w2 = w[i+1] - 2 * w[i] + w[i-1];
      w1 = w[i+1] - w[i-1];
      u1 = w[2*(params.n-1)+i+1] - w[2*(params.n-1)+i-1];
      u2 = w[2*(params.n-1)+i+1] - 2*w[2*(params.n-1)+i] + w[2*(params.n-1)+i-1];
      w4 =  - 4 * w[i+1] + 6 * w[i] - 4 * w[i-1] + w[i-2];
    }
  if (i!=0 && i!=1 && i!= params.n-2 && i!=params.n-3)
   {
    w2 = w[i+1] - 2 * w[i] + w[i-1];
    w1 = w[i+1] - w[i-1];
    u1 = w[2*(params.n-1)+i+1] - w[2*(params.n-1)+i-1];
    u2 = w[2*(params.n-1)+i+1] - 2*w[2*(params.n-1)+i] + w[2*(params.n-1)+i-1];
    w4 = w[i+2] - 4 * w[i+1] + 6 * w[i] - 4 * w[i-1] + w[i-2];
   }

//  if (params.with <= i && params.to >= i) q_ = q(t);
//	else q_ = 0;

   w_rhs[i] = w[i+(params.n-1)];
   w_rhs[i+2*(params.n-1)] = w[i+3*(params.n-1)];
   w_rhs[i+(params.n-1)] = ((-1./12) * c4 * w4 + w1 * c1 * ( c2 * u2 + c1 * c2 * w1 * w2)
                        + w2 * c2 * ( u1 * c1 + (3./2) * w1 * w1 * c1 * c1) 
                        + q(t))*L2 + px1(t) * w2  - params.e1psilon * w[i+(params.n-1)] /*-params.kk*
				(w[i]-w[i+4*(params.n-1)]-params.hk) * PSI[i-4*(params.n-1)]*/ ;     
				                                                                                        

   w_rhs[i+3*(params.n-1)] = c2 * u2 + c3 * w1 * w2 - params.e2psilon * w[i+3*(params.n-1)];

  }


	


     return GSL_SUCCESS;
}

static INLINE void
init_values (double w[])
{
  //начальные условия
  int i;
  memset (w, 0, SYS_DIMENSION * sizeof (double));
  max_w = 0;

for (i=0; i<= ( params.n-1); i++)
{
 w[i]=0; 
 w[i+(params.n-1)]=0; 
 w[i+2*(params.n-1)]=0; 
 w[i+3*(params.n-1)]=0; 
 w[i+4*(params.n-1)]=0; 
 w[i+5*(params.n-1)]=0; 
 
}

  if (params.sp_flag)
         {
           period =  2 * M_PI / params.omega0;
           params.dt = period / (long)(period / params.dt);
         }

}

   double drob (double x)
 {
  return x - (long)(x);
 } 
  
static INLINE void
on_step (double t, const double w[])
{
  static int nr = 0;
  double val = 0;
  double val1 = 0;
  double valu = 0;
  double valu1=0;
  double valexx=0;
  static double w2 = 0;
  int i;

  
  
  //val - сигнал
  int nn = (params.n) * 0.5;
  int uu = (5*params.n) * 0.5 + 3;
  int nn_ = (params.n) * 0.5+params.n-1;
  int uu_ = (5*params.n) * 0.5 + 3 + params.n-1;
  
  val1 = w[nn] ;
  valu = w[uu];

  if (params.kluch == 0) val = val1;
  if (params.kluch == 1) val = valu;  

//   w[nexx];

    /* если kluch = 0 то спектр считается  для w, kluch=1 то для u, kluch = 2 то для exx*/
     
 if(params.kluch == 1)  val = valu;
       else if(params.kluch == 2) val = valexx;

  
  if ((t > params.hsa_start_time) && (fabs (val) > max_w))
    max_w = fabs (val);

  if (t == 0)
    nr = 0;
  if ((nr++ % params.output_divider) != 0)
    return;

  if (params.hsa_flag)
    hsa_read_data (t, val, params.hsa_start_time);

    else
//   подсчет отображения Пуанкаре

    if (params.sp_flag)
     {
      if (t <= params.hsa_start_time + period)
        {
          if ( Max < val )
            {
             Max = val;
             maxt = t;
            }
        }
       else
        {
          double K =  (t - maxt) / period;

          if  ( drob(K) < 0.0001  || (1-drob(K)) < 0.0001)
           {
            if(w2 != 0) fprintf (output_fd, "%g %g\n", w2, val);
            w2 = val;
           }

         }

       }
  

//  конец



  else  if(t >= params.hsa_start_time)  /*вывод результата после отсечки*/

  if(params.tm_w_flag)
   {
         if (t > params.hsa_start_time) 
              {

		
                    		 fprintf(output_fd, "0 ");

               			 for(i = 0; i <= params.n-2; i++) 
                     

                    		fprintf(output_fd, "%g   ",  w[i]);
                            
                   
                    		 fprintf(output_fd, "0");

                    		 fprintf(output_fd, "\n");
    
	      }

    }
	else

  if(params.tm_u_flag)
      {
         if (t > params.hsa_start_time) 
            	{

		
                    		 fprintf(output_fd, "0 ");

               			 for(i = 0; i <= params.n-2; i++) 
                     

                    		fprintf(output_fd, "%g   ",  w[2*params.n+i]);
                            
                   
                    		 fprintf(output_fd, "0");

                    		 fprintf(output_fd, "\n");
    
         	}




   }

  else
    fprintf (output_fd, "%g %g %g %g %g\n", t, val1, w[nn_], valu, w[uu_]);
 
  fflush (output_fd);
}

static INLINE boolean_t
init_local_variables (void)
{
  coef = 80.0 / (9.0 * (params.nu * params.nu - 1));

  if (strlen (params.output_file) && strcmp ("-", params.output_file))
    {
      if (!(output_fd = fopen (params.output_file, "wb")))
  {
    ERROR_ ("Failed to open output file `%s` for writing\n",
     params.output_file);
    exit (EXIT_FAILURE);
  }
    }
  else
    output_fd = stdout;
    
  return FALSE;
}

/*-----------------------------------------------------------------*/

static INLINE void
do_calc (gsl_odeiv_step * stepper,
   gsl_odeiv_system * rhs_func_p,
   double * y, double * yerr)
{
  double t;

#ifdef VERBOSE_PROGRESS
  int percents = 0;
  double check_time = 0;
  clock_t cpu_start_time = clock ();
  struct timeval start_time, stop_time;
  
  gettimeofday (&start_time, NULL);
  fprintf (logfd,
     "a0_0 : %g, a0_1 : %g, omega0 : %g\n",
     params.a0_0, params.a0_1, params.omega0);
  fprintf (logfd, "Plate calculation\n");
  fflush (logfd);
#endif /* VERBOSE_PROGRESS */

  init_values (y);

  for (t = 0.0; t < params.stop_time; t += params.dt)
    {
      on_step (t, y);
      gsl_odeiv_step_apply (stepper, t, params.dt, y, yerr,
          NULL, NULL, rhs_func_p);
#ifdef CHECK_SERVER_KEEP_ALIVE
      if (interrupt_handler && interrupt_handler ())
  return;
#endif /* CHECK_SERVER_KEEP_ALIVE */
#ifdef VERBOSE_PROGRESS
      while (t > check_time)
  {
    fprintf (logfd, "\rDone : %d%%", percents++);
    fflush (logfd);
    check_time += params.stop_time / 100;
  }
#endif /* VERBOSE_PROGRESS */
      
      if (gsl_isnan (y[0]))
  break;
    }
  
#ifdef VERBOSE_PROGRESS
  if (gsl_isnan (y[0]))
    fprintf (logfd, "\n");
  else
    fprintf (logfd, "\rDone : 100%%\n");
  fflush (logfd);
#endif /* VERBOSE_PROGRESS */
  
  if (params.max_flag)
    fprintf (output_fd, "%g %g ",params.a0_1, max_w);
  if (params.hsa_flag)
    {
      char filename[32];
      char * filename_ptr = filename;
      if (strlen (params.hsa_filename_template))
  sprintf (filename_ptr, params.hsa_filename_template,
     params.omega0, params.a0_1);
      else
  filename_ptr = NULL;
      if (gsl_isnan (y[0]))
  fprintf (output_fd, "%d %d ", 0, UNDEF);
      else
  {
    int osc_type = 0;
    double main_freq = 0;
    
    osc_type = hsa_main (&main_freq, filename_ptr,
             params.omega0 * 2.1,
             params.dt * params.output_divider);
              
         /*!!if(!params.max_flag)*/ fprintf (output_fd, "%.2g %d ",
               main_freq / params.omega0, osc_type);
  }
    }

#ifdef VERBOSE_PROGRESS
  gettimeofday (&stop_time, NULL);
  fprintf (logfd,
     "Processor time usage : %.2f sec\n"
     "Real time elapsed    : %.2f sec\n",
     ((double) (clock () - cpu_start_time)) / CLOCKS_PER_SEC,
     (stop_time.tv_sec - start_time.tv_sec) +
     (stop_time.tv_usec - start_time.tv_usec) * 1e-6);
  fflush (logfd);
#endif /* VERBOSE_PROGRESS */
}

static boolean_t
run_stepper (gsl_odeiv_step * stepper)
{
  gsl_odeiv_system rhs_func;
  double * y, * yerr;
  double omega0_, a0_1_;
  clock_t cpu_start_time;
  struct timeval start_time, stop_time;

  gettimeofday (&start_time, NULL);
  cpu_start_time = clock ();
     
  rhs_func.function = rhs;
  rhs_func.dimension = SYS_DIMENSION;

  y = (double*)alloca (rhs_func.dimension * sizeof (double));
  yerr = (double*)alloca (rhs_func.dimension * sizeof (double));
  
  omega0_ = params.omega0;
  a0_1_ = params.a0_1;

  for (;;)
    {
      params.omega0 = omega0_;
      do {
  do_calc (stepper, &rhs_func, y, yerr);
  if (interrupt_handler && interrupt_handler ())
    return EXIT_FAILURE;
  params.omega0 += params.omega0_step;
      } while ((params.omega0 < params.omega0_up)
         && (params.omega0_step != 0));
      params.a0_1 += params.a0_step;
      if ((params.a0_1 < params.a0_up) && (params.a0_step != 0))
  fprintf (output_fd, "\n");
      else
  break;
    }

  params.omega0 = omega0_;
  params.a0_1 = a0_1_;
  
  gettimeofday (&stop_time, NULL);
  fprintf (logfd,
     "Total time usage\n"
     "Processor time usage : %.2f sec\n"
     "Real time elapsed    : %.2f sec\n",
     ((double) (clock () - cpu_start_time)) / CLOCKS_PER_SEC,
     (stop_time.tv_sec - start_time.tv_sec) +
     (stop_time.tv_usec - start_time.tv_usec) * 1e-6);
  fflush (logfd);

  return EXIT_SUCCESS;
}

int
run_method (parameters_t * params_)
{
  gsl_odeiv_step *stepper;
  int status;

#define NEW_STEPPER(NAME, SUFFIX) \
    case NAME:                \
      stepper = gsl_odeiv_step_alloc (gsl_odeiv_step_ ## SUFFIX,  \
              SYS_DIMENSION);     \
      break;

  params = *params_;
   
  if (init_local_variables ())
    return EXIT_FAILURE;

  switch (params.method)
    {
      NEW_STEPPER (RK2, rk2);
      NEW_STEPPER (RK4, rk4);
      NEW_STEPPER (RKF45, rkf45);
      NEW_STEPPER (RKCK, rkck);
      NEW_STEPPER (RK8PD, rk8pd);
      NEW_STEPPER (RK2IMP, rk2imp);
      NEW_STEPPER (RK4IMP, rk4imp);
      NEW_STEPPER (GEAR1, gear1);
      NEW_STEPPER (GEAR2, gear2);
    default:
      ERROR_ ("Unknown method\n");
      return EXIT_FAILURE;
    }
  
  status = run_stepper (stepper);

  fclose (output_fd);
  hsa_cleanup ();
  
  gsl_odeiv_step_free (stepper);
  return status;
}
