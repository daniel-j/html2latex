html2latex
==========

Dependencies
------------
Install on Arch Linux: `# pacman -S python3 python-lxml python-cssutils python-cssselect`

Usage
-----
`html2latex.py [--input HTML FILE] [--output TEX FILE] [--style CSS FILE] [--config CONFIG FILE]`

* To convert a HTML/XHTML file to LaTeX:
`./html2latex.py --style stylesheet.css --input document.html --output document.tex`
* To convert several HTML files at once, just add more `--input` and `--output` arguments:
`./html2latex.py --style stylesheet.css --input document.html --output document.tex --input other.xhtml --output other.tex`

Configuration
-------------
Make a copy of `config.py` and modify it.

Examples:
```python

# Available options: hyperref, footnotes or None
hyperlinks = None

selectors = {
    ...
    # 'em' is a CSS selector. You can use any valid CSS3 selector
    # First argument is what replaces <em>
    # Second argument is what replaces </em>
    # ignoreStyle means that no other CSS styling will be applied to this element.
    # Don't forget to escape backslashes in strings!
    # s() is a helper function defined in config.py
    'em': s('\\emph{', '}', ignoreStyle=True)
    ...
}

characters = {
    ...
    # Replace characters with their LaTeX equivalents.
    # Use u'\u1234' for matching unicode characters.
    # HTML entities are decoded. LaTeX special characters are already escaped.
    u'\u2009': '\\,'
    ...
}

styles = {
    ...
    'text-indent': {
        # If an element is matched with having text-indent: 0; in the CSS, \noindent is prepended in the output.
        '0': ('\\noindent ', ''),
    }
    ...
}
```