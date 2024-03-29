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

if len(sys.argv) > 1:
   SETSTR = "SET=%s" % sys.argv[1]
else:
   SETSTR = ''

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
        proc = subprocess.Popen(["make","-f", "Makefile", "download","PKG=%s" % name_mangle(pkg), SETSTR], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print (["make","-f", "Makefile", "download","PKG=%s" % name_mangle(pkg), SETSTR] )
        (output,err) = proc.communicate()
