#!/usr/bin/env python
import re
import sys
import subprocess
import yaml
from os import path
BUILDDEPS = "builddeps.yaml"
RTEMPLATE = """
module load %s;
echo 'download.packages("%s",destdir="../sources", repos=c("https://cran.r-project.org","http://bioconductor.org/packages/release/bioc"))' | R --slave
"""

MAKEFILE_SUFFIX = ''
#if len(sys.argv) > 1:
#   MAKEFILE_SUFFIX = sys.argv[1]

def name_mangle(name):
    return name.replace(".","_")

##  Read the builddeps file
f = open(BUILDDEPS,"r")
allPkgs = yaml.load(f)
f.close()

# This might include system packages 
total = len(allPkgs.keys())
count = 0

for pkg in allPkgs.keys():
    count = count + 1 
    if not path.exists("../sources/%s_%s.tar.gz" % (pkg, allPkgs[pkg]['version'])): 
        print("[%d/%d] downloading package %s version %s" % \
           (count,total, pkg,allPkgs[pkg]['version']))
#        if pkg not in basePkgs.keys():
#        	proc = subprocess.Popen(["/bin/bash"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#        	(output,err) = proc.communicate(RTEMPLATE % (R_MODULE,pkg))
#        else:
       	proc = subprocess.Popen(["make","-f", "Makefile%s" % MAKEFILE_SUFFIX, "download","PKG=%s" % name_mangle(pkg)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
       	(output,err) = proc.communicate()

