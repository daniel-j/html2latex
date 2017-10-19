#!/usr/bin/env python3

import sys
import lxml.html
from lxml.cssselect import CSSSelector
import cssutils
import re
from importlib import import_module

sys.path.insert(0, './')
config = import_module('config')

root = lxml.html.parse(
    'test.html',
    parser=lxml.html.HTMLParser(encoding='utf-8', remove_comments=True)
).getroot()

stylesheet = cssutils.parseFile('test.css')


def styleattribute(element):
    "returns css.CSSStyleDeclaration of inline styles, for html: @style"
    cssText = element.get('style')
    if cssText:
        return cssutils.css.CSSStyleDeclaration(cssText=cssText)
    else:
        return None


def getView(document, sheet, media='all', name=None,
            styleCallback=lambda element: None):
    """
    document
        a DOM document, currently an lxml HTML document
    sheet
        a CSS StyleSheet
    media: optional
        TODO: view for which media it should be
    name: optional
        TODO: names of sheets only
    styleCallback: optional
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
            cssselector = CSSSelector(selector.selectorText)
            matching = cssselector.evaluate(document)
            for element in matching:
                # if element.tag in ('div',):
                    # add styles for all matching DOM elements

                    if element not in view:
                        # add initial empty style declatation
                        view[element] = cssutils.css.CSSStyleDeclaration()
                        specificities[element] = {}

                        # and add inline @style if present
                        inlinestyle = styleCallback(element)
                        if inlinestyle:
                            for p in inlinestyle:
                                # set inline style specificity
                                view[element].setProperty(p)
                                specificities[element][p.name] = (1,0,0,0)

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


def getSelectors(document, selectors):
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
                view[element].update(info)
            else:
                head = view[element].get('start', '')
                tail = view[element].get('end', '')
                view[element].update(info)
                #view[element]['head'] = head
                #view[element]['tail'] = tail
    return view


def getChar(ent):
    for e in config.html_entities:
        if e.get('num') == ent or e.get('name') == ent:
            return e.get('convertTo')
    return ''


# def convertCharEntitites(string):
#     entity = ""

#     i = 0
#     addToBuffer = False
#     while i < len(string):
#         # new entity started
#         if string[i] == '&':
#             addToBuffer = True
#             entity = ''
#             i += 1
#             continue

#         if addToBuffer and string[i] == ';':
#             # find symbol
#             repl = ''

#             if entity[0] == '#':
#                 entityNum = 0
#                 if entity[1].lower() == 'x':
#                     entityNum = int(entity[2:], 16)
#                 else:
#                     entityNum = int(entity[1:], 10)
#                 repl = getChar(entityNum)
#             else:
#                 repl = getChar(entity)
#             if repl:
#                 string = string.replace("&" + entity + ";", repl)
#                 i += len(repl) - (len(entity) + 2)

#             addToBuffer = False
#             entity = ''
#             i += 1
#             continue

#         if addToBuffer:
#             entity += string[i]
#         i += 1

#     return string


def convertLaTeXSpecialChars(string):
    string = string \
        .replace("\\", "@-DOLLAR-\\backslash@-DOLLAR-") \
        .replace("&#", "&@-HASH-") \
        .replace("$", "\\$").replace("#", "\\#") \
        .replace("%", "\\%").replace("~", "\\textasciitilde") \
        .replace("_", "\\_").replace("^", "\\textasciicircum") \
        .replace("{", "\\{").replace("}", "\\}") \
        .replace("@-DOLLAR-", "$") \
        .replace("@-HASH-", "#")
    return string


def characters(string, leaveText, ignoreContent):
    if not leaveText:
        string = string.replace('\n', ' ').replace('\t', ' ')

    if string.strip() == '' or ignoreContent:
        return ''

    if leaveText:
        string = convertLaTeXSpecialChars(string)
    # string = convertCharEntitites(string)
    s = list(string)
    for i, char in enumerate(s):
        if char in config.html_entities:
            s[i] = config.html_entities.get(char)
    return ''.join(s)


def html2latex(el):
    if False:
        print('tag', el.tag)
        if el.text:
            print('text "'+el.text.replace('\n', ' ')+'"')
        if el.tail:
            print('tail "'+el.tail.replace('\n', ' ')+'"')
        print('attrib', el.attrib)
        print()
    result = []
    heads = []
    tails = []

    declarations = cascadingStyle.get(el, [])
    # htmlfunc = getattr(config, 'element_'+el.tag.lower(), None)
    ignoreContent = False
    ignoreStyle = False
    leaveText = False

    # if htmlfunc:
    #     o = htmlfunc(el, declarations) if callable(htmlfunc) else htmlfunc
    #     heads.insert(0, o.get('head', ''))
    #     tails.append(o.get('tail', ''))
    #     ignoreContent = o.get('ignoreContent', ignoreContent)
    #     ignoreStyle = o.get('ignoreStyle', ignoreStyle)
    #     leaveText = o.get('leaveText', leaveText)

    sel = selectors.get(el, None)
    if sel:
        heads.insert(0, sel.get('start', ''))
        tails.append(sel.get('end', ''))
        ignoreContent = sel.get('ignoreContent', ignoreContent)
        ignoreStyle = sel.get('ignoreStyle', ignoreStyle)
        leaveText = sel.get('leaveText', leaveText)

    if not ignoreStyle:
        for d in declarations:
            style = config.styles.get(d.name.lower(), None)
            if style:
                if callable(style):
                    style = style(d.name.lower(), d.value, el)
                else:
                    style = style.get(d.value, None)
                    if callable(style):
                        style = style(d.name.lower(), d.value, el)
                if style:
                    heads.append(style[0])
                    tails.insert(0, style[1])
            # print(d.name+': '+d.value)

    result.append(''.join(heads))

    if not ignoreContent:
        if el.text:
            text = characters(el.text, leaveText, ignoreContent)
            r = config.replacements_head.get(el, None)
            if r:
                text = re.sub(r[0], r[1], text)
            result.append(text)
        for child in el:
            result.append(html2latex(child))
            if child.tail:
                text = characters(child.tail, leaveText, ignoreContent)
                r = config.replacements_tail.get(el, None)
                if r:
                    text = re.sub(r[0], r[1], text)
                result.append(text)

    result.append(''.join(tails))
    return ''.join(result)


cascadingStyle = getView(root, stylesheet, styleCallback=styleattribute)
selectors = getSelectors(root, config.selectors)
out = html2latex(root)
with open('test.tex', 'w') as f:
    f.write(out)
# print(out)
