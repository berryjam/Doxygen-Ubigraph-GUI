#
# This file was generated from Makefile.in on 2014年11月29日 星期六 21时31分06秒 CST
#

RM        = rm -f
VERSION   = 1.8.6
INSTALL   = /usr/local
INSTTOOL  = /usr/local/bin/ginstall
DOXYDOCS  = ..

export TMAKEPATH
install: 
	$(INSTTOOL) -d $(INSTALL)/bin
	$(INSTTOOL) -d $(INSTALL)/doc/doxygen
	$(INSTTOOL) -m 755 bin/doxygen    $(INSTALL)/bin
	#$(INSTTOOL) -m 755 bin/doxytag    $(INSTALL)/bin
	#$(INSTTOOL) -m 755 bin/doxywizard $(INSTALL)/bin
	cp -r html $(INSTALL)/doc/doxygen
	cp -r examples $(INSTALL)/doc/doxygen
