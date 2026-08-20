# Palavras Cruzadas

> A versão mais recente do Python que você deve usar neste curso é o Python 3.12.

Implemente uma IA capaz de gerar palavras cruzadas.

```text
$ python generate.py data/structure1.txt data/words1.txt output.png
██████████████
███████M████R█
█INTELLIGENCE█
█N█████N████S█
█F██LOGIC███O█
█E█████M████L█
█R███SEARCH█V█
███████X████E█
██████████████
```

![Palavras Cruzadas](https://cs50.harvard.edu/ai/projects/3/crossword/images/crossword.png)

## Contexto

Como podemos gerar um jogo de palavras cruzadas? Dada a estrutura de um jogo — isto é, quais células da grade devem ser preenchidas com letras — e uma lista de palavras disponíveis, o problema consiste em escolher quais palavras devem ocupar cada sequência vertical ou horizontal de células. Podemos modelar esse tipo de problema como um problema de satisfação de restrições.

Cada sequência de células corresponde a uma variável. Para cada uma delas, precisamos decidir seu valor, ou seja, qual palavra do domínio de palavras possíveis preencherá aquela sequência. Considere a seguinte estrutura de palavras cruzadas:

![Estrutura de Palavras Cruzadas](https://cs50.harvard.edu/ai/projects/3/crossword/images/structure.png)

Nessa estrutura, existem quatro variáveis, correspondentes às quatro palavras que precisam ser inseridas no jogo. Cada uma está indicada por um número na imagem acima. Toda variável é definida por quatro valores:

- a linha em que começa, representada pelo valor `i`;
- a coluna em que começa, representada pelo valor `j`;
- a direção da palavra, que pode ser `down` ou `across`;
- o comprimento da palavra.

A variável 1, por exemplo, seria representada pela linha `1`, considerando a contagem iniciada em `0` a partir do topo, pela coluna `1`, também considerando a contagem iniciada em `0` a partir da esquerda, pela direção `across` e pelo comprimento `4`.

Como ocorre em muitos problemas de satisfação de restrições, essas variáveis possuem restrições unárias e binárias. A restrição unária de uma variável é determinada por seu comprimento. Para a variável 1, por exemplo, o valor `BYTE` satisfaria a restrição unária, enquanto `BIT` não satisfaria, pois possui a quantidade errada de letras. Portanto, qualquer valor que não satisfaça as restrições unárias de uma variável pode ser removido imediatamente de seu domínio.

As restrições binárias de uma variável são determinadas por suas interseções com as variáveis vizinhas. A variável 1 possui uma única vizinha: a variável 2. A variável 2 possui duas vizinhas: as variáveis 1 e 3. Para cada par de variáveis vizinhas, existe uma interseção, isto é, uma única célula compartilhada por ambas. Podemos representar essa interseção pelo índice do caractere da palavra de cada variável que deve ser igual.

Por exemplo, a interseção entre as variáveis 1 e 2 pode ser representada pelo par `(1, 0)`. Isso significa que o caractere de índice `1` do valor da variável 1 deve ser igual ao caractere de índice `0` do valor da variável 2, novamente considerando índices iniciados em `0`. A interseção entre as variáveis 2 e 3 seria representada pelo par `(3, 1)`: o caractere de índice `3` do valor da variável 2 deve ser igual ao caractere de índice `1` do valor da variável 3.

Neste problema, será acrescentada ainda a restrição de que todas as palavras devem ser diferentes: uma mesma palavra não poderá ser repetida várias vezes no jogo.

O desafio, portanto, é escrever um programa que encontre uma atribuição satisfatória: uma palavra diferente, retirada de uma lista de vocabulário fornecida, para cada variável, de modo que todas as restrições unárias e binárias sejam atendidas.

## Primeiros Passos

- Baixe o código.

## Entendendo o Projeto

Há dois arquivos Python neste projeto: `crossword.py` e `generate.py`. O primeiro já foi totalmente implementado. O segundo possui algumas funções que deverão ser implementadas por você.

Primeiro, examine `crossword.py`. Esse arquivo define duas classes:

- `Variable`, que representa uma variável do jogo de palavras cruzadas;
- `Crossword`, que representa o próprio jogo.

Para criar uma `Variable`, é necessário informar quatro valores: sua linha `i`, sua coluna `j`, sua direção, que pode ser a constante `Variable.ACROSS` ou `Variable.DOWN`, e seu comprimento.

A classe `Crossword` requer dois valores para criar um novo jogo de palavras cruzadas:

- `structure_file`, que define a estrutura do jogo. O caractere `_` representa uma célula em branco, na qual deverá ser inserida uma letra. Qualquer outro caractere representa uma célula que não será preenchida;
- `words_file`, que define a lista de palavras do vocabulário, com uma palavra em cada linha.

O diretório `data` do projeto contém três exemplos de cada um desses tipos de arquivo. Você também pode criar seus próprios arquivos.

Para qualquer objeto `crossword` da classe `Crossword`, os seguintes valores são armazenados:

- `crossword.height`: número inteiro que representa a altura do jogo de palavras cruzadas;
- `crossword.width`: número inteiro que representa a largura do jogo;
- `crossword.structure`: lista bidimensional que representa a estrutura do jogo. Para qualquer linha válida `i` e coluna válida `j`, `crossword.structure[i][j]` será `True` se a célula estiver em branco e precisar receber um caractere, e será `False` se nenhum caractere precisar ser inserido nela;
- `crossword.words`: conjunto de todas as palavras disponíveis para a construção do jogo;
- `crossword.variables`: conjunto de todas as variáveis do jogo, cada uma representada por um objeto `Variable`;
- `crossword.overlaps`: dicionário que associa um par de variáveis à interseção entre elas. Para duas variáveis distintas `v1` e `v2`, `crossword.overlaps[v1, v2]` será `None` se elas não possuírem uma interseção. Caso possuam, o valor será um par de inteiros `(i, j)`, indicando que o caractere de índice `i` do valor de `v1` deve ser igual ao caractere de índice `j` do valor de `v2`.

Objetos `Crossword` também possuem o método `neighbors`, que retorna todas as variáveis que se sobrepõem a determinada variável. Assim, `crossword.neighbors(v1)` retorna um conjunto contendo todas as variáveis vizinhas de `v1`.

Em seguida, examine `generate.py`. Nesse arquivo, está definida a classe `CrosswordCreator`, que será usada para resolver o jogo. Quando um objeto `CrosswordCreator` é criado, ele recebe a propriedade `crossword`, cujo valor deve ser um objeto `Crossword` e que, portanto, possui todas as propriedades descritas anteriormente.

Cada objeto `CrosswordCreator` também recebe a propriedade `domains`: um dicionário que associa cada variável a um conjunto de possíveis palavras que ela pode assumir como valor. Inicialmente, esse conjunto contém todas as palavras do vocabulário, mas você implementará funções para restringir esses domínios.

Algumas funções auxiliares já foram definidas para ajudar nos testes:

- `print` exibe no terminal uma representação do jogo correspondente a determinada atribuição. Nessa função e nas demais, uma atribuição é um dicionário que associa variáveis às palavras correspondentes;
- `save` gera um arquivo de imagem correspondente a determinada atribuição. Para usar essa função, é necessário instalar `Pillow` executando `pip install Pillow`;
- `letter_grid` é uma função auxiliar usada por `print` e `save`. Ela gera uma lista bidimensional com todos os caracteres em suas posições apropriadas para determinada atribuição. Provavelmente não será necessário chamá-la diretamente, mas você poderá fazê-lo se desejar.

Por fim, observe a função `solve`. Ela executa três etapas:

1. chama `enforce_node_consistency` para impor a consistência de nó ao jogo, garantindo que todos os valores do domínio de uma variável satisfaçam suas restrições unárias;
2. chama `ac3` para impor a consistência de arco, garantindo que as restrições binárias sejam satisfeitas;
3. chama `backtrack` com uma atribuição inicialmente vazia, representada pelo dicionário `dict()`, para tentar encontrar uma solução para o problema.

As funções `enforce_node_consistency`, `ac3` e `backtrack`, entre outras, ainda não foram implementadas. Essa será a sua tarefa.

## Especificação

Conclua a implementação das funções `enforce_node_consistency`, `revise`, `ac3`, `assignment_complete`, `consistent`, `order_domain_values`, `select_unassigned_variable` e `backtrack` em `generate.py`, para que sua IA gere jogos completos de palavras cruzadas sempre que houver uma solução possível.

### `enforce_node_consistency`

A função `enforce_node_consistency` deve atualizar `self.domains` para que todas as variáveis sejam consistentes em seus nós.

- A consistência de nó é alcançada quando, para cada variável, todos os valores de seu domínio são compatíveis com as restrições unárias da variável. No caso das palavras cruzadas, isso significa garantir que cada valor do domínio possua a mesma quantidade de letras que o comprimento da variável.
- Para remover um valor `x` do domínio de uma variável `v`, como `self.domains` é um dicionário que associa variáveis a conjuntos de valores, você pode chamar `self.domains[v].remove(x)`.
- Essa função não precisa retornar nenhum valor.

### `revise`

A função `revise` deve tornar a variável `x` consistente em arco com a variável `y`.

- `x` e `y` serão objetos `Variable` que representam variáveis do jogo.
- `x` é consistente em arco com `y` quando todo valor do domínio de `x` possui algum valor possível no domínio de `y` que não provoca conflito. No contexto das palavras cruzadas, ocorre um conflito quando duas variáveis discordam sobre o caractere que deve ocupar uma célula compartilhada.
- Para tornar `x` consistente em arco com `y`, remova do domínio de `x` qualquer valor para o qual não exista um valor possível correspondente no domínio de `y`.
- Você pode acessar `self.crossword.overlaps` para obter a interseção, caso exista, entre duas variáveis.
- O domínio de `y` deve permanecer inalterado.
- A função deve retornar `True` se o domínio de `x` tiver sido revisado e `False` caso nenhuma revisão tenha sido realizada.

### `ac3`

A função `ac3` deve usar o algoritmo AC-3 para impor a consistência de arco ao problema. A consistência de arco é alcançada quando todos os valores do domínio de cada variável satisfazem as restrições binárias dessa variável.

- O algoritmo AC-3 mantém uma fila de arcos a serem processados. A função recebe um argumento opcional chamado `arcs`, que representa uma lista inicial de arcos.
- Se `arcs` for `None`, a função deverá começar com uma fila que contenha todos os arcos do problema.
- Caso contrário, o algoritmo deverá começar apenas com os arcos presentes na lista `arcs`. Cada arco é uma tupla `(x, y)`, formada por uma variável `x` e uma variável diferente `y`.
- Para implementar o AC-3, revise cada arco da fila, um de cada vez. Sempre que um domínio for alterado, poderá ser necessário adicionar outros arcos à fila para garantir que eles continuem consistentes.
- Pode ser útil chamar a função `revise` durante a implementação de `ac3`.
- Se, durante a imposição da consistência de arco, todos os valores restantes de um domínio forem removidos, retorne `False`. Isso significa que o problema não pode ser resolvido, pois não há mais valores possíveis para aquela variável. Caso contrário, retorne `True`.
- Não é necessário impor a unicidade das palavras nessa função. Essa verificação será implementada na função `consistent`.

### `assignment_complete`

A função `assignment_complete` deve verificar se determinada `assignment` está completa.

- Uma `assignment` é um dicionário cujas chaves são objetos `Variable` e cujos valores são strings que representam as palavras atribuídas a essas variáveis.
- Uma atribuição está completa quando todas as variáveis do jogo receberam um valor, independentemente de qual seja esse valor.
- A função deve retornar `True` se a atribuição estiver completa e `False` caso contrário.

### `consistent`

A função `consistent` deve verificar se determinada `assignment` é consistente.

- Uma `assignment` é um dicionário cujas chaves são objetos `Variable` e cujos valores são strings que representam as palavras atribuídas a essas variáveis.
- A atribuição pode estar incompleta, isto é, nem todas as variáveis precisam estar presentes nela.
- Uma atribuição é consistente quando satisfaz todas as restrições do problema: todos os valores são distintos, cada valor possui o comprimento correto e não existem conflitos entre variáveis vizinhas.
- A função deve retornar `True` se a atribuição for consistente e `False` caso contrário.

### `order_domain_values`

A função `order_domain_values` deve retornar uma lista com todos os valores do domínio de `var`, ordenados de acordo com a heurística do valor menos restritivo.

- `var` será um objeto `Variable` que representa uma variável do jogo.
- A heurística do valor menos restritivo é calculada pela quantidade de valores eliminados dos domínios das variáveis vizinhas ainda não atribuídas. Em outras palavras, se atribuir determinado valor a `var` eliminar `n` escolhas possíveis das variáveis vizinhas, os resultados devem ser ordenados em ordem crescente de `n`.
- Uma variável presente em `assignment` já possui um valor e, portanto, não deve ser considerada no cálculo da quantidade de valores eliminados das variáveis vizinhas ainda não atribuídas.
- Se dois valores do domínio eliminarem a mesma quantidade de escolhas possíveis das variáveis vizinhas, qualquer ordem entre eles será aceita.
- Você pode acessar `self.crossword.overlaps` para obter a interseção, caso exista, entre duas variáveis.
- Pode ser útil implementar primeiro essa função retornando uma lista de valores em qualquer ordem. Isso ainda permitirá gerar palavras cruzadas corretas. Depois que o algoritmo estiver funcionando, retorne à função e garanta que os valores sejam devolvidos na ordem correta.
- Pode ser útil [ordenar](https://docs.python.org/3/howto/sorting.html) uma lista de acordo com uma `key`. O Python possui funções que facilitam essa tarefa.

### `select_unassigned_variable`

A função `select_unassigned_variable` deve retornar uma única variável do jogo que ainda não esteja atribuída em `assignment`, usando primeiro a heurística do menor valor restante e, em seguida, a heurística de grau.

- Uma `assignment` é um dicionário cujas chaves são objetos `Variable` e cujos valores são strings que representam as palavras atribuídas às variáveis.
- Você pode assumir que a atribuição não estará completa, isto é, que nem todas as variáveis estarão presentes nela.
- A função deve retornar um objeto `Variable`.
- Retorne a variável que possui a menor quantidade de valores restantes em seu domínio.
- Em caso de empate, escolha, entre as variáveis empatadas, aquela de maior grau, isto é, a que possui mais vizinhas.
- Se também houver empate no grau, qualquer uma das variáveis empatadas poderá ser escolhida.
- Pode ser útil implementar primeiro essa função retornando qualquer variável ainda não atribuída. Isso ainda permitirá gerar palavras cruzadas corretas. Depois que o algoritmo estiver funcionando, retorne à função e garanta que a variável seja escolhida de acordo com as heurísticas.
- Pode ser útil [ordenar](https://docs.python.org/3/howto/sorting.html) uma lista de acordo com uma `key`. O Python possui funções que facilitam essa tarefa.

### `backtrack`

A função `backtrack` deve receber como entrada uma atribuição parcial `assignment` e, usando busca por retrocesso, retornar uma atribuição completa e satisfatória de variáveis para valores, caso seja possível encontrá-la.

- Uma `assignment` é um dicionário cujas chaves são objetos `Variable` e cujos valores são strings que representam as palavras atribuídas às variáveis.
- A atribuição de entrada pode estar incompleta, isto é, nem todas as variáveis precisam possuir valores.
- Se for possível gerar um jogo satisfatório, a função deve retornar a atribuição completa: um dicionário em que cada variável é uma chave e o valor associado é a palavra que ela deve assumir.
- Se não houver uma atribuição satisfatória possível, a função deve retornar `None`.
- Se desejar, você poderá tornar o algoritmo mais eficiente intercalando a busca com inferências, por exemplo, mantendo a consistência de arco sempre que uma nova atribuição for realizada. Isso não é obrigatório, mas é permitido, desde que a função continue produzindo resultados corretos. É por esse motivo que `ac3` aceita o argumento `arcs`, caso seja necessário iniciar o algoritmo com uma fila de arcos diferente.

Não modifique nenhuma outra parte de `generate.py` além das funções indicadas na especificação. Você pode criar funções auxiliares e importar outros módulos da biblioteca padrão do Python. Também pode importar `numpy` ou `pandas`, caso esteja familiarizado com essas bibliotecas, mas não deve utilizar nenhum outro módulo de terceiros.

Não modifique nenhuma parte de `crossword.py`.

## Dicas

- Para `order_domain_values` e `select_unassigned_variable`, pode ser útil implementar primeiro as funções sem se preocupar com as heurísticas e acrescentá-las depois. O algoritmo continuará funcionando, mas poderá explorar mais atribuições do que o necessário antes de encontrar uma solução.
- Para executar o programa, use um comando como:

```bash
python generate.py data/structure1.txt data/words1.txt
```

Informe um arquivo de estrutura e um arquivo de palavras. Se houver uma atribuição possível, ela será exibida no terminal.

Você também pode fornecer um argumento adicional contendo o nome de um arquivo de imagem:

```bash
python generate.py data/structure1.txt data/words1.txt output.png
```

Esse comando gera uma representação em imagem do jogo de palavras cruzadas resolvido.

- A classe `Crossword` possui a função `neighbors`, que permite acessar todas as variáveis vizinhas, isto é, todas as variáveis que se sobrepõem a determinada variável. Use-a sempre que precisar determinar as vizinhas de uma variável.

## Testes

Para acompanhar o progresso da sua implementação, execute:

```bash
python test_crossword.py
```

O script apresenta os testes agrupados por função, mostra os valores esperados e obtidos e fornece dicas quando encontra uma falha. Esses testes são auxiliares e não garantem que todos os casos possíveis estejam corretos.

Execute o programa com as diferentes estruturas e listas de palavras disponíveis no diretório `data`. Por exemplo:

```bash
python generate.py data/structure0.txt data/words0.txt
python generate.py data/structure1.txt data/words1.txt
python generate.py data/structure2.txt data/words2.txt
```

Verifique se todas as palavras exibidas possuem o comprimento correto, são distintas e concordam nas células de interseção.

Para testar também a geração de imagens, instale `Pillow`, caso ainda não esteja instalado, e execute:

```bash
pip install Pillow
python generate.py data/structure1.txt data/words1.txt output.png
```

Você não deve importar módulos que não façam parte da biblioteca padrão do Python, com exceção de `numpy` e `pandas`, expressamente autorizados pela especificação da atividade.

Existem ferramentas capazes de simplificar alguns destes projetos, mas esse não é o objetivo da atividade. O propósito é compreender e implementar os conceitos em um nível mais fundamental. Se o uso de uma ferramenta não foi autorizado, ela não deve ser utilizada.

---

## Atribuição e Licença

Material original: **CS50’s Introduction to Artificial Intelligence with Python — Crossword**, de CS50/Harvard University.

Este documento é uma tradução e adaptação do [material original](https://cs50.harvard.edu/ai/projects/3/crossword/). As imagens permanecem hospedadas no site do CS50.

O material original e esta adaptação estão licenciados sob a [Licença Internacional Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
