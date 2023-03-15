#include <stdio.h>
#include <process.h>

char *my_template =
 "
 	#-sr -l ipo_s.log\n\
	-o pr_hk_0.1_KK_5000_om_2.847_e_0.5_n16_p_0_q_\n\
  --max --hsa_ft  pr_hk_0.01_KK_5000_om_2.847_e_0.5_n40_p_0_q_%s\n\
  --hsa\n\               
  #--tm_u\n\             
  #--tm_w\n\
  --a0_0 0\n\
  --a0_1 %s\n\
  --a0_step 0\n\
  --a0_up 0\n\ 
  --omega0 2.847\n\
  --omega0_step 0.\n\
  --omega0_up 0.\n\
  --kluch 0\n\
  --klsq 0\n\
  --kleq 0\n\
  --hk 0.01\n\ 
  #--sp\n\ 
  --st 532\n\
  --out_div 8\n\
  --e1 0.5\n\ 
  --e2 0.0\n\
  --e3 0.5\n\ 
  --am 0.000\n\
  -m rk4\n\
  --hsa_st 20\n\
  --cappa 0.0\n\
  --sk_gr 0.0000\n\
  --lymbda 50\n\
  --n 40\n\   

#--d 0.0625\n\
#19 --d 1.9073486328125e-06\n\
#18 --d 3.814697265625e-06\n\
#17 --d 7.62939453125e-06\n\
#16 --d 1.52587890625e-05\n\
#15 --d 3.0517578125e-05\n\
#14 --d 6.103515625e-05\n\
#13 --d 0.0001220703125\n\
#12 --d 0.000244140625\n\
# --d 0.00048828125\n\
 --d 0.0009765625\n\
# --d 0.001953125\n\
# --d 0.00390625\n\
#7 --d 0.0078125\n\
#   --d 0.015625\n\
#5 --d 0.03125\n\
#4 --d 0.0625\n\
#3 --d 0.125\n\
#2 --d 0.25\n\
#1.336847937698
# 32968\n";

void main(int argc,char **argv)
  {

        printf(my_template,argv[1],argv[1]);
    
  }

