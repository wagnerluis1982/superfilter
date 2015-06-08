#!/usr/bin/env python
import re

import pandocfilters as pf

# useful regular expressions
RE_FLOAT = r'(?:[0-9]+\.?|\.[0-9])[0-9]*'

def parse_options(s):
    if s:
        opts = re.split(r' *, *', s)
        return dict([re.split(r' *= *', opt) for opt in opts])


def latex_join(values, sep):
    output = [values[0]]
    for i in range(1, len(values)):
        last = output[-1]
        curr = values[i]
        if last['t'] == curr['t'] == "RawBlock" \
                and last['c'][0] == curr['c'][0] == "latex":
            output[-1] = latex(last['c'][1] + sep + curr['c'][1])
        else:
            output.append(values[i])

    return output


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


def put_subfigures(images):
    output = []
    options = {'width': '1'}
    for (uri, caption) in images:
        subopts = {'width': '1'}
        uri_has_args = re.findall(r'^(.*?)(?:%20)*\|(?:%20)*(.*)$', uri)
        if uri_has_args:
            uri, args = uri_has_args[0]
            subopts = parse_options(args)

        output.extend([latex(r'\begin{subfigure}[b]{%s\linewidth}' '\n'
                             % subopts['width']),
                       put_image(uri, options),
                       put_caption(caption),
                       latex(r'\end{subfigure}')])
    return latex_join(output, '\n')


def split(s, sep, maxsplit):
    explode = s.split(sep, maxsplit)
    while len(explode) <= maxsplit:
        explode.append('')
    return explode


def do_filter(k, v, f, m):
    if k == "Para":
        value = pf.stringify(v)

        # Colunas no slide
        if f == 'beamer':
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

        # Subfiguras
        if not _.is_figure:
            if value == '<[figures]':
                _.is_figure = True
                return latex(r'\begin{figure}[ht]' '\n' r'\centering')
        else:
            if value == '[figures]>':
                _.is_figure = False
                return latex(r'\end{figure}')
            if v[0]['t'] == "Str" and v[0]['c'] == "Caption:" \
                    and v[1]['t'] == "Space":
                return put_caption(v[2:])
            if len(v) >= 1 and v[0]['t'] == "Image":
                images = []
                for i in range(len(v)):
                    if v[i]['t'] == "Image":
                        uri = v[i]['c'][1][0]
                        caption = v[i]['c'][0]
                        images.append((uri, caption))
                return put_subfigures(images)

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

    # Special citations
    elif k == "Cite":
        kind = ''
        citations = []
        for bib in v[0]:
            citeid, ki = split(bib['citationId'], '#', 1)
            kind = ki or kind
            citations.append(citeid)
            bib['citationId'] = citeid

        bibid = ','.join(citations)
        if kind:
            return inlatex(r'\cite%s{%s}' % (kind, bibid))
        else:
            return pf.Cite(*v)


# flags
_ = do_filter
_.is_columns = False
_.is_figure = False


if __name__ == "__main__":
    pf.toJSONFilter(do_filter)
