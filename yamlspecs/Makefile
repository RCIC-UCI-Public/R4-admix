# Copyright (c) 2000 - 2019 The Regents of the University of California.
# All rights reserved.	
# This includes the Generic yaml2rpm Makefile - most packaging should
# be able to use this.
ALL_TARGETS = rebuild
include $(YAML2RPM_HOME)/sys/Makefile
SHELL = /bin/bash

.DEFAULT_GOAL = default
.PHONY: force

## when cleaning temporary yaml files, figure out which ones to not remove
KEEPYAMLS0 = $(shell cat modules.bootstrap | grep -v '^\#' )
#KEEPYAMLS0 += $(shell cat keepyamls | grep -v '^\#' )
KEEPYAMLS0 += common
KEEPYAMLS = $(patsubst %,%.yaml,$(KEEPYAMLS0))
TMPYAMLS0 = $(wildcard *.yaml)
TMPYAMLS = $(filter-out $(KEEPYAMLS),$(TMPYAMLS0))

RVERSION = $(shell grep ^R: versions.yaml.base | awk -F \" '{print $$2}')
FREEZE_DIR=freeze
BASE_SRCVER = $(shell $(GENERATE) --query=tarsources versions.yaml.base)

# run this if need to automatically rebuild the whole admix
# from already existing and saved yamls in 'freeze/' and using
# pickled sources. 
rebuild: versions.yaml bootstrap thaw 
	make BOOTSTRAP_MODULES_FILE=buildorder bootstrap
	make modules.manifest

# run this target if building all packages anew from scratch 
# and downloading new verisons, building dependency, etc.
# must have desired list of modules to start with.
all: versions.yaml bootstrap modules.build allversions prep 
	make BOOTSTRAP_MODULES_FILE=buildorder bootstrap
	make modules.manifest

# build using yamls in freeze/
thaw:
	/bin/cp $(FREEZE_DIR)/buildorder .
	/bin/cp $(FREEZE_DIR)/modules.build .
	/bin/cp $(FREEZE_DIR)/*.yaml .
	cat versions.yaml.base outversions.yaml > versions.yaml
	(cd ../sources; tar xvf sources-$(BASE_SRCVER).tar.gz)

prep: modules.build 
	./downloadpkg.py

builddeps.yaml: modules.desired deps.R
	( module load R/$(RVERSION); \
	  cat deps.R | R --slave > $@  )

allversions: outversions.yaml versions.yaml.base
	rm -rf versions.yaml
	cat versions.yaml.base outversions.yaml > $@
	cat versions.yaml.base outversions.yaml > versions.yaml

versions.yaml: 
	cat versions.yaml.base > $@

buildorder outversions.yaml: builddeps.yaml 
	./depend.py > buildorder

modules.build: modules.bootstrap buildorder 
	cat modules.bootstrap buildorder > $@

modules.manifest: force
	cat modules.build >$@
	
manifest:: modules.manifest

# save initital build
freeze: allversions force
	echo "freezing all yaml files, bootstrap files, buildorder into freeze subdir $(FREEZE_DIR)"
	if [ ! -d $(FREEZE_DIR) ]; then mkdir $(FREEZE_DIR); fi
	/usr/bin/cp -p *base *yaml  modules.* buildorder $(FREEZE_DIR) 

# clean after making all RPMs, do after 'freeze' target
deletemod:
	/bin/rm -f allversions
	/bin/rm -f modules.build
	/bin/rm -f modules.manifest
	if [ ! -z "$(TMPYAMLS)" ]; then /bin/rm -f $(TMPYAMLS); fi
	/bin/rm -f buildorder 
