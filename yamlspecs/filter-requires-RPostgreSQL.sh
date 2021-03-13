#!/bin/bash
#
# remove erroneous requirements
# with hard-coded paths.

/usr/lib/rpm/find-requires $* | sed  \
    -e '/\/usr\/bin\/r/d' \
