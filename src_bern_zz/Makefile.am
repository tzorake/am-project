## Process this file with automake to produce Makefile.in

bin_PROGRAMS = cone 

cone_SOURCES = main.c cone.c hsa.c client.c server.c \
	cone.h hsa.h client.h server.h

static:
	$(MAKE) clean-binPROGRAMS
	$(MAKE) LDFLAGS="-s --static"

cone_LDADD = $(GETOPT_LIBS) $(GSL_LIBS) $(RESLIB_LIBS) $(WINSOCK_LIBS)
INCLUDES = -I$(top_builddir) -I.
