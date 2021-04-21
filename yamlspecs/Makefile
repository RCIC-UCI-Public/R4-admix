# Copyright (c) 2000 - 2019 The Regents of the University of California.
# All rights reserved.	
# This includes the Generic yaml2rpm Makefile - most packaging should
# be able to use this.
ALL_TARGETS = all
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

all: versions.yaml modules.build bootstrap allversions prep 
	make BOOTSTRAP_MODULES_FILE=buildorder bootstrap
	make modules.manifest
restore:
	if [ ! -f buildorder ]; then cp $(FREEZE_DIR)/buildorder .; fi
	if [ ! -f outversions.yaml ]; then cp $(FREEZE_DIR)/outversions.yaml .; fi
	if [ ! -f builddeps.yaml ]; then cp $(FREEZE_DIR)/builddeps.yaml .; fi
	if [ ! -f modules.build ]; then cp $(FREEZE_DIR)/modules.build .; fi

prep: modules.build 
	./downloadpkg.py

builddeps.yaml: modules.desired deps.R
	( module load R/$(RVERSION); \
	  cat deps.R | R --slave > $@  )

allversions: outversions.yaml versions.yaml.base
	rm -rf versions.yaml
	cat outversions.yaml versions.yaml.base > $@
	cat outversions.yaml versions.yaml.base > versions.yaml

versions.yaml: 
	cat versions.yaml.base > $@

buildorder outversions.yaml: builddeps.yaml 
	./depend.py > buildorder

modules.build: modules.bootstrap buildorder 
	cat modules.bootstrap buildorder > $@

modules.manifest: force
	cat modules.build >$@
	
manifest: modules.manifest

freeze: allversions force
	echo "freezing all yaml files, bootstrap files, buildorder into freeze subdir $(FREEZE_DIR)"
	if [ ! -d $(FREEZE_DIR) ]; then mkdir $(FREEZE_DIR); fi
	/usr/bin/cp -p *base *yaml  modules.* buildorder $(FREEZE_DIR) 

deletemod:
	-/bin/rm allversions
	-/bin/rm modules.build
	-/bin/rm $(TMPYAMLS)
	-/bin/rm buildorder 
