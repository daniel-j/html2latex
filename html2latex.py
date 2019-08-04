#!/usr/bin/env python3

# created by djazz
# https://github.com/daniel-j/html2latex

import lxml.html
from lxml.cssselect import CSSSelector, ExpressionError
import cssutils
import re
import argparse
import os.path

import logging
cssutils.log.setLevel(logging.CRITICAL)


class Html2Latex(object):
    """docstring for Html2Latex"""
    def __init__(self, styles={}, selectors={}, characters={},
                 replacements_head={}, replacements_tail={},
                 input_files=[], output_files=[], css_files=[],
                 disable_style_tags=False):
        super(Html2Latex, self).__init__()

        self.styles = styles
        self.selectors = selectors
        self.characters = characters
        self.replacements_head = replacements_head
        self.replacements_tail = replacements_tail

        self.inputFiles = input_files
        self.outputFiles = output_files
        self.cssFiles = css_files
        self.disable_style_tags = disable_style_tags

    def get_char(self, ent):
        for e in self.characters:
            if e.get('num') == ent or e.get('name') == ent:
                return e.get('convertTo')
        return ''

    def inside_characters(self, el, string, leaveText=False, ignoreContent=False):
        string = self.modify_characters(el, string, leaveText)
        if string.strip() == '' or ignoreContent:
            return ''
        return string

    def modify_characters(self, el, string, leaveText=False):
        if not leaveText:
            string = string.replace('\n', ' ').replace('\t', ' ')
            string = re.sub('[ ]+', ' ', string)

        string = convertLaTeXSpecialChars(string)
        # string = convertCharEntitites(string)
        s = list(string)
        for i, char in enumerate(s):
            if char in self.characters:
                s[i] = self.characters.get(char)
                if callable(s[i]):
                    s[i] = s[i](el, i, char)
        return ''.join(s)

    def element2latex(self, el, cascading_style, selectors):
        if False:
            print('tag', el.tag)
            if el.text:
                print('text "' + el.text.replace('\n', ' ') + '"')
            if el.tail:
                print('tail "' + el.tail.replace('\n', ' ') + '"')
            print('attrib', el.attrib)
            print()
        result = []
        heads = []
        tails = []

        # and add inline @style if present
        inlinestyle = styleattribute(el)
        if inlinestyle:
            for p in inlinestyle:
                if el not in cascading_style:
                    # add initial empty style declatation
                    cascading_style[el] = cssutils.css.CSSStyleDeclaration()
                # set inline style specificity
                cascading_style[el].setProperty(p)
                # specificities[el][p.name] = (1,0,0,0)

        declarations = cascading_style.get(el, [])
        # htmlfunc = getattr(config, 'element_'+el.tag.lower(), None)
        ignoreContent = False
        ignoreStyle = False
        leaveText = False

        sel = selectors.get(el, None)
        if sel:
            ignoreContent = sel.get('ignoreContent', ignoreContent)
            ignoreStyle = sel.get('ignoreStyle', ignoreStyle)
            leaveText = sel.get('leaveText', leaveText)

        if not ignoreStyle:
            for d in declarations:
                style = self.styles.get(d.name.lower(), None)
                if style:
                    if callable(style):
                        style = style(d.name.lower(), d.value, el)
                    else:
                        style = style.get(d.value, None)
                        if callable(style):
                            style = style(d.name.lower(), d.value, el)
                    if style:
                        if type(style) is tuple:
                            heads.append(style[0])
                            tails.insert(0, style[1])
                        else:
                            heads.append(style.get('start', ''))
                            tails.insert(0, style.get('end', ''))
                            ignoreContent = style.get('ignoreContent', ignoreContent)
                            ignoreStyle = style.get('ignoreStyle', ignoreStyle)
                            leaveText = style.get('leaveText', leaveText)
                # print(d.name+': '+d.value)
        if ignoreStyle:
            heads.clear()
            tails.clear()
        if sel:
            heads.insert(0, sel.get('start', ''))
            tails.append(sel.get('end', ''))

        result.append(''.join(heads))

        if not ignoreContent:
            if el.text:
                text = self.inside_characters(el, el.text, leaveText, ignoreContent)
                r = self.replacements_head.get(el, None)
                if r:
                    text = re.sub(r[0], r[1], text)
                result.append(text)
            for child in el:
                result.append(self.element2latex(child, cascading_style, selectors))
                if child.tail:
                    text = self.modify_characters(child, child.tail)
                    r = self.replacements_tail.get(el, None)
                    if r:
                        text = re.sub(r[0], r[1], text)
                    result.append(text)

        result.append(''.join(tails))
        result = ''.join(result)
        # strip whitespace at the start and end of lines
        return '\n'.join(map(str.strip, result.split('\n')))

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', action='append', default=[])
        parser.add_argument('--output', action='append', default=[])
        parser.add_argument('--style', action='append', default=[])
        parser.add_argument('--disable-style-tags', action='store_true')
        args = parser.parse_args()
        self.inputFiles = args.input
        self.outputFiles = args.output
        self.cssFiles = args.style
        self.disable_style_tags = args.disable_style_tags
        return self

    def run(self):
        assert len(self.inputFiles) == len(self.outputFiles)

        externalStyle = []
        if self.cssFiles:
            # print('Parsing stylesheets...')
            for f in self.cssFiles:
                with open(f, 'r') as stylefile:
                    externalStyle.append(stylefile.read())
        externalStyle = '\n'.join(externalStyle)

        styleparser = cssutils.CSSParser(validate=False, parseComments=False)

        htmlParser = lxml.html.HTMLParser(encoding='utf-8', remove_comments=True)
        for i in range(0, len(self.inputFiles)):
            inputFile = self.inputFiles[i]
            outputFile = self.outputFiles[i]
            print('Converting ' + inputFile + ' to ' + outputFile)
            root = lxml.html.parse(inputFile, parser=htmlParser).getroot()
            documentStyle = ''
            if not self.disable_style_tags:
                documentStyle = '\n'.join([style.text for style in root.getchildren()[0].findall('style')])
            stylesheet = styleparser.parseString(externalStyle + documentStyle, href="file://"+os.path.abspath(inputFile))
            cascading_style = get_view(root, stylesheet, style_callback=styleattribute)
            selectors = get_selectors(root, self.selectors)
            out = self.element2latex(root, cascading_style, selectors)
            with open(outputFile, 'w') as f:
                f.write(out)
        return self


def styleattribute(element):
    # returns css.CSSStyleDeclaration of inline styles, for html: @style
    value = element.get('style')
    if value:
        return cssutils.css.CSSStyleDeclaration(cssText=value)
    else:
        return None


def get_view(document, sheet, name=None,
             style_callback=lambda element: None):
    """
    document
        a DOM document, currently an lxml HTML document
    sheet
        a CSS StyleSheet
    name: optional
        TODO: names of sheets only
    style_callback: optional
        should return css.CSSStyleDeclaration of inline styles, for html
        a style declaration for ``element@style``. Gets one parameter
        ``element`` which is the relevant DOMElement

    returns style view
        a dict of {DOMElement: css.CSSStyleDeclaration} for html
    """

    view = {}
    specificities = {}  # needed temporarily

    # TODO: filter rules simpler?, add @media
    rules = (rule for rule in sheet if rule.type == rule.STYLE_RULE)
    for rule in rules:
        for selector in rule.selectorList:
            # TODO: make this a callback to be able to use other stuff than lxml
            try:
                cssselector = CSSSelector(selector.selectorText)
            except ExpressionError:
                continue
            matching = cssselector.evaluate(document)

            for element in matching:
                # if element.tag in ('div',):
                    # add styles for all matching DOM elements

                    if element not in view:
                        # add initial empty style declatation
                        view[element] = cssutils.css.CSSStyleDeclaration()
                        specificities[element] = {}

                    for p in rule.style:
                        # update style declaration
                        if p not in view[element]:
                            # setProperty needs a new Property object and
                            # MUST NOT reuse the existing Property
                            # which would be the same for all elements!
                            # see Issue #23
                            view[element].setProperty(p.name, p.value, p.priority)
                            specificities[element][p.name] = selector.specificity

                        else:
                            sameprio = (p.priority ==
                                        view[element].getPropertyPriority(p.name))
                            if not sameprio and bool(p.priority) or (
                               sameprio and selector.specificity >=
                                    specificities[element][p.name]):
                                # later, more specific or higher prio
                                view[element].setProperty(p.name, p.value, p.priority)
    return view


def get_selectors(document, selectors):
    view = {}
    for selector in selectors:
        val = selectors.get(selector)
        cssselector = CSSSelector(selector)
        matching = cssselector.evaluate(document)
        # print(selector, info)
        for element in matching:
            info = val
            if callable(val):
                info = val(selector, element)
            if element not in view:
                view[element] = {}
                if info:
                    view[element].update(info)
            else:
                # head = view[element].get('start', '')
                # tail = view[element].get('end', '')
                if info:
                    view[element].update(info)
    return view


def convertLaTeXSpecialChars(string):
    string = string \
        .replace("{", "\\{").replace("}", "\\}") \
        .replace("\\", "\\textbackslash{}") \
        .replace("&#", "&@-HASH-") \
        .replace("$", "\\$").replace("#", "\\#") \
        .replace("%", "\\%").replace("~", "\\textasciitilde{}") \
        .replace("_", "\\_").replace("^", "\\textasciicircum{}") \
        .replace("@-HASH-", "#").replace("&", "\\&")
    return string
