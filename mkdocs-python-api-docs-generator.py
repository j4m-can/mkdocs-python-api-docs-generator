#! /usr/bin/env python3
#
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# mkdocs-python-api-docs-generator.py


"""Someone must have something like this. But I could not find it.

Pass a path to Python code and a path to where the docs should be.
Markdown files are created for each .py file (for __init__.py for
directories). An updated mkdocs.yml-new is provided with a
basic "nav" setup.
"""


import io
import os
import os.path
import shutil
import sys
import time
import yaml


MKDOCS_FILENAME = "mkdocs.yml"


def print_usage():
    progname = os.path.basename(sys.argv[0])
    print(f"""\
usage: {progname} <srcpath> <docspath>
       {progname} -h|--help

Generate mkdocs-compatible markup documents from Python source code
tree.""")


def generate_home_index(srcpath, dstpath):
    """Generate the home/toplevel index.md.
    """

    mkdocs_yaml = yaml.safe_load(open(mkdocs_filename))
    basename = os.path.basename(srcpath)

    print(f"""# {mkdocs_yaml.get("site_name", "Unnamed")}

Generated: {time.asctime()}

## Package: [{basename}]({basename})
""", file=open(f"{dstpath}/index.md", "w"))


def update_docs(srcpath, dstpath):
    """Update docs directory at dstpath from Python code at srcpath.

    Return navpaths which is an ordered list of paths encountered.
    """

    navpaths = []

    srccomps = srcpath.split("/")
    nsrccomps = len(srccomps)

    basedir = os.path.dirname(srcpath)
    basename = os.path.basename(srcpath)

    try:
        os.makedirs(f"{dstpath}/{basename}")
    except:
        pass

    for dirpath, dirnames, filenames in os.walk(srcpath):
        # don't fiddle with dirnames object so that walk can adjust to
        # changes to dirnames

        navpaths.append(dirpath)

        dstdirpath = dstpath+"/"+dirpath[len(basedir):]

        # filter dirnames (in place)
        for i, dirname in list(enumerate(dirnames[:]))[::-1]:
            if dirname in ["__pycache__"]:
                print(f"deleting i ({i}) dirname ({dirname}) dirnames[i] ({dirnames[i]}")
                del dirnames[i]
        _dirnames = sorted(dirnames)

        # filter filenames (in place)
        for i, filename in list(enumerate(filenames[:]))[::-1]:
            if not filename.endswith(".py") or filename in ["__init__.py"]:
                del filenames[i]
        _filenames = sorted(filenames)

        print(dirpath, dirnames, filenames)
        print(dstdirpath)
        print("-----")

        # create dstdirpath for md files
        try:
            os.makedirs(dstdirpath)
        except FileExistsError:
            print(f"directory ({dstdirpath}) already exists")


        with open(f"{dstdirpath}/index.md", "w") as f:
            # this package
            print("creating index.md for package ({pkgname})")
            pkgname = dirpath.replace("/", ".")

            # need a newline on first line for heading to get picked up!
            f.write(f"\n# Package: {pkgname}\n\n")
            f.write(f"::: {pkgname}\n")
            f.write("\n-----\n\n")

            if _dirnames:
                # list subpackages
                print("listing subpackages ...")
                f.write("## Subpackages\n\n")
                for dirname in _dirnames:
                    f.write(f"* [{dirname}]({dirname})\n")

                f.write("\n")

            if _filenames:
                print("listing modules ...")

                # list modules and create an md file per module
                f.write("## Modules\n\n")
                for name in _filenames:
                    shortname = name[:-3]
                    f.write(f"* [{shortname}]({shortname}.md)\n")

                    print(f"creating md file for module ({shortname})")
                    dstfilename = dstdirpath+"/"+shortname+".md"
                    with open(dstfilename, "w") as ff:
                        # newline on first line
                        ff.write(f"\n# Module: {pkgname}.{shortname}\n\n")
                        ff.write(f"::: {pkgname}.{shortname}")

    return navpaths


def update_mkdocs_yaml(mkdocs_filename, navpaths):
    """Update the "nav" part of the mkdocs.yaml file.
    """

    INDENT = "  "

    l = [
        f"{INDENT}- Home: index.md",
    ]

    for navpath in sorted(navpaths):
        comps = navpath.split("/")
        indent = INDENT*len(comps)
        l.append(f"{indent}- {comps[-1]}:")
        l.append(f"{indent}  - index: {navpath}/index.md")

    mkdocs_yaml = yaml.safe_load(open(mkdocs_filename))
    nav_yaml = yaml.safe_load(io.StringIO("\n".join(l)))

    if "nav" in mkdocs_yaml:
        del mkdocs_yaml["nav"]

    mkdocs_yaml["nav"] = nav_yaml

    # don't overwrite original
    yaml.dump(mkdocs_yaml, open(f"{mkdocs_filename}-new", "w"))


if __name__ == "__main__":
    try:
        args = sys.argv[1:]

        if args[0] in ["-h", "--help"]:
            print_usage()
            sys.exit(0)

        srcpath = args.pop(0)
        dstpath = args.pop(0)

        mkdocs_filename = MKDOCS_FILENAME
        if args:
            mkdocs_filename = args.pop(0)
    except SystemExit:
        raise
    except:
        print("error: bad/missing argument", file=sys.stderr)
        sys.exit(1)

    try:
        navpaths = update_docs(srcpath, dstpath)
        generate_home_index(srcpath, dstpath)
        update_mkdocs_yaml(mkdocs_filename, navpaths)
    except Exception as e:
        print(f"failed with exception ({e})", file=sys.stderr)
        sys.exit(1)

