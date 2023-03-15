/* -*- C -*- */
/* I hate this bloody country. Smash. */
/* This file is part of ResLib project */

#if defined(RL_MAKE_DESCRIPTORS) && defined(RL_MAKE_PROTOS)
#error Define only one of possible variants : RL_MAKE_PROTOS or RL_MAKE_DESCRIPTORS
#endif

#if !defined(RL_MAKE_DESCRIPTORS) && !defined(RL_MAKE_PROTOS)
#define RL_MAKE_PROTOS
#endif

#undef RL_TYPEDEF_STRUCT
#undef RL_FIELD
#undef RL_POINTER
#undef RL_SELF_POINTER
#undef RL_SELF_POINTER_
#undef RL_RARRAY
#undef RL_FUNC
#undef RL_END_STRUCT

#undef RL_TYPEDEF_ENUM
#undef RL_ENUM_DEF
#undef RL_COMMENTED_ENUM_DEF
#undef RL_END_ENUM

/* macroses for defining prototypes */
#ifdef RL_MAKE_PROTOS

#define RL_TYPEDEF_STRUCT(T_NAME) typedef struct s_ ## T_NAME {
#define RL_FIELD(T_NAME, TYPE, NAME, RL_TYPE, SUFFIX, COM...) TYPE NAME SUFFIX;
#define RL_POINTER(T_NAME, TYPE, NAME, RL_TYPE, COM...) TYPE * NAME;
#define RL_SELF_POINTER(T_NAME, NAME, COM...) struct s_ ## T_NAME * NAME;
#define RL_SELF_POINTER_ RL_SELF_POINTER
#define RL_RARRAY(T_NAME, TYPE, NAME, RL_TYPE, COM...) rarray_t NAME;
#define RL_FUNC(T_NAME, TYPE, NAME, ARGS, COM...) TYPE (*NAME) ARGS;
#define RL_END_STRUCT(T_NAME) } T_NAME;

#define RL_TYPEDEF_ENUM(T_NAME) typedef enum {
#define RL_ENUM_DEF(NAME, RHS...) NAME RHS,
#define RL_COMMENTED_ENUM_DEF(COM, NAME, RHS...) NAME RHS,
#define RL_END_ENUM(T_NAME) } T_NAME

/* ResLib prototypes */
#ifndef RL_DEFINE_ONCE
#define RL_DEFINE_ONCE

#define RL_TYPE_BITS (8)
#define RL_MAX_TYPES (1 << RL_TYPE_BITS)
#define RL_TYPE_MASK (RL_MAX_TYPES - 1)

#include <stdio.h> /* for FILE */
#include <rlprotos.h>

#define RL_NUM_MASKS (sizeof (rl_type_mask_t) * 8)

extern rl_conf_t rl_conf;

typedef char * (*rl_save_type_handler_t) (void*, rl_fd_t*, int, rarray_t*);
typedef char * (*rl_load_type_handler_t) (void*, rl_fd_t*, char*, rarray_t*);

extern rarray_t * rl_add_type (rl_type_t, rl_fd_t*, char*, int, int, char*);
extern rarray_t * rl_add_own_descriptors (void);
extern char * rl_read_object (FILE*);
extern char * rl_save_field (void*, rl_fd_t*, int, rarray_t*);
extern char * rl_load_field (void*, rl_fd_t*, char*, rarray_t*);

/* also possible custom types save/load handlers */
extern rl_save_type_handler_t *
rl_register_save_type_handler (rl_type_t, rl_save_type_handler_t);
extern rl_load_type_handler_t *
rl_register_load_type_handler (rl_type_t, rl_load_type_handler_t);

/* also possible custom mask save/load handlers */
extern rl_save_type_handler_t *
rl_register_save_mask_handler (rl_type_mask_t, rl_save_type_handler_t);
extern rl_load_type_handler_t *
rl_register_load_mask_handler (rl_type_mask_t, rl_load_type_handler_t);

#define RL_ARRAY(RL_TYPE) ((RL_TYPE) | (1 << RL_MASK_ARRAY))

#define RL_ADD_TYPE(RL_TYPE, T_NAME, COM...) rl_add_type (RL_TYPE, rl_ ## T_NAME, #T_NAME, sizeof (rl_ ## T_NAME), sizeof (T_NAME), "" COM)

#define RL_SAVE_STRUCT(S_PTR, S_TYPE) ({				\
  rl_fd_t __fd__ = {.type = #S_TYPE, .rl_type = RL_STRUCT};		\
  rarray_t __ptrs__ = {.size = 0, .data = NULL};			\
  char * __str__ = rl_save_field (S_PTR, &__fd__, 0, &__ptrs__);	\
  if (__ptrs__.data) free (__ptrs__.data);				\
  __str__;								\
})

#define RL_LOAD_STRUCT(S_PTR, S_TYPE, STR) ({				\
  rl_fd_t __fd__ = {.type = #S_TYPE, .rl_type = RL_STRUCT};		\
  rarray_t __ptrs__ = {.size = 0, .data = NULL};			\
  char * __str__ = rl_load_field (S_PTR, &__fd__, STR, &__ptrs__);	\
  if (__ptrs__.data) free (__ptrs__.data);				\
  __str__;								\
})

#define RL_SAVE_RARRAY(S_PTR, S_TYPE, RL_TYPE) ({			\
  rl_fd_t __fd__ = {.type = #S_TYPE, .type_size = sizeof (S_TYPE), .rl_type = RL_TYPE | (1 << RL_MASK_RARRAY)}	\
  rarray_t __ptrs__ = {.size = 0, .data = NULL};			\
  char * __str__ = rl_save_field (S_PTR, &__fd__, 0, &__ptrs__);	\
  if (__ptrs__.data) free (__ptrs__.data);				\
  __str__;								\
})

#define RL_LOAD_RARRAY(S_PTR, S_TYPE, RL_TYPE, STR) ({			\
  rl_fd_t __fd__ = {.type = #S_TYPE, .type_size = sizeof (S_TYPE), .rl_type = RL_TYPE | (1 << RL_MASK_RARRAY)}	\
  rarray_t __ptrs__ = {.size = 0, .data = NULL};			\
  char * __str__ = rl_load_field (S_PTR, &__fd__, STR, &__ptrs__);	\
  if (__ptrs__.data) free (__ptrs__.data);				\
  __str__;								\
})

#endif /* RL_DEFINE_ONCE */

#endif /* RL_MAKE_PROTOS */

/* macros for defining descriptors */
#ifdef RL_MAKE_DESCRIPTORS

#ifndef RL_DESCRIPTOR_PREFIX
#define RL_DESCRIPTOR_PREFIX static
#endif /* RL_DESCRIPTOR_PREFIX */

#define RL_TYPEDEF_STRUCT(T_NAME) RL_DESCRIPTOR_PREFIX rl_fd_t rl_ ## T_NAME [] = {
 
#define RL_FIELD(T_NAME, TYPE, NAME, RL_TYPE, SUFFIX, COM...) {		\
  .type = #TYPE,							\
  .name = #NAME,							\
  .type_size = sizeof(TYPE),						\
  .offset = (int)(&(((T_NAME*)0)->NAME)),				\
  .rl_type = RL_TYPE,							\
  .count = sizeof (((T_NAME*)0)->NAME) / sizeof (TYPE),			\
  .value = 0,								\
  .comment = "" COM,							\
},
	  
#define RL_POINTER(T_NAME, TYPE, NAME, RL_TYPE, COM...) {		\
  .type = #TYPE,							\
  .name = #NAME,							\
  .type_size = sizeof(TYPE),						\
  .offset = (int)(&(((T_NAME*)0)->NAME)),				\
  .rl_type = (RL_TYPE) | (1 << RL_MASK_POINTER),			\
  .count = sizeof (((T_NAME*)0)->NAME) / sizeof (TYPE),			\
  .value = 0,								\
  .comment = "" COM,							\
},

#define RL_SELF_POINTER(T_NAME, NAME, COM...) {				\
  .type = #T_NAME,							\
  .name = #NAME,							\
  .type_size = sizeof(T_NAME),						\
  .offset = (int)(&(((T_NAME*)0)->NAME)),				\
  .rl_type = (RL_STRUCT) | (1 << RL_MASK_POINTER),			\
  .count = 1,								\
  .value = 0,								\
  .comment = "" COM,							\
},

#define RL_SELF_POINTER_(T_NAME, NAME, COM...) {			\
  .type = #T_NAME,							\
  .name = #NAME,							\
  .type_size = sizeof(T_NAME),						\
  .offset = (int)(&(((T_NAME*)0)->NAME)),				\
  .rl_type = (RL_NONE) | (1 << RL_MASK_POINTER),			\
  .count = 1,								\
  .value = 0,								\
  .comment = "" COM,							\
},

#define RL_RARRAY(T_NAME, TYPE, NAME, RL_TYPE, COM...) {		\
  .type = #TYPE,							\
  .name = #NAME,							\
  .type_size = sizeof(TYPE),						\
  .offset = (int)(&(((T_NAME*)0)->NAME)),				\
  .rl_type = (RL_TYPE) | (1 << RL_MASK_RARRAY),				\
  .count = 1,								\
  .value = 0,								\
  .comment = "" COM,							\
},

#define RL_FUNC(T_NAME, TYPE, NAME, ARGS, COM...)

#define RL_END_STRUCT(T_NAME) }

#define RL_TYPEDEF_ENUM(T_NAME) static rl_fd_t rl_ ## T_NAME [] = {
#define RL_ENUM_DEF(NAME, RHS...) { .name = #NAME, .value = NAME, .comment = "", },
#define RL_COMMENTED_ENUM_DEF(COM, NAME, RHS...) { .name = #NAME, .value = NAME, .comment = "" COM, },
#define RL_END_ENUM(T_NAME) }

#endif /* RL_MAKE_DESCRIPTORS */

#undef RL_MAKE_DESCRIPTORS
#undef RL_MAKE_PROTOS
