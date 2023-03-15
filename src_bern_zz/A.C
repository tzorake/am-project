#include <stdio.h>
#include <math.h>

int main ()
{
  double i, h, m, n;
  m = 26; n = 40;  h = 1;
  for (i = m; i < n; i+=h)
   {
   printf("starter_fft_0.1_q.exe %g > q_fft_0.1_q.opt\n", i);
    printf("cone1.exe -@ q_fft_0.1_q.opt\n");
  }
 return 0;
}