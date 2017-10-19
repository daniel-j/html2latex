
import re

replacements_head = {}
replacements_tail = {}


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

    return {'start': '\n\n'}


selectors = {
    'html': {'start': '\n\n', 'end': '\n\n'},
    'head': {'ignoreContent': True, 'ignoreStyle': True},
    'body': {'start': '\n\n', 'end': '\n\n'},
    'blockquote': {'start': '\n\\begin{quotation}', 'end': '\n\\end{quotation}'},
    'ol': {'start': '\n\\begin{enumerate}', 'end': '\n\\end{enumerate}'},
    'ul': {'start': '\n\\begin{itemize}', 'end': '\n\\end{itemize}'},
    'li': {'start': '\n\t\item '},
    'i': {'start': '\\textit{', 'end': '}', 'ignoreStyle': True},
    'b, strong': {'start': '\\textbf{', 'end': '}', 'ignoreStyle': True},
    'em': {'start': '\\emph{', 'end': '}', 'ignoreStyle': True},
    'u': {'start': '\\underline{', 'end': '}'},
    'sub': {'start': '$_', 'end': '$'},
    'sup': {'start': '$^', 'end': '$'},
    'br': {'start': '\\\\\n'},
    'p': handle_paragraph,
    '.chapter-name': {'start': '\n\\noindent\\hfil\\charscale[1.7]{\n', 'end': '\n}\\hfil\\newline\n\\vspace*{1\\nbs}\n\n'},
    '.chapter-number': {'start': '\n\\noindent\\hfil\\charscale[1.0]{\\textsc{\\addfontfeature{Ligatures=NoCommon}{', 'end': '}}}\\hfil\\newline\n\\vspace*{0.0\\nbs}\n'},
    'p.break': {'start': '\n\n\scenepause', 'ignoreStyle': True, 'ignoreContent': True}
}

html_entities = {
    u'\u00A0': '\\,',
    u'\u2009': '\\,',
    '&': '\\&',
    '<': '$<$',
    '>': '$>$',
    '\\': '\\textbackslash{}',
    '~': '\\textasciitilde{}',
    '^': '\\textasciicircum{}',
    '%': '\\%',
    '$': '\\$',
    '#': '\\#',
    '_': '\\_',
    '{': '\\{',
    '}': '\\}',

}

styles = {
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
    'margin': {
        '0 2em': ('\n\n\\begin{adjustwidth}{2em}{2em}\n', '\n\\end{adjustwidth}\n\n')
    },
    'margin-top': {
        '1em': ('\n\n\\vspace{\\baselineskip}\n\\noindent\n', '')
    }
}
