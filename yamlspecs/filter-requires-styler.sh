#!/bin/bash
#
# remove erroneous dependency on /usr/local/bin 

/usr/lib/rpm/find-requires $* | sed  \
    -e '/\/usr\/local\/bin/d' \
