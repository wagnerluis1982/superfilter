superfilter.py
==============

Vários funcionalidades para ser usado no pandoc na geração de LaTeX. Segue
abaixo o que o filtro faz.

Imagens com a largura informada
-------------------------------

Parâmetro para informar a largura da imagem. Pode ser largura fixa ou
proporcional à largura do texto, seja em uma coluna ou duas.

### Largura fixa

Para obter a largura fixa, escreve `|` (pipe) após o caminho da imagem e informa
a largura. Assim, a declaração abaixo

```markdown
![Image caption](img/to_path.png | width=50mm)
```

é convertido para o seguinte código LaTeX

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=50mm]{img/to_path.png}
  \caption{Image caption}
\end{figure}
```

### Largura dinâmica

Semelhante à largura fixa, mas não é informado a unidade de medida. A declaração

```markdown
![Image caption](img/to_path.png | width=.6)
```

converte-se no seguinte LaTeX

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=.6\linewidth]{img/to_path.png}
  \caption{Image caption}
\end{figure}
```

Âncoras
-------

Define uma âncora no texto que pode ser referenciada mais tarde. Para definir
uma âncora, escreva

```markdown
^[#sec:intro]
```

que se tornará em LaTeX

```latex
\label{sec:intro}
```

Links de referência
-------------------

Faz referência à uma âncora definida previsamente. Uma referência é feita
escrevendo

```markdown
[](#sec:intro)
```

e quando o filtro for aplicado vira o LaTeX

```latex
\ref{sec:intro}
```

### Referência de página

Podemos referenciar a página, usando

```markdown
[](#sec:intro "page")
```

que se converte em LaTeX para

```latex
\pageref{sec:intro}
```

Math com âncoras
----------------

Não há como referenciar uma equação usando pandoc. Usando o seguinte código,
pode-se definir um `\label` à equação para referenciar em outra parte.

```markdown
$$ t(n) = {n(n-1)\over{2}} #eq:graphs $$
```

Com o código acima, será gerado o seguinte LaTeX:

```latex
\begin{equation}\label{eq:graphs}
    t(n) = {n(n-1)\over{2}}
\end{equation}
```

Colunas na saída beamer
-----------------------

Como o pandoc não disponibiliza nenhuma forma para definir colunas no beamer,
então eu peguei emprestado a sintaxe do
[wiki2beamer](http://wiki2beamer.sourceforge.net/).

Assim, o código Markdown abaixo

```markdown
<[columns]

[[[ 0.4 ]]]

Content of the first column using 40% of width

[[[ 0.6 ]]]

Content of the second column using 60% of width

[columns]>
```

gerará o seguinte código LaTeX

```latex
\begin{columns}

\column{0.4\textwidth}

Content of the first column using 40\% of width

\column{0.6\textwidth}

Content of the second column using 60\% of width

\end{columns}
```
