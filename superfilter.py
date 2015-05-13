#!/usr/bin/env python
import re

import pandocfilters as pf

# useful regular expressions
RE_FLOAT = r'(?:[0-9]+\.?|\.[0-9])[0-9]*'

def parse_options(s):
    if s:
        opts = re.split(r' *, *', s)
        return dict([re.split(r' *= *', opt) for opt in opts])


def latex(s):
    return pf.RawBlock('latex', s)


def inlatex(s):
    return pf.RawInline('latex', s)


def put_image(uri, options):
    if options:
        width = options['width']
        if re.match(r'^%s$' % RE_FLOAT, width):
            return latex(r'\includegraphics[width=%s\linewidth]{%s}' %
                         (width, uri))
        else:
            return latex(r'\includegraphics[width=%s]{%s}' %
                         (width, uri))
    else:
        return latex(r'\includegraphics{%s}' % uri)


def put_caption(s):
    if s:
        return pf.Para([inlatex(r'\caption{')] + s + [inlatex('}')])
    else:
        return pf.Null()


def put_figure(uri, caption):
    star = ''
    if uri[0] == '*':
        star = '*'
        uri = uri[1:]

    options = None
    uri_has_args = re.findall(r'^(.*?)(?:%20)*\|(?:%20)*(.*)$', uri)
    if uri_has_args:
        uri, args = uri_has_args[0]
        options = parse_options(args)

    if star or options:
        return [latex(r'\begin{figure%s}[ht]' '\n' r'\centering' % star),
                put_image(uri, options),
                put_caption(caption),
                latex(r'\end{figure%s}' % star)]


def do_filter(k, v, f, m):
    if k == "Para":
        if f == 'beamer':
            # Colunas no slide
            value = pf.stringify(v)
            if not _.is_columns:
                # Inicia bloco 'columns'
                if value == '<[columns]':
                    _.is_columns = True
                    return latex(r'\begin{columns}')
            else:
                # Termina bloco 'columns'
                if value == '[columns]>':
                    _.is_columns = False
                    return latex(r'\end{columns}')
                # Demarca uma coluna
                m = re.match(r'^\[\[\[ *(%s) *\]\]\]$' % RE_FLOAT, value)
                if m:
                    return latex(r'\column{%s\textwidth}' % m.group(1))

        # Imagens com largura informada
        if len(v) == 1 and v[0]['t'] == "Image":
            uri = v[0]['c'][1][0]
            caption = v[0]['c'][0]
            return put_figure(uri, caption)

    elif k == "RawInline" and v[0] == "html":
        # Anchor (\label)
        m = re.match(r'^<anchor:#(.*?)>', v[1])
        if m:
            return [inlatex(r'\label{%s}' % m.group(1))]

        # Reference link (\ref)
        m = re.match(r'^<ref:#(.*?)>', v[1])
        if m:
            return [inlatex(r'\ref{%s}' % m.group(1))]

        # Page reference link (\pageref)
        m = re.match(r'^<pageref:#(.*?)>', v[1])
        if m:
            return [inlatex(r'\pageref{%s}' % m.group(1))]

    # Math with anchors
    elif k == "Math" and v[0]['t'] == "DisplayMath":
        pos = v[1].find('#')
        # Return math without changes
        if pos == -1:
            return {'t': k, 'c': v}
        # Return math inside an equation environment
        else:
            anchor = v[1][pos+1:].strip()
            math = v[1][:pos]
            return inlatex(r'\begin{equation}\label{%s}'
                           '\n%s\n'
                           r'\end{equation}' % (anchor, math))


# flags
_ = do_filter
_.is_columns = False


if __name__ == "__main__":
    pf.toJSONFilter(do_filter)
