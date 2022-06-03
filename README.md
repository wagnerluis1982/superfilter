superfilter.py
==============

Several functionalities to be used on [pandoc](https://pandoc.org/) in the LaTeX generation.

DISCLAIMER: this filter was originally created for pandoc v1.13.x. There is no guarantee it will work for latest versions.

Usage
-----

To use `superfilter.py`, it is only a matter of use the parameter `--filter` in the pandoc command line:

    $ pandoc --filter /path/to/superfilter.py paper.mkd -o paper.pdf

Functionalities
---------------

### Pictures

Parameters to help the inclusion of images in the text.

#### Fixed-width images

To get a fixed-width image, type `|` after the image path and provide the width. Thus, the declaration below defines that the image will have the width of 50mm. Any other LaTeX compatible unit of measure is possible.

```markdown
![Image caption](img/to_path.png | width=50mm)
```

The code above is converted to the following LaTeX code:

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=50mm]{img/to_path.png}
  \caption{Image caption}
\end{figure}
```

#### Dynamic width images

It is similar to the fixed-width, but the unit is not provided. The code below defines a image which will be 60% of the current text space. Makes use of fractions of `\linewidth`, so it works in one or two columns text.

```markdown
![Image caption](img/to_path.png | width=.6)
```

The code above converts to the following LaTeX:

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=.6\linewidth]{img/to_path.png}
  \caption{Image caption}
\end{figure}
```

### Cross References

LaTeX can make references to practically any element of the text, such as section number, image number, table number or the page itself. This is accomplished by using anchors, which define a tag in the text that can be referenced elsewhere by referral links.

#### Anchors

To define an anchor, just write the statement below in almost any part of the text.

```markdown
<anchor:#sec:intro>
```

This code will become the following LaTeX:

```latex
\label{sec:intro}
```

To define an anchor on an image, you need to write the declaration inside the caption, as shown below.

```markdown
![Image caption
<anchor:#interesting>](img/to_path.png)
```

Similarly, you can add anchor to tables with the following:

```markdown
Name    Phone
------  ---------
John    7632-3241
Wagner  1234-6789

Table: Phone list
<anchor:#phonelist>
```

#### Referral links

There are two types of reference links in LaTeX: one for the numbers of sections, figures and tables, and another to reference the page where the anchor is defined.

A reference can be made by writing the following almost anywhere in the text.

```markdown
<ref:#sec:intro>
```

When the filter is applied it turns into LaTeX:

```latex
\ref{sec:intro}
```

To reference the page, we use the following declaration.

```markdown
<pageref:#sec:intro>
```

This code converts in LaTeX to:

```latex
\pageref{sec:intro}
```

### Math

Improvements to write math equations.

#### Math with anchors

In pandoc, we can write equations in separate paragraphs, but these equations are not numbered and it is not even possible to set an anchor for it. Unfortunately it is not possible to use the `<anchor:#sec:intro>` declaration inside an equation because it will be interpreted as math. So we need to use the following special notation.

```markdown
$$ t(n) = {n(n-1)\over{2}} #eq:graphs $$
```

With the code above, the following LaTeX will be generated. Notice the `equation` environment, this will ensure the equation to be numbered and with the `\label` we can reference that number elsewhere.

```latex
\begin{equation}\label{eq:graphs}
    t(n) = {n(n-1)\over{2}}
\end{equation}
```

### Citations

Improvements to work with citations. These improvements are aimed at using the pandoc with the `--natbib` or `--biblatex` parameter, so it will not be used the pandoc built-in citation engine.

#### Special citations

Some LaTeX citation packages allow to cite only the author or the year. That is the case with the `biblatex` or `abntex2cite` package. Usually these special citation commands have suggestible names such as like `\citeauthor` or `\citeyear`.

Taking this into account, this filter allow to use the normal citations of the pandoc, like `[@Wei91]`, but we can also add an indication for the citation command, such as `[@Wei91#author]`. The following example illustrates the usage.

```markdown
According to [@Wei91#author], in the year of [@Wei91#year], ubiquitous computing
will be the future of the world.
```

The above text converts to the following LaTeX:

```latex
According to \citeauthor{Wei91}, in the year of \citeyear{Wei91}, ubiquitous computing
will be the future of the world.
```

### Beamer

Improvements to *beamer*, the LaTeX package used to create presentations.

#### Columns in beamer

As pandoc doesn't provide any way to define columns in a slide, I borrowed the syntax from [wiki2beamer](http://wiki2beamer.sourceforge.net/) and added a way to write columns in the slides.

```markdown
<[columns]

[[[ 0.4 ]]]

Content of the first column using 40% of width

[[[ 0.6 ]]]

Content of the second column using 60% of width

[columns]>
```

This code is self-explanatory and will generate the following LaTeX code:

```latex
\begin{columns}

\column{0.4\textwidth}

Content of the first column using 40\% of width

\column{0.6\textwidth}

Content of the second column using 60\% of width

\end{columns}
```
