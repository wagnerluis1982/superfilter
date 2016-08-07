#!/usr/bin/env python
import sys
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
        graphargs = []
        if 'width' in options:
            width = options['width']
            if re.match(r'^%s$' % RE_FLOAT, width):
                graphargs.append(r'width=%s\linewidth' % width)
            else:
                graphargs.append(r'width=%s' % width)
        elif 'height' in options:
            height = options['height']
            if re.match(r'^%s$' % RE_FLOAT, height):
                graphargs.append(r'height=%s\textheight' % height)
            else:
                graphargs.append(r'height=%s' % height)
        return latex(r'\includegraphics[%s]{%s}' % (','.join(graphargs), uri))
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
    uri_has_args = re.findall(r'^(.*?)(?:%20)*%7C(?:%20)*(.*)$', uri)
    if uri_has_args:
        uri, args = uri_has_args[0]
        options = parse_options(args)

    if star or options:
        return [latex(r'\begin{figure%s}[htbp]' '\n' r'\centering' % star),
                put_image(uri, options),
                put_caption(caption),
                latex(r'\end{figure%s}' % star)]


def put_subfigures(images):
    output = []
    options = {'width': '1'}
    for (uri, caption) in images:
        subopts = {'width': '1'}
        uri_has_args = re.findall(r'^(.*?)(?:%20)*%7C(?:%20)*(.*)$', uri)
        if uri_has_args:
            uri, args = uri_has_args[0]
            subopts = parse_options(args)

        output.extend([latex(r'\begin{subfigure}[b]{%s\linewidth}' '\n'
                             % subopts['width']),
                       put_image(uri, options),
                       put_caption(caption),
                       latex(r'\end{subfigure}')])
    return latex_join(output, '\n')


def tbl_caption(s):
    return pf.Para([inlatex(r'\caption{')] + s + [inlatex('}')])


def tbl_alignment(s, h):
    aligns = {
        "AlignDefault": 'l',
        "AlignLeft": 'l',
        "AlignCenter": 'c',
        "AlignRight": 'r',
    }
    params = []
    for se, he in zip(s, h):
        # last element at this column header title
        try:
            last = he[0]['c'][-1]
        except IndexError:
            last = {'t': None}
        if last['t'] == "Str" and re.match(r'^\{.+?\}$', last['c']):
            del he[0]['c'][-(1 + (he[0]['c'][-2]['t'] == "Space")):]
            if re.match(r'^\{%s\}$' % RE_FLOAT, last['c']):
                params.append('p' + last['c'][:-1] + r'\textwidth}')
            else:
                params.append('p' + last['c'])
        else:
            params.append(aligns[se['t']])
    return ''.join(params)


def tbl_headers(s):
    try:
        result = s[0][0]['c'][:]
    except IndexError:
        result = []
    for i in range(1, len(s)):
        result.append(inlatex(' & '))
        try:
            result.extend(s[i][0]['c'])
        except IndexError:
            pass
    result.append(inlatex(r' \\\midrule'))
    return pf.Para(result)


def tbl_contents(s):
    result = []
    for row in s:
        para = []
        for col in row:
            para.extend(col[0]['c'])
            para.append(inlatex(' & '))
        result.extend(para)
        result[-1] = inlatex(r' \\' '\n')
    return pf.Para(result)


def has_table_option(cap, option):
    return get_table_option(cap, option) is not None


def get_table_option(cap, option):
    if not (cap and cap[0]['t'] == "Str"):
        return
    s = cap[0]['c']
    if s[0] == '{' and s[-1] == '}':
        m = re.search(r'\b(%s)=?([^,]+)?\b' % option, s)
        if m:
            return m.group(2) or ''


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
                return latex(r'\begin{figure}[tbp]' '\n' r'\centering')
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
        # Return math without changes if no anchor was found
        if pos == -1:
            return
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

    elif k == "Table":
        cap = v[0]
        # Coloca uma imagem como tabela
        tbl_image = get_table_option(cap, 'from')
        if tbl_image is not None:
            cap.pop(0)
            return [latex(r'\begin{table}[tbp]' '\n' r'\centering' '\n'),
                    tbl_caption(cap),
                    put_image(tbl_image, None),
                    latex(r'\end{table}')]
        # Usa longtable, mas a coloca na proxima pagina
        if has_table_option(cap, 'longtable'):
            cap.pop(0)
            return [latex(r'\afterpage{'),
                    pf.Table(*v),
                    latex(r'}')]
        # Coloca as tabelas em ambientes table comuns
        elif len(sys.argv) > 1 and sys.argv[1] == "--table":
            place = get_table_option(cap, 'place')
            if place is not None:
                cap.pop(0)
            else:
                place = 'tbp'
            return [latex(r'\begin{table}[%s]' '\n'
                          r'\centering' '\n' % place),
                    tbl_caption(cap),
                    latex(r'\begin{tabular}{@{}%s@{}}' %
                        tbl_alignment(v[1], v[3]) +
                        ('\n' r'\toprule')),
                    tbl_headers(v[3]),
                    tbl_contents(v[4]),
                    latex(r'\bottomrule' '\n' r'\end{tabular}'),
                    latex(r'\end{table}')]

    # Envolve codigos com caption no environment 'codigo'
    elif k == "CodeBlock":
        attrs = dict(v[0][2])
        if "caption" in attrs:
            objs = [latex(r'\begin{codigo}'), pf.CodeBlock(*v),
                   latex(r'\caption{%s}' % attrs["caption"])]
            if "label" in attrs:
                objs.append(latex(r'\label{%s}' % attrs["label"]))
            objs.append(latex(r'\end{codigo}'))
            return objs


# flags
_ = do_filter
_.is_columns = False
_.is_figure = False


if __name__ == "__main__":
    pf.toJSONFilter(do_filter)
