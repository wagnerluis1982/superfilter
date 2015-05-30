superfilter.py
==============

Vários funcionalidades para ser usado no pandoc na geração de LaTeX.

Modo de usar
------------

Para usar o `superfilter.py`, basta utilizar o parâmetro `--filter` no pandoc
escolhendo o caminho do script

    $ pandoc --filter ./superfilter.py paper.mkd -o paper.pdf

Segue nas próximas seções o que o filtro pode fazer.

Imagens
-------

Parâmetros para auxiliar na inclusão de imagens no texto.

### Imagens com a largura fixa

Para obter a largura fixa, escreve `|` (pipe) após o caminho da imagem e informa
a largura. Assim, a declaração abaixo define que a imagem terá a largura de
50mm. Qualquer outra unidade de medida compatível com o LaTeX é possível.

```markdown
![Image caption](img/to_path.png | width=50mm)
```

O código acima é convertido para o seguinte código LaTeX:

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=50mm]{img/to_path.png}
  \caption{Image caption}
\end{figure}
```

### Imagens com a largura dinâmica

Semelhante à largura fixa, mas não é informado a unidade de medida. A declaração
abaixo define que a imagem terá a largura de 60% do espaço de texto atual.
Utiliza a fração da `\linewidth`, de forma que funciona em textos de uma ou duas
colunas.

```markdown
![Image caption](img/to_path.png | width=.6)
```

O código acima converte-se no seguinte LaTeX:

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=.6\linewidth]{img/to_path.png}
  \caption{Image caption}
\end{figure}
```

Referência cruzada
------------------

No LaTeX podemos fazer referências a praticamente qualquer elemento do texto,
seja o número da seção, número da imagem, número da tabela ou o número da
página. Fazemos isso usando âncoras, que definem uma marca no texto que então
podem ser referenciadas em outro lugar por links de referência.

### Âncoras

Para definir uma âncora, basta escrever a declaração abaixo em quase qualquer
parte do texto.

```markdown
<anchor:#sec:intro>
```

Esse código se tornará em LaTeX o seguinte:

```latex
\label{sec:intro}
```

Para definir uma âncora em uma imagem, é preciso escrever a declaração dentro do
caption, conforme exemplo abaixo.

```markdown
![Image caption
<anchor:#interesting>](img/to_path.png)
```

No caso de tabelas, é semelhante:

```markdown
Name    Phone
------  ---------
John    7632-3241
Wagner  1234-6789

Table: Phone list
<anchor:#phonelist>
```

### Links de referência

No LaTeX existem dois tipos de links de referência: um para os números das
seções, figuras e tabelas, e outro para referenciar a página em que a âncora
está definida.

Uma referência pode ser feita escrevendo o seguinte em quase qualquer parte.

```markdown
<ref:#sec:intro>
```

Quando o filtro for aplicado vira em LaTeX:

```latex
\ref{sec:intro}
```

Para referenciar a página, usamos a seguinte declaração.

```markdown
<pageref:#sec:intro>
```

Esse código se converte em LaTeX para:

```latex
\pageref{sec:intro}
```

Math
----

Melhorias ao definir equações matemáticas.

### Math com âncoras

No pandoc, podemos definir uma equação em seu próprio parágrafo, porém essa
equação não é numerada e nem é possível lhe definir uma âncora. Infelizmente não
é possível utilizar a declaração `<anchor:#sec:intro>` dentro de uma equação
porque será interpretado como matemática. Assim precisamos definir a seguinte
notação especial.

```markdown
$$ t(n) = {n(n-1)\over{2}} #eq:graphs $$
```

Com o código acima, será gerado o seguinte LaTeX. O ambiente `equation`
garantirá que a equação será numerada e o `\label` que podemos referenciar esse
número em outro lugar.

```latex
\begin{equation}\label{eq:graphs}
    t(n) = {n(n-1)\over{2}}
\end{equation}
```

Citações
--------

Melhorias para auxiliar nas citações. Essas melhorias são direcionadas ao uso do
pandoc com o parâmetro `--natbib` ou `--biblatex`, ou seja, não será usado o
recurso de citação interno do pandoc.

### Citações especiais

Alguns pacotes de citações do LaTeX permitem citar, por exemplo, somente o autor
ou somente o ano. Esse é o caso do pacote `biblatex` ou do `abntex2cite`.
Geralmente esses comandos de citação especiais possuem nomes sugestíveis tais
como `\citeauthor` ou `\citeyear`.

Levando isso em conta, com esse filtro, podemos utilizar as citações normais do
pandoc, como `[@Wei91]`, mas também podemos adicionar um parâmetro
indicando o nome desses comandos especiais, como `[@Wei91#author]`. O
exemplo a seguir ilustra melhor o uso.

```markdown
Conforme [@Wei91#author], no ano de [@Wei91#year], a computação ubíqua seria o
futuro do mundo.
```

O texto acima se converte para o seguinte LaTeX:

```latex
Conforme \citeauthor{Wei91}, no ano de \citeyear{Wei91}, a computação ubíqua
seria o futuro do mundo.
```

Beamer
------

Melhorias para o *beamer*, o pacote LaTeX usado para criar apresentações.

### Colunas no beamer

Como o pandoc não disponibiliza nenhuma forma para definir colunas em um slide,
então eu peguei emprestado a sintaxe do
[wiki2beamer](http://wiki2beamer.sourceforge.net/) e permiti a definição abaixo.

```markdown
<[columns]

[[[ 0.4 ]]]

Content of the first column using 40% of width

[[[ 0.6 ]]]

Content of the second column using 60% of width

[columns]>
```

Esse código é auto-explicativo e gerará o seguinte código LaTeX:

```latex
\begin{columns}

\column{0.4\textwidth}

Content of the first column using 40\% of width

\column{0.6\textwidth}

Content of the second column using 60\% of width

\end{columns}
```
