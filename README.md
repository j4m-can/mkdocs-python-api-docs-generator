# Mkdocs Python API Docs Generator

Generates markdown files for Python packages and modules that should be
processed by ```mkdocstrings```.

This program does not do anything with the actual Python packages or modules.
That is left up to ```mkdocstrings```. Instead it creates directories under
```docs/``` (if that is specified), markdown files with links and directives,
and provides an updated the ```mkdocs.yml``` at ```mkdocs.yml-new``` with the
```nav``` section set up.

## Requirements

```mkdocs``` and ```mkdocstrings``` must be installed. See ```pip```.
