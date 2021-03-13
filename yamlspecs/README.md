This creates a large number of RPMS for R-modules defined in the file: modules.desired

The logic is as follows on a build system:
* bootstrap builds R and the R-module
* Then R is used to a create a yaml file of module dependencies (based on those listed in modules.desired)
* From the dependences (outputfile is builddeps.yaml) a build order of modules is created AND yaml files
  to define an RPM of each R modules built
* Tarballs are downloaded to the ../sources directory
* The Modules are built in and installed in dependency order

To return the build system to a state where R is not installed
"""make unbootstrap"""


