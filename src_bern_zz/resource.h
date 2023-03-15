#ifdef HAVE_CONFIG_H
#include <config.h>
#endif /* HAVE_CONFIG_H */

#ifdef HAVE_LIBRESLIB

#include <reslib.h>

#else /* ! HAVE_LIBRESLIB */

#define RL_TYPEDEF_STRUCT(T_NAME) typedef struct s_ ## T_NAME {
#define RL_FIELD(T_NAME, TYPE, NAME, RL_TYPE, COM...) TYPE NAME;
#define RL_ARRAY(T_NAME, TYPE, NAME, RL_TYPE, COUNT, COM...) TYPE NAME[COUNT];
#define RL_RARRAY(T_NAME, TYPE, NAME, RL_TYPE, COM...) rarray_t * NAME;
#define RL_END_STRUCT(T_NAME) } T_NAME;

#define RL_TYPEDEF_ENUM(T_NAME) typedef enum {
#define RL_ENUM_DEF(NAME, RHS...) NAME RHS,
#define RL_COMMENTED_ENUM_DEF(COM, NAME, RHS...) NAME RHS,
#define RL_END_ENUM(T_NAME) } T_NAME

#endif /* HAVE_LIBRESLIB */

#undef FALSE
#undef TRUE
RL_TYPEDEF_ENUM (boolean_t)
     RL_ENUM_DEF (FALSE, = 0)
     RL_ENUM_DEF (TRUE, = !0)
RL_END_ENUM (boolean_t);

RL_TYPEDEF_ENUM (method_t)
     RL_ENUM_DEF (RK2, = 0) /* rk2    : embedded 2nd(3rd) Runge-Kutta */
     RL_ENUM_DEF (RK4)    /* rk4    : 4th order (classical) Runge-Kutta */
     RL_ENUM_DEF (RKF45)  /* rk4/5  : 4/5th order Runge-Kutta Fehlberg */
     RL_ENUM_DEF (RKCK)   /* rkck   : embedded 4th(5th) Runge-Kutta, Cash-Karp */
     RL_ENUM_DEF (RK8PD)  /* rk8pd  : embedded 8th(9th) Runge-Kutta, Prince-Dormand */
     RL_ENUM_DEF (RK2IMP) /* rk2imp : implicit 2nd order Runge-Kutta at Gaussian points */
     RL_ENUM_DEF (RK4IMP) /* rk4imp : implicit 4th order Runge-Kutta at Gaussian points */
     RL_ENUM_DEF (GEAR1)  /* gear1  : M=1 implicit Gear method */
     RL_ENUM_DEF (GEAR2)  /* gear2  : M=2 implicit Gear method */
     RL_ENUM_DEF (NUM_METHODS)  /* always keep last */
RL_END_ENUM (method_t);

RL_TYPEDEF_STRUCT (parameters_t)
     RL_FIELD (parameters_t, method_t, method, RL_ENUM, )
     RL_FIELD (parameters_t, int, output_divider, RL_INTEGER, )
     RL_FIELD (parameters_t, double, stop_time, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, dt, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, e1psilon, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, e2psilon, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, e3psilon, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, cappa, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, sk_gr, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, px, RL_DOUBLE, )
     RL_FIELD (parameters_t, int, lymbda, RL_INTEGER, )
     RL_FIELD (parameters_t, double, p0_0, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, p0_1, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, p1_0, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, p1_1, RL_DOUBLE, )
     RL_FIELD (parameters_t, int, n, RL_INTEGER, )
     RL_FIELD (parameters_t, double, nu, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, amplitude, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, a0_0, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, a0_1, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, a0_up, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, a0_step, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, omega0, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, omega1, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, omega2, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, omega0_up, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, omega0_step, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, fu, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, with, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, to, RL_DOUBLE, )
     RL_FIELD (parameters_t, int, kluch, RL_INTEGER, )
     RL_FIELD (parameters_t, int, kk, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, kleq, RL_DOUBLE, )
     RL_FIELD (parameters_t, double, hk, RL_DOUBLE, )

     RL_FIELD (parameters_t, boolean_t, sp_flag, RL_ENUM, )
     RL_FIELD (parameters_t, boolean_t, verbose_output_flag, RL_ENUM, )
     RL_FIELD (parameters_t, boolean_t, hsa_flag, RL_ENUM, )
     RL_FIELD (parameters_t, boolean_t, tm_u_flag, RL_ENUM, )
     RL_FIELD (parameters_t, boolean_t, tm_w_flag, RL_ENUM, )
     RL_FIELD (parameters_t, boolean_t, max_flag, RL_ENUM, )
     RL_FIELD (parameters_t, double, hsa_start_time, RL_DOUBLE, )
     RL_FIELD (parameters_t, str_t, hsa_filename_template, RL_CHAR_ARRAY, )
     RL_FIELD (parameters_t, str_t, output_file, RL_CHAR_ARRAY, )
     RL_FIELD (parameters_t, str_t, host_name, RL_CHAR_ARRAY, )
     RL_FIELD (parameters_t, int, server_port, RL_INTEGER, )
     RL_FIELD (parameters_t, int, client_retry_period, RL_INTEGER, )
     RL_FIELD (parameters_t, int, start_m, RL_INTEGER, )
     RL_FIELD (parameters_t, int, stop_m, RL_INTEGER, )
     RL_FIELD (parameters_t, boolean_t, restart_server_flag, RL_ENUM, )
 RL_END_STRUCT (parameters_t);
