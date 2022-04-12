# Copyright (c) 2000 - 2019 The Regents of the University of California.
# All rights reserved.	
# This includes the Generic yaml2rpm Makefile - most packaging should
# be able to use this.

ALL_TARGETS = bootstrap rebuild
include $(YAML2RPM_HOME)/sys/Makefile

.DEFAULT_GOAL = default
.PHONY: force

## when cleaning temporary yaml files, figure out which ones to not remove
KEEPYAMLS0 = $(shell $(BASEGENERATE) -Q --query=bootstrap $(PACKAGES_FILE))
KEEPYAMLS = $(patsubst %,%.yaml,$(KEEPYAMLS0))
KEEPYAMLS += $(wildcard set-*.yaml versions*.yaml common.yaml packages.yaml)
TMPYAMLS0 = $(wildcard *.yaml)
TMPYAMLS = $(filter-out $(KEEPYAMLS),$(TMPYAMLS0))

debug:
	echo "TMPYAMLS" $(TMPYAMLS)
#echo "KEEPYAMLS" $(KEEPYAMLS)
#echo "TMPYAMLS" $(TMPYAMLS)

# when building targets for different R version need to give on a commadn line
# set name, for example SET='404'
ifeq ($(SET),)
    VERSIONS := versions.yaml
else
    VERSIONS := versions-$(SET).yaml
endif

RVERSION = $(shell $(GENERATE) --query=version R.yaml -V $(VERSIONS))
BASE_SRCVER = $(shell $(GENERATE) --query=tarsources R.yaml -V $(VERSIONS))
FREEZE_DIR=freeze-$(SET)
RSETS = $(shell $(BASEGENERATE) -Q --query=rsets $(PACKAGES_FILE))

rebuild:
ifndef BASEONLY
	if [ "$(SET)" == "" ] && [ "$(ALLSETS)" != "" ]; then \
	    for set in $(ALLSETS); do \
		make -e -f $(THISMAKE) SET=$$set bootstrap; \
	    done; \
	fi
endif
ifndef BASEONLY
	if [ "$(SET)" == "" ] && [ "$(RSETS)" != "" ]; then \
	    for set in $(RSETS); do \
		make -e SET=$$set -f $(THISMAKE) clean; \
		make -e -f $(THISMAKE) SET=$$set thaw; \
		make -e -f $(THISMAKE) SET=$$set bootstrap; \
	    done; \
	fi
endif

manifest::
ifndef BASEONLY
	if [ "$(SET)" == "" ] && [ "$(RSETS)" != "" ]; then \
	    for set in $(RSETS); do \
	        make -s -e -f $(THISMAKE) SET=$$set $@; \
	    done; \
	fi
endif

# build using yamls in freeze/
thaw:
	/bin/cp $(FREEZE_DIR)/*.yaml .
	/bin/cp $(FREEZE_DIR)/buildorder .
	(cd ../sources; tar xvf sources-$(BASE_SRCVER).tar.gz)

prep: builddeps.yaml
	./downloadpkg.py $(SET)

builddeps.yaml: modules.desired deps.R
	( module load R/$(RVERSION); \
	  cat deps.R | R --slave > $@  )

buildorder outversions.yaml: builddeps.yaml
	./depend.py > buildorder

# save initial build, provide SET=name
# for example: make freeze SET=404
freeze: force
	echo "freezing all yaml files, bootstrap files, buildorder into freeze subdir $(FREEZE_DIR)"
	if [ ! -d $(FREEZE_DIR) ]; then mkdir $(FREEZE_DIR); fi
	(for name in  $(shell cat buildorder); do       \
	    /usr/bin/cp -p  $$name.yaml  $(FREEZE_DIR); \
	done)
	/usr/bin/cp -p outversions.yaml builddeps.yaml buildorder modules.desired  $(FREEZE_DIR)

# clean after making all RPMs, do after 'freeze' target
deletemod:
	if [ ! -z "$(TMPYAMLS)" ]; then /bin/rm -f $(TMPYAMLS); fi
	/bin/rm -f buildorder
