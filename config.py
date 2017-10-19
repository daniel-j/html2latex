
import re

replacements_head = {}
replacements_tail = {}


def s(start='', end='', ignoreStyle=False, ignoreContent=False):
    # helper for generating the selector objects
    return {
        'start': start,
        'end': end,
        'ignoreStyle': ignoreStyle,
        'ignoreContent': ignoreContent
    }


def handle_hyperlink(selector, el):
    href = el.get('href')
    name = el.get('name')

    if hyperlinks == 'hyperref':
        start = ''
        end = ''
        if href and href.startswith('#'):
            start = '\\hyperlink{' + href[1:] + '}{'
            end = '}'
        elif name:
            start = '\\hypertarget{' + name + '}{'
            end = '}'
        elif href:
            start = '\\href{' + href + '}{'
            end = '}'
        return s(start, end)
    elif hyperlinks == 'footnotes':
        if href and not href.startswith('#'):
            return s(end='\\footnote{' + href + '}')
    return None


def handle_paragraph(selector, el):
    # hanging indentation
    match = r'^“'
    node = el
    while True:
        if node.text and re.match(match, node.text):
            replacements_head[node] = (match, '\\indent\\llap{“}')
            break
        elif not node.text and node.__len__() > 0:
            node = node[0]
        else:
            break

    return s('\n\n')


# Available options: None, hyperref, footnotes
hyperlinks = None

selectors = {
    # defaults
    'html': s('\n\n', '\n\n'),
    'head': s(ignoreContent=True, ignoreStyle=True),
    'body': s('\n\n', '\n\n'),
    'blockquote': s('\n\\begin{quotation}', '\n\\end{quotation}'),
    'ol': s('\n\\begin{enumerate}', '\n\\end{enumerate}'),
    'ul': s('\n\\begin{itemize}', '\n\\end{itemize}'),
    'li': s('\n\t\item '),
    'i': s('\\textit{', '}', ignoreStyle=True),
    'b, strong': s('\\textbf{', '}', ignoreStyle=True),
    'em': s('\\emph{', '}', ignoreStyle=True),
    'u': s('\\underline{', '}', ignoreStyle=True),
    'sub': s('\\textsubscript{', '}'),
    'sup': s('\\textsuperscript{', '}'),
    'br': s('\\\\\n'),
    'hr': s('\n\n\\line(1,0){300}\n', ignoreStyle=True),
    'a': handle_hyperlink,

    # customized
    'p': handle_paragraph,
    '.chapter-name': s( '\n\\noindent\\hfil\\charscale[1.7]{\n', '\n}\\hfil\\newline\n\\vspace*{1\\nbs}\n\n'),
    '.chapter-number': {'start': '\n\\noindent\\hfil\\charscale[1.0]{\\textsc{\\addfontfeature{Ligatures=NoCommon}{', 'end': '}}}\\hfil\\newline\n\\vspace*{0.0\\nbs}\n'},
    'p.break': {'start': '\n\n\scenepause', 'ignoreStyle': True, 'ignoreContent': True}
}

html_entities = {
    u'\u00A0': '\\,',
    u'\u2009': '\\,',
    '&': '\\&'
}

styles = {
    # defaults
    'font-weight': {
        'bold': ('\\textbf{', '}'),
        'bolder': ('\\textbf{', '}')
    },
    'font-style': {
        'italic': ('\\textit{', '}')
    },
    'font-variant': {
        'small-caps': ('\\textsc{', '}')
    },
    'text-indent': {
        '0': ('\\noindent ', '')
    },
    'text-align': {
        'center': ('\n{\centering\n', '\n}\n')
    },
    'page-break-inside': {
        'avoid': ('\n\n\\begin{samepage}\n\n', '\n\n\\end{samepage}\n\n')
    },

    # customized
    'margin': {
        '0 2em': ('\n\n\\begin{adjustwidth}{2em}{2em}\n', '\n\\end{adjustwidth}\n\n')
    },
    'margin-top': {
        '1em': ('\n\n\\vspace{\\baselineskip}\n\\noindent\n', '')
    }
}
