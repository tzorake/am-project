#ifndef _HSA_H_
#define _HSA_H_

/*
                           -1 - 2 независимые частоты
                           -2 - суперпозиция независимых частот
                           -3 - undef
                           -4 - затухающии колебания
                           -5 - хаос
                           0 - гармоники
                           n > 0 - номер бифуркации 
*/
typedef enum {
  UNDEF = -3,
  CHAOS = -5,
  FAKE = -4,
  HARMONIC = 0,
  IND_FREQ = -1,
  SP_IND_FREQ = -2
} osc_type;


void hsa_read_data (double, double, double);
osc_type hsa_main (double *, char *, double, double);
void hsa_cleanup (void);

#endif /* _HSA_H_ */
