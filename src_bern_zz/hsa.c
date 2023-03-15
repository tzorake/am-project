/* -*- C -*- */
/* I hate this bloody country. Smash. */
/* This file is part of INFINITE PLATE OSCILLATIONS project */
/* Heuristic Spectrum Analyzer */

#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <math.h>
#include <gsl/gsl_sys.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_math.h>
#include <gsl/gsl_fft_real.h>

#include <cone.h>
#include <hsa.h>

typedef double c_type;
#define CHUNK_SIZE ((32 * 4096 - 16) / sizeof (c_type))

static c_type * hsa_array = NULL;
static int hsa_curent_size = 0;
static int hsa_n = 0;

void
hsa_read_data (double time, double value, double hsa_start_time)
{
  if (time == 0)
    hsa_n = 0;
  if (time >= hsa_start_time)
    {
      if (hsa_n >= hsa_curent_size)
	{
	  hsa_curent_size += CHUNK_SIZE;
	  hsa_array =
	    (c_type*) realloc (hsa_array, hsa_curent_size * sizeof (c_type));
	}
      hsa_array[hsa_n++] = value;
    }
}


//#define DEBUG
#define DIF_LONG 2
#define ANAL_EPS 0.01
#define HSA_VER 1.6.5

static osc_type 
get_interval_type(float *norm, int n, double domega) 
  {
#ifdef DEBUG
    static int once = 0;
    static FILE *df;
#endif
    double anal_eps = ANAL_EPS;
    int idx_eps = (int) (anal_eps / domega);
    int simple_nums[] = {2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37, 39}; //simple numbers table
    int bif_pos = 0;
    int i = sizeof(simple_nums) / sizeof(simple_nums[0]) - 1;
    int current_type = 0; 

    //проверка близости локального максимума
    int peak_test(int i)
      {
        int eps = (i < idx_eps) ? i : idx_eps;
        for(; eps >= 0; eps--)
          {
            if(norm[i + eps] != 0)
              return i + eps;
            if(norm[i - eps] != 0)
              return i - eps;
          }
        return 0;
      }
#ifdef DEBUG
    if(!once)
      {
        df = fopen("debug.hsa", "w");
        once = 1;
      }
    fprintf(df, "Debug session start, n = %d, domega = %g\n", n, domega);
#endif
    //тест на бифуркации
    for(i = 0; i < sizeof(simple_nums) / sizeof(simple_nums[0]); i++)
      {
        int peaks = 0;
        int j;
        for(j = 1; j < simple_nums[i]; j++) 
          {
            int idx = j * n / simple_nums[i];
            if(peak_test(idx))
              peaks++;
            else 
              break;
          }

        if(peaks != 0) 
          {
            bif_pos = peak_test(n / simple_nums[i]);
            if(bif_pos < n) 
               current_type = simple_nums[i];
            else
               current_type = HARMONIC;
            break;
          }
#ifdef DEBUG
    fprintf(df, "n = %d, simple_num = %d, peaks = %d, bif_pos = (%d) %g, test_bif_pos = (%d) %g\n", n, simple_nums[i], peaks, bif_pos, bif_pos * domega, n / simple_nums[i], n / simple_nums[i] * domega);
    fflush(df);
    fflush(df);
#endif
      }
    //тест на независимые частоты
    if(current_type == 0)
      {
        for(i = 0; i < n; i++)
          if(norm[i] != 0)
            break;
        //суперпозиция независимых частот
        if(i != n)
          if(peak_test(n - i - 1)) 
            current_type = SP_IND_FREQ;
          //просто независимая частота
          else
            {
              double div = (double)n / i;
              // несоизмерима с основной частотой
              if(fabs(div - (int)div - 0.5) < 0.5 - anal_eps) 
                {
                  current_type = IND_FREQ;
#ifdef DEBUG
    fprintf(df,"IND_FREQ: position = (%d) %g peak = \n ", i, i * domega);
    fflush(df);
    fflush(df);
#endif
                }
              else
                current_type = UNDEF;

            }
      }
    //тест на вложенные интервалы в бифуркациях
    else 
      {
        osc_type next_type = get_interval_type(norm, bif_pos, domega);
#ifdef DEBUG
    fprintf(df,"return from get_type: current_type = %d next_type = %d\n ", current_type, next_type);
    fflush(df);
    fflush(df);
#endif
        if (next_type < 0) 
          current_type = next_type;
        if ((current_type >= 2) && (current_type < next_type))
          current_type = next_type;
      }
    return current_type;
      
  }


//------------------------------------------------------------------------
static osc_type
get_type (c_type * data, int n, double * mf, double domega)
{
  int i;
  int main_freq;
  double max, min;
  int peak_number, bifurcations;
  float * norm;
  int div;


  data[0] = data[1]; /* special hack for constant part of signal - freq 0 */

  max = min = data[0];
  for (i = 1; i < n; ++i)
    {
      if (data[i] < min)
        min = data[i];
      if (data[i] > max)
        max = data[i];
    }
    
  if (max <= -7)
    return FAKE; //Затухаюшие колебания

  max -= min;
  if (max == 0)
    max = 1;

  /* will be automatically freed */
  norm = (float*) alloca (sizeof (float) * n);
  memset (norm, 0, sizeof (float) * n);
  for (i = 3; i < n - 1; ++i)
    if ((data[i] > data[i - 1]) && (data[i] > data[i + 1]) )
      if((data[i] - data[i - DIF_LONG]) / DIF_LONG / domega >= 1.0)
         norm[i] = (data[i] - min) / max;

  peak_number = 0;
  for (i = 0; (i < n / 4); ++i)
    if (norm[i] != 0)    
      ++peak_number;

  if (peak_number > n / 40 + 1)
    return CHAOS; 

  for (i = 0; i < n; ++i)
    if (norm[i] > 0.99)
      break;
  
  main_freq = i;
  *mf = main_freq * domega;

  return get_interval_type(norm, main_freq, domega);

}


static int
do_fft (double * in, int n)
{
  int i;

  if (n & (n - 1))
    fprintf (logfd, "Warning hsa_n is not radix 2\n");
  
  while (n & (n - 1))
    n &= n - 1;

  if (n <= 1)
    {
      ERROR_ ("Critical error : do_fft failed (n = %d)\n", n);
      return 0;
    }

  gsl_fft_real_radix2_transform (in, 1, n);

  in[0] = log (sqrt (in[0] * in[0]) / n);  /* DC component */
  for (i = 1; i < n / 2; ++i)  /* (i < N/2 rounded up) */
    in[i] = log (sqrt (in[i] * in[i] + in[n - i] * in[n - i]) / n);
  in[n / 2] = log (sqrt (in[n / 2] * in[n / 2]) / n); /* Nyquist freq. */
  return n;
}

static int
hsa_save_spectrum (char * filename, c_type * spectrum, int n, double domega)
{
  FILE * fd = NULL;
  int i;
  
  if (!filename)
    return FALSE;
  if (!(fd = fopen (filename, "w")))
    return FALSE;
  for (i = 0; i < n; ++i)
    fprintf (fd, "%g %g\n", i * domega, spectrum[i]);
  fclose (fd);
  return TRUE;
}

osc_type
hsa_main (double * mf, char * filename, double max_omega, double time_step)
{
  int i;
  int spec_size;
  double domega;
  
  for (i = 0; i < hsa_n; ++i)
    if (gsl_isnan (hsa_array[i]))
      return UNDEF;
  
  if (!(hsa_n = do_fft (hsa_array, hsa_n)))
    return UNDEF;

  domega = (2 * M_PI) / (hsa_n * time_step);
  spec_size = MIN (max_omega / domega, hsa_n / 2);
  
  if (filename)
    if (!hsa_save_spectrum (filename, hsa_array, spec_size, domega))
      fprintf (logfd, "Failed to save spectrum to file %s\n", filename);
  fflush (logfd);
  
  return get_type (hsa_array, spec_size, mf, domega);
}

void
hsa_cleanup (void)
{
  if (hsa_array)
    free (hsa_array);
  hsa_array = NULL;
  hsa_curent_size = 0;
}
