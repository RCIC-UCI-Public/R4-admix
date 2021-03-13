#! /bin/bash
#
# remove requirement that rstudio depends on an system-supplied library
# libQt5EglFSDeviceIntegration.so.5()(64bit) is provided by qt5-qtbase
/usr/lib/rpm/find-requires $* | sed -e 'libQt5EglFSDeviceIntegration.so.5\.*Qt_5_PRIVATE_API\.*/d'
