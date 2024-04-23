#!/usr/bin/env python
from __future__ import print_function
import re
import sys
import subprocess
import yaml

R_VERSION = "{{Rversion}}"
R_MODULE = "R/%s" % R_VERSION

YAMLTEMPLATE="""
!include common.yaml
---
- package: R module MODULE
  name: MODULE
  rpkgname: %s
  version: "{{versions.MODULE}}"
  baseurl: %s
  src_tarball: "{{rpkgname}}_{{version}}.{{extension}}"
  vendor_source: "{{baseurl}}/{{rpkgname}}_{{version}}.{{extension}}"
"""
YAMLTEMPLATE_RELEASE="""
!include common.yaml
---
- package: R module MODULE
  name: MODULE
  rpkgname: %s
  sversion: "{{versions.MODULE}}"
  subversion: "{{versions.MODULE_subversion}}"
  version: "{{sversion}}.{{subversion}}"
  baseurl: %s
  src_tarball: "{{rpkgname}}_{{sversion}}-{{subversion}}.{{extension}}"
  vendor_source: "{{baseurl}}/{{rpkgname}}_{{sversion}}-{{subversion}}.{{extension}}"
  description: >
    {{rpkgname}} version {{sversion}}-{{subversion}} for R version {{Rversion}}.
"""
BUILD_OVERRIDE="""
  build:
    configure: echo no configure required
    pkgmake: echo installed with R CMD INSTALL
    target:
    modules:
      - R/{{Rversion}}
"""

addModules = { 'Rmpi': ['mpi/openmpi-x86_64'] }

def name_mangle(name):
    return name.replace(".","_")

class Node(object):
    def __init__(self,name,r_modules=None):
        self.name = name
        self.pkgname = name_mangle(self.name)
        try:
            self.baseurl = r_modules[name]['baseurl']
        except:
            pass
        self.edges = []
    def addEdge(self, node):
        self.edges.append(node)

    def resolve(self,resolved):
        for edge in self.edges:
            if edge not in resolved:
                edge.resolve(resolved)
        resolved.append(self)

syspkgs = [ "KernSmooth", "MASS", "Matrix", "base", "boot", "class", "cluster", "codetools", \
"compiler", "datasets", "foreign", "grDevices", "graphics", "grid", "lattice", "methods", \
"mgcv", "nlme", "nnet", "parallel", "rpart", "spatial", "splines", "stats", "stats4", "survival", \
"tcltk", "tools", "translations", "utils" ] 

# Create Graph nodes for every module
with open("builddeps.yaml") as f:
    r_modules = yaml.load(f)

nodes = [ Node(name,r_modules) for name in r_modules.keys()]

# Track the yaml files we are not supposed to overwrite
with open("modules.bootstrap","r") as g:
    klines = g.readlines()
    keep = [ x.strip() for x in klines ]

# make a  master Node to and add all edges to it to make sure that the dependency graph is connected
master = Node('root node')
for node in nodes:
    if node.name not in syspkgs:
        master.addEdge(node)
    else:
        sys.stderr.write("INFO: Not writing yaml file for system package %s\n" % node.name)
        
    deps = r_modules[node.name]['requires']
    try:
        edges = filter(lambda x: x.name in deps, nodes)
        for edge in edges:
            if edge.name not in syspkgs:
                node.addEdge(edge)
    except:
        pass

resolved = []
# Resolve 
master.resolve(resolved)
yamlversions=open("outversions.yaml","w")
for pkg in resolved:
    try:
        version=r_modules[pkg.name]['version']
        print("%s" % pkg.pkgname)
        if pkg.pkgname in keep:
            sys.stderr.write("INFO: Skipping pre-defined package yaml %s\n" % pkg.pkgname)
            continue
        r=re.search("-",version)
        if r is None:
           template = YAMLTEMPLATE
        else:
           (version,subversion) = version.split('-')
           yamlversions.write('%s_subversion: "%s"\n' % (pkg.pkgname,subversion))
           template = YAMLTEMPLATE_RELEASE

        yamlversions.write('%s: "%s"\n' % (pkg.pkgname,version))
   
        appendFileName = "%s.yaml.append" % pkg.pkgname
        try:
            with open(appendFileName,"r") as addToF:
                appendData = addToF.readlines()
        except:
            appendData = ""
        with open("%s.yaml" % pkg.pkgname,"w") as f:
            contents=re.sub("MODULE", pkg.pkgname, template) % (pkg.name,pkg.baseurl)
            f.write(contents)
            deps = r_modules[pkg.name]['requires']
            f.write("  requires:\n") 
            f.write("    - R_%s\n" % R_VERSION)
            if deps is not None:
                for p in deps:
                    if p not in syspkgs:
                        f.write("    - R_%s-%s\n" % (R_VERSION,name_mangle(p)))

            if pkg.pkgname in addModules.keys():
                f.write(BUILD_OVERRIDE)
                for mod in addModules[pkg.pkgname]:
                    f.write("      - %s\n" % mod)
            f.write("".join(appendData))
    except: 
        pass 

yamlversions.close()
