## Read the files "modules.desired" to generate a YAML file 
## of all packages and dependencies. This uses the miniCRAN 
## module, which does recursive dependency resolution.
## This file can then be processed to determine the build/bootstrap order
## of R RPMs, it can also be used to place dependencies in R module RPMs

## Greatfully taken from miniCRAN
## ==> FROM miniCRAN
#' Returns names of base packages.
#'
#' Retrieves names of installed packages by calling
#' [utils::installed.packages()] and returning only those packages where
#' `Priority == "base"`.
#'
#' @export
#' @family dependency functions
#'
#' @seealso [pkgDep()]
basePkgs <- function()names(which(installed.packages()[, "Priority"] == "base"))


#' Retrieves package dependencies.
#'
#' Performs recursive retrieve for `Depends`, `Imports` and `LinkLibrary`.
#' Performs non-recursive retrieve for `Suggests`.
#'
#'
#' @param pkg Character vector of packages.
#'
#' @param availPkgs Data frame with an element called `package`. The `package`
#'   element is a vector of available packages.  Defaults to reading this list
#'   from CRAN, using [available.packages()]
#'
#' @param repos URL(s) of the 'contrib' sections of the repositories, e.g.
#'   `"http://cran.us.r-project.org"`. Passed to [available.packages()]
#'
#' @param type Possible values are (currently) "source", "mac.binary" and
#'   "win.binary": the binary types can be listed and downloaded but not
#'   installed on other platforms.  Passed to [download.packages()].
#'
#' @param depends If TRUE, retrieves `Depends`, `Imports` and `LinkingTo` dependencies
#'   (non-recursively)
#' @param suggests If TRUE, retrieves Suggests dependencies (non-recursively)
#' @param enhances If TRUE, retrieves Enhances dependencies (non-recursively)
#' @param quiet If TRUE, suppresses warnings
#'
#' @param includeBasePkgs If TRUE, include base R packages in results
#' @template Rversion
#' @param ... Other arguments passed to [available.packages()]
#'
#' @export
#' @family dependency functions
#'
#' @example /inst/examples/example_pkgDep.R
#'   
pkgDep <- function(pkg, availPkgs, repos = getOption("repos"), type = "source",
                   depends = TRUE, suggests = TRUE, enhances = FALSE,
                   includeBasePkgs = FALSE, Rversion = R.version, quiet = FALSE, ...) 
{

  if (!depends & !suggests & !enhances) {
    warning("Returning nothing, since depends, suggests and enhances are all FALSE")
    return(character(0))
  }
  

  pkgInAvail <- pkg %in% availPkgs[, "Package"]
  if (sum(pkgInAvail) == 0 ) stop("No valid packages in pkg")
  if (sum(pkgInAvail) < length(pkg)) {
    warning("Package not recognized: ", paste(pkg[!pkgInAvail], collapse = ", "))
  }

  n_req <- pkg[pkgInAvail]
  n_req_all <- pkg

  # Suggests
  if (suggests) {
    p_sug <- tools::package_dependencies(n_req, availPkgs,
                                         which = "Suggests", recursive = FALSE)
    n_sug <- unique(unname(unlist(p_sug)))
    n_req_all <- c(n_req_all, n_sug)
  } else {
    p_sug <- NA
  }

  # Enhances
  if (enhances) {
    p_enh <- tools::package_dependencies(n_req, availPkgs,
                                         which = "Enhances", recursive = FALSE)
    n_enh <- unique(unname(unlist(p_enh)))
    n_req_all <- c(n_req_all, n_enh)
  } else {
    p_enh <- NA
  }

  # Depends, Imports and LinkingTo
  p_dep <- tools::package_dependencies(n_req_all, availPkgs,
                                       which = c("Depends", "Imports", "LinkingTo"),
                                       recursive = TRUE)
  n_dep <- unique(unname(unlist(p_dep)))

  p_all <- p_dep
  n_all <- unique(c(n_dep, n_req_all))
  n_all <- c(n_req, setdiff(n_all, n_req))

  ret <- n_all
  if(!includeBasePkgs) ret <- ret[!ret %in% basePkgs()]
  attr(ret, "pkgs") <- list(
    n_req = n_req,
    n_all = n_all,
    p_dep = p_dep,
    p_sug = p_sug,
    p_enh = p_enh,
    p_all = p_all
    )
  class(ret) <- c("pkgDep", "character")
  ret
}

#' @export
print.pkgDep <- function(x, ...) {
  attr(x, "pkgs") <- NULL
  class(x) <- "character"
  print(as.vector(x), ...)
}

## <== END FROM miniCRAN

allPkgs <- available.packages(repos=c("https://cran.r-project.org","http://bioconductor.org/packages/release/bioc","https://mc-stan.org/r-packages"))
pkgList <- readLines("modules.desired") 

############## SPECIAL PACKAGE HANDLING ##############
# This is as list of packages that we have precompiled/predownloaded and 
# should not have yamls regenerated. 
#     * Their versions should be in versions.yaml.base
#     * They need to be in modules.bootstrap
# These are usually packages that somehow aren't added correctly to CRAN/Bioconductor

excludePackages = c("GenomeInfoDbData","tmvnsim")

# These are packages where we only archive the yaml and therefore don't overwrite the
# yaml file. Otherwise, normally processed. These are usually cases where we need an
# older version of a package to properly compile. 
#    * They need to have versions in versions.yaml.base

archivePackages = f <- readLines("modules.bootstrap")

#cat(pkgList)
allDeps <- pkgDep(pkgList, availPkgs=allPkgs, suggests=FALSE) 
allDeps <- unique(allDeps)
allDeps <- allDeps[!allDeps %in% excludePackages]

cat(sprintf("## %d desired --> %d required\n", length(pkgList), length(allDeps)))
cat(sprintf("---\n"))
#cat(sprintf("===== allDeps\n"))
#cat(allDeps)
for (pkg in allDeps) 
{
        cat(sprintf("PKG %s\n",pkg),file=stderr())
        tryCatch( {
           deps <- pkgDep(pkg,availPkgs=allPkgs,suggests=FALSE)
           pkgInfo = allPkgs[allPkgs[,"Package"] %in% pkg,]
           # cat(sprintf("INFO %s\n",pkgInfo["Repository"]),file=stderr())
	   cat(sprintf("%s : \n",deps[1]))
	   cat(sprintf("  baseurl : \"%s\"\n",pkgInfo["Repository"]))
	   cat(sprintf("  version : \"%s\"\n",pkgInfo["Version"]))
	   cat(sprintf("  requires : \n"))
           if ( length(deps) > 1 )
               for (i in 2:length(deps))
                   cat(sprintf("    - %s\n",deps[i]))
        },
        error = function(e) {
           cat(sprintf("Caught error %s for PKG %s\n", e, pkg), file=stderr())
	   cat(sprintf("%s : \n",pkg))
	   cat(sprintf("  version :  \"unknown\"\n"))
	   cat(sprintf("  requires : \n"))
        } 
        )
        if (pkg %in%  archivePackages)
        {
            cat(sprintf(" -- PKG %s using archive\n",pkg),file=stderr())
	    cat(sprintf("  archive: True \n"))
        }
        else
        {
	    cat(sprintf("  archive: False \n"))
        }
}
