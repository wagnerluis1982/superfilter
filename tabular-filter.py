# tabular-filter.py is a pandoc filter to use tabular instead of longtable in LaTeX generation.
# Copyright (C) 2014 Wagner Macedo
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pandocfilters as pf

def latex(s):
    return pf.RawBlock('latex', s)

def inlatex(s):
    return pf.RawInline('latex', s)

def tbl_caption(s):
    return pf.Para([inlatex(r'\caption{')] + s + [inlatex('}')])

def tbl_alignment(s):
    aligns = {
        "AlignDefault": 'l',
        "AlignLeft": 'l',
        "AlignCenter": 'c',
        "AlignRight": 'r',
    }
    return ''.join([aligns[e['t']] for e in s])

def tbl_headers(s):
    result = s[0][0]['c'][:]
    for i in range(1, len(s)):
        result.append(inlatex(' & '))
        result.extend(s[i][0]['c'])
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

def do_filter(k, v, f, m):
    if k == "Table":
        return [latex(r'\begin{table}[ht]' '\n' r'\centering' '\n'),
                tbl_caption(v[0]),
                latex(r'\begin{tabular}{@{}%s@{}}' % tbl_alignment(v[1]) +
                      ('\n' r'\toprule')),
                tbl_headers(v[3]),
                tbl_contents(v[4]),
                latex(r'\bottomrule' '\n' r'\end{tabular}'),
                latex(r'\end{table}')]


if __name__ == "__main__":
    pf.toJSONFilter(do_filter)
