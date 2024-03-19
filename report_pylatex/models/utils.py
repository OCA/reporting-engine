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
#
cssutils.log.setLevel(logging.CRITICAL)

def handle_anchor(el):
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


def handle_paragraph(el, parser):
    # hanging indentation
    out="\\begin{center}"
    for child in el:
        out+=parser.element2latex(child)
    out+="\\end{center}"
    return out

def handle_table(table, parser):
    out =''
    for row in table.findall(".//tr"):
        th_s = [parser.element2latex(cell,ignore=['p']) for cell in row.findall(".//th")]
        td_s = [parser.element2latex(cell,ignore=['p']) for cell in row.findall(".//td")]
        if not out:
            column_header_def = " c" * max(len(th_s),len(td_s))
            out+=r"\begin{longtable}{" + column_header_def +"}"
        if th_s:
            out+="&".join(th_s) + r"\\"
        if td_s:
            out+="&".join(td_s) + r"\\"
    out+= r"\end{longtable}"
    return out
    
def s(start='',
      end='',
      ignoreStyle=False,
      ignoreContent=False,
      function=None):
    # helper for generating the selector objects
    return {
        'start': start,
        'end': end,
        'function': function,
        'ignoreStyle': ignoreStyle,
        'ignoreContent': ignoreContent
    }

SECTORS = {
    # defaults
    'html': s('\\thispagestyle{empty}\n{\n', '\n}\n'),
    'head': s(ignoreContent=True, ignoreStyle=True),
    'body': s('\n\n', '\n\n\\clearpage\n\n'),
    'blockquote': s('\n\\begin{quotation}', '\n\\end{quotation}'),
    'ol': s('\n\\begin{enumerate}', '\n\\end{enumerate}'),
    'ul': s('\n\\begin{itemize}', '\n\\end{itemize}'),
    'li': s('\n\t\\item '),
    'i': s('\\textit{', '}', ignoreStyle=True),
    'b, strong': s('\\textbf{', '}', ignoreStyle=True),
    'em': s('\\emph{', '}', ignoreStyle=True),
    'u': s('\\underline{', '}', ignoreStyle=True),
    'sub': s('\\textsubscript{', '}'),
    'sup': s('\\textsuperscript{', '}'),
    'br': s('\\newline\n', ignoreStyle=True,ignoreContent=True),
    'hr': s('\\hrule\n', ignoreStyle=True,ignoreContent=True),
    #'a': s(function=handle_anchor),
    'table': s(function=handle_table,ignoreContent=True),
   
    # customized
    #'p': s(function=handle_paragraph),
    '.chapter-name': s('\n\\noindent\\hfil\\charscale[2,0,-0.1\\nbs]{', '}\\hfil\\newline\n\\vspace*{2\\nbs}\n\n', ignoreStyle=True),
    '.chapter-number': s('\\vspace*{3\\nbs}\n\\noindent\\hfil\\charscale[1.0,0,-0.1\\nbs]{\\textsc{\\addfontfeature{Ligatures=NoCommon,LetterSpace=15}{\\strreplace{', '}{ }{}}}}\\hfil\\newline\n\\vspace*{0.0\\nbs}\n', ignoreStyle=True),
    'p.break': s('\n\n\\scenepause', ignoreStyle=True, ignoreContent=True),
    '.center': s('\n\n{\\csname @flushglue\\endcsname=0pt plus .25\\textwidth\n\\noindent\\centering{}', '\\par\n}', ignoreStyle=True)
}
CHARACHTER = {
    u'\u00A0': '~',  # &nbsp;
    u'\u2009': '\\,',  # &thinsp;
    u'\u2003': '\\hspace*{1em}',  # &emsp;
    '[': '{[}',
    ']': '{]}'
}

STYLES = {
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
        '0': ('\\noindent{}', ''),
        '-1em': ('\\noindent\\hspace*{-1em}', '')
    },
    'text-align': {
        'left': ('\n{\\raggedright{}', '}'),
        'center': ('\n{\\centering{}', '\\par}'),
        'right': ('\n{\\raggedleft{}', '}')
    },
    'text-wrap': {
        'balanced': ('{\\csname @flushglue\\endcsname=0pt plus .25\\textwidth\n', '\n}')
    },
    '-latex-needspace': {
        '2': ('\n\n\\needspace{2\\baselineskip}\n', '')
    },

    'display': {
        'none': s(ignoreContent=True, ignoreStyle=True)
    },

    # customized
    'margin': {
        '0 2em': ('\n\n\\begin{adjustwidth}{2em}{2em}\n', '\n\\end{adjustwidth}\n\n'),
        '0 1em 0 2em': ('\n\n\\begin{adjustwidth}{2em}{1em}\n', '\n\\end{adjustwidth}\n\n'),
        '0 1em': ('\n\n\\begin{adjustwidth}{2em}{2em}\n', '\n\\end{adjustwidth}\n\n')
    },
    'margin-top': {
        '1em': ('\n\n\\vspace{\\baselineskip}\n\\noindent\n', '')
    },
    'margin-bottom': {
        '1em': ('', '\n\n\\vspace{\\baselineskip}\n\\noindent\n')
    },
    '-latex-display': {
        'none': s(ignoreContent=True, ignoreStyle=True)
    }
}


class Html2Latex(object):
    """docstring for Html2Latex"""
    def __init__(self, styles=STYLES,
                 selectors=SECTORS,
                 characters=CHARACHTER,
                 replacements_head={},
                 replacements_tail={}):
        self.styles = styles
        self.selectors = selectors
        self.characters = characters
        self.replacements_head = replacements_head
        self.replacements_tail = replacements_tail


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

    def element2latex(self, el, cascading_style={}, selectors={},ignore=[]):
        if not selectors:
            selectors=self.selectors
        if not cascading_style:
            cascading_style=self.styles
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
        function = False
        tag_element = el.tag.lower()
        if tag_element in ignore:
            sel=None
        else:
            sel = selectors.get(tag_element, None)
        if sel:
            ignoreContent = sel.get('ignoreContent', ignoreContent)
            ignoreStyle = sel.get('ignoreStyle', ignoreStyle)
            leaveText = sel.get('leaveText', leaveText)
            function = sel.get('function')
        if function:
            return function(el, self)
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
                result.append(self.element2latex(child,
                                                 cascading_style,
                                                 selectors,
                                                 ignore=ignore))
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