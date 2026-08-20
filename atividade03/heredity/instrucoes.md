# Hereditariedade

> A versão mais recente do Python que você deve usar neste curso é o Python 3.12.

Implemente uma IA capaz de avaliar a probabilidade de uma pessoa possuir uma determinada característica genética.

```text
$ python heredity.py data/family0.csv
Harry:
  Gene:
    2: 0.0092
    1: 0.4557
    0: 0.5351
  Trait:
    True: 0.2665
    False: 0.7335
James:
  Gene:
    2: 0.1976
    1: 0.5106
    0: 0.2918
  Trait:
    True: 1.0000
    False: 0.0000
Lily:
  Gene:
    2: 0.0036
    1: 0.0136
    0: 0.9827
  Trait:
    True: 0.0000
    False: 1.0000
```

## Contexto

Versões mutadas do [gene GJB2](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1285178/) estão entre as principais causas de deficiência auditiva em recém-nascidos. Cada pessoa carrega duas versões desse gene e, portanto, pode possuir `0`, `1` ou `2` cópias da versão do GJB2 associada à deficiência auditiva.

Sem um teste genético, porém, não é fácil saber quantas cópias do GJB2 mutado uma pessoa possui. Trata-se de um **estado oculto**: uma informação que produz um efeito observável, como a deficiência auditiva, mas que não conhecemos diretamente. Algumas pessoas podem possuir uma ou duas cópias do GJB2 mutado sem apresentar deficiência auditiva, enquanto outras podem não possuir nenhuma cópia e ainda assim apresentar essa característica.

Cada criança herda uma cópia do gene GJB2 de cada um de seus pais. Se um dos pais possui duas cópias do gene mutado, transmitirá o gene mutado à criança. Se não possui nenhuma cópia, não transmitirá o gene mutado. Se possui uma cópia, o gene é transmitido à criança com probabilidade de `0.5`.

Depois de ser transmitido, entretanto, o gene possui certa probabilidade de sofrer uma nova mutação: uma versão que causa deficiência auditiva pode se transformar em uma versão que não a causa, ou vice-versa.

Podemos modelar essas relações por meio de uma Rede Bayesiana com todas as variáveis relevantes. A rede abaixo representa uma família formada por dois pais e uma criança.

![Rede Bayesiana para características genéticas](https://cs50.harvard.edu/ai/projects/2/heredity/images/gene_network.png)

Cada pessoa da família possui uma variável aleatória `Gene`, que representa quantas cópias de determinado gene ela possui — por exemplo, a versão do GJB2 associada à deficiência auditiva. Essa variável pode assumir os valores `0`, `1` ou `2`.

Cada pessoa também possui uma variável aleatória `Trait`, cujo valor é `yes` ou `no`, de acordo com a manifestação ou não de uma característica associada ao gene, como a deficiência auditiva.

Há uma seta da variável `Gene` de cada pessoa para sua variável `Trait`, representando que os genes de uma pessoa afetam a probabilidade de ela manifestar determinada característica. Há também uma seta da variável `Gene` da mãe e outra da variável `Gene` do pai para a variável `Gene` da criança, pois os genes da criança dependem dos genes de seus pais.

Neste projeto, você utilizará esse modelo para realizar inferências sobre uma população. A partir de informações sobre as pessoas, seus pais e a presença ou ausência de uma característica observável causada por determinado gene, sua IA deverá inferir, para cada pessoa:

- a distribuição de probabilidade da quantidade de cópias do gene;
- a distribuição de probabilidade da manifestação da característica.

## Primeiros Passos

- Baixe o código.

## Entendendo o Projeto

Abra um dos conjuntos de dados de exemplo do diretório `data`, como `data/family0.csv`. Você pode usar um editor de texto ou um aplicativo de planilhas, como Google Sheets, Excel ou Apple Numbers.

A primeira linha define as colunas do arquivo CSV: `name`, `mother`, `father` e `trait`.

A linha seguinte informa que Harry tem Lily como mãe e James como pai. A célula vazia na coluna `trait` indica que não sabemos se Harry manifesta a característica. James não possui pais registrados no conjunto de dados, como mostram as células vazias em `mother` e `father`, e manifesta a característica, o que é representado por `1` em `trait`. Lily também não possui pais registrados, mas não manifesta a característica, o que é representado por `0`.

Abra o arquivo `heredity.py` e observe primeiro a definição de `PROBS`. `PROBS` é um dicionário que contém constantes correspondentes às probabilidades de diferentes eventos. Esses eventos se referem à quantidade de cópias de determinado gene — chamado daqui em diante apenas de **gene** — e à manifestação de determinada característica associada a ele — chamada apenas de **característica**.

Os dados são aproximadamente baseados nas probabilidades da versão do gene GJB2 associada à deficiência auditiva e da própria deficiência auditiva. Se esses valores forem alterados, a IA também poderá realizar inferências sobre outros genes e características.

Primeiro, `PROBS["gene"]` representa a distribuição de probabilidade incondicional do gene, isto é, a probabilidade usada quando nada se sabe sobre os pais da pessoa. De acordo com os dados fornecidos:

- a probabilidade de possuir `2` cópias do gene é de `1%`;
- a probabilidade de possuir `1` cópia do gene é de `3%`;
- a probabilidade de possuir `0` cópias do gene é de `96%`.

Em seguida, `PROBS["trait"]` representa a probabilidade condicional de uma pessoa manifestar a característica. Na verdade, há três distribuições de probabilidade distintas: uma para cada valor possível de `gene`.

Por exemplo, `PROBS["trait"][2]` é a distribuição de probabilidade da característica quando a pessoa possui duas cópias do gene. Nesse caso, a pessoa possui `65%` de probabilidade de manifestar a característica e `35%` de probabilidade de não manifestá-la. Se uma pessoa possui zero cópias do gene, há `1%` de probabilidade de manifestar a característica e `99%` de probabilidade de não manifestá-la.

Por fim, `PROBS["mutation"]` é a probabilidade de um gene sofrer mutação, passando de uma versão do gene em questão para outra versão, ou vice-versa.

Se uma mãe possui duas cópias do gene, por exemplo, ela necessariamente transmite uma cópia à criança, mas existe `1%` de probabilidade de essa cópia sofrer mutação e deixar de ser o gene considerado. Por outro lado, se a mãe não possui nenhuma cópia do gene, ela não o transmite, mas existe `1%` de probabilidade de o gene transmitido sofrer mutação e se transformar no gene considerado.

Portanto, mesmo que nenhum dos pais possua uma cópia do gene em questão, ainda é possível que a criança possua uma ou duas cópias. As probabilidades calculadas pelo programa serão baseadas nos valores definidos em `PROBS`.

Agora observe a função `main`. Primeiro, ela carrega os dados de um arquivo para o dicionário `people`. Esse dicionário associa o nome de cada pessoa a outro dicionário que contém:

- seu nome;
- sua mãe, se estiver registrada no conjunto de dados;
- seu pai, se estiver registrado no conjunto de dados;
- se a pessoa foi observada manifestando a característica: `True` se manifesta, `False` se não manifesta e `None` se não sabemos.

Em seguida, `main` define o dicionário `probabilities`, com todas as probabilidades inicialmente iguais a `0`. Esse dicionário representa o resultado que o projeto deverá calcular: para cada pessoa, a IA determinará a distribuição de probabilidade da quantidade de cópias do gene e a distribuição de probabilidade da manifestação da característica.

Por exemplo, `probabilities["Harry"]["gene"][1]` será a probabilidade de Harry possuir uma cópia do gene, enquanto `probabilities["Lily"]["trait"][False]` será a probabilidade de Lily não manifestar a característica.

O dicionário `probabilities` é criado usando uma [compreensão de dicionário](https://docs.python.org/3/tutorial/datastructures.html#dictionaries), que cria um par de chave e valor para cada `person` existente em `people`.

O objetivo é calcular essas probabilidades a partir das evidências disponíveis. Sabendo que determinadas pessoas manifestam ou não a característica, podemos calcular uma probabilidade condicional somando todas as probabilidades conjuntas compatíveis com as evidências e, depois, normalizando os valores para que cada distribuição some `1`.

Você deverá implementar três funções:

- `joint_probability`, que calcula uma probabilidade conjunta;
- `update`, que adiciona a probabilidade conjunta recém-calculada às distribuições existentes;
- `normalize`, que garante que todas as distribuições de probabilidade somem `1` ao final.

## Especificação

Conclua a implementação das funções `joint_probability`, `update` e `normalize`.

### `joint_probability`

A função `joint_probability` recebe um dicionário de pessoas, informações sobre quantas cópias do gene cada pessoa possui e informações sobre quem manifesta a característica. A função deve retornar a probabilidade conjunta de todos esses eventos ocorrerem.

A função recebe quatro argumentos: `people`, `one_gene`, `two_genes` e `have_trait`.

- `people` é um dicionário de pessoas, conforme descrito na seção **Entendendo o Projeto**. As chaves representam os nomes, e os valores são dicionários que contêm, entre outras informações, as chaves `mother` e `father`. Você pode assumir que `mother` e `father` estarão ambos vazios, quando não houver informação parental no conjunto de dados, ou ambos indicarão outras pessoas existentes no dicionário `people`.
- `one_gene` é o conjunto de todas as pessoas para as quais se deseja calcular a probabilidade de possuírem uma cópia do gene.
- `two_genes` é o conjunto de todas as pessoas para as quais se deseja calcular a probabilidade de possuírem duas cópias do gene.
- `have_trait` é o conjunto de todas as pessoas para as quais se deseja calcular a probabilidade de manifestarem a característica.
- Para qualquer pessoa que não pertença a `one_gene` nem a `two_genes`, deve-se calcular a probabilidade de ela possuir zero cópias do gene. Para qualquer pessoa que não pertença a `have_trait`, deve-se calcular a probabilidade de ela não manifestar a característica.

Por exemplo, se a família for formada por Harry, James e Lily, uma chamada em que `one_gene = {"Harry"}`, `two_genes = {"James"}` e `have_trait = {"Harry", "James"}` deverá calcular a probabilidade de todos os seguintes eventos ocorrerem simultaneamente:

- Lily possui zero cópias do gene;
- Harry possui uma cópia do gene;
- James possui duas cópias do gene;
- Harry manifesta a característica;
- James manifesta a característica;
- Lily não manifesta a característica.

Para realizar o cálculo:

- Quando uma pessoa não possuir pais registrados no conjunto de dados, use a distribuição `PROBS["gene"]` para determinar a probabilidade de ela possuir a quantidade correspondente de cópias do gene.
- Quando uma pessoa possuir pais registrados, considere que cada um deles transmite aleatoriamente um de seus dois genes à criança. Existe uma probabilidade `PROBS["mutation"]` de o gene transmitido sofrer mutação, passando de uma versão do gene para outra ou vice-versa.
- Use a distribuição `PROBS["trait"]` para calcular a probabilidade de uma pessoa manifestar ou não a característica.

### `update`

A função `update` adiciona uma nova probabilidade conjunta às distribuições já existentes em `probabilities`.

A função recebe cinco argumentos: `probabilities`, `one_gene`, `two_genes`, `have_trait` e `p`.

- `probabilities` é um dicionário de pessoas, conforme descrito na seção **Entendendo o Projeto**. Cada pessoa está associada a uma distribuição `"gene"` e a uma distribuição `"trait"`.
- `one_gene` é o conjunto de pessoas que possuem uma cópia do gene na distribuição conjunta atual.
- `two_genes` é o conjunto de pessoas que possuem duas cópias do gene na distribuição conjunta atual.
- `have_trait` é o conjunto de pessoas que manifestam a característica na distribuição conjunta atual.
- `p` é a probabilidade da distribuição conjunta.

Para cada `person` existente em `probabilities`, a função deve atualizar `probabilities[person]["gene"]` e `probabilities[person]["trait"]`, adicionando `p` ao valor apropriado de cada distribuição. Todos os demais valores devem permanecer inalterados.

Por exemplo, se `"Harry"` pertencer tanto a `two_genes` quanto a `have_trait`, o valor de `p` deverá ser adicionado a `probabilities["Harry"]["gene"][2]` e a `probabilities["Harry"]["trait"][True]`.

A função não deve retornar nenhum valor; ela deve apenas atualizar o dicionário `probabilities`.

### `normalize`

A função `normalize` atualiza um dicionário de probabilidades para que cada distribuição seja normalizada, isto é, para que seus valores somem `1` sem alterar suas proporções relativas.

A função recebe um único argumento: `probabilities`.

- `probabilities` é um dicionário de pessoas, conforme descrito na seção **Entendendo o Projeto**. Cada pessoa está associada a uma distribuição `"gene"` e a uma distribuição `"trait"`.
- Para cada pessoa, a função deve normalizar as duas distribuições de modo que os valores de cada uma somem `1`, mantendo as mesmas proporções relativas.

Por exemplo, se `probabilities["Harry"]["trait"][True]` for igual a `0.1` e `probabilities["Harry"]["trait"][False]` for igual a `0.3`, a função deverá atualizar o primeiro valor para `0.25` e o segundo para `0.75`. Agora os valores somam `1`, e o segundo continua sendo três vezes maior que o primeiro.

A função não deve retornar nenhum valor; ela deve apenas atualizar o dicionário `probabilities`.

Não modifique nenhuma parte de `heredity.py` além das três funções indicadas na especificação. Você pode criar funções auxiliares e importar outros módulos da biblioteca padrão do Python. Também pode importar `numpy` ou `pandas`, se estiver familiarizado com eles, mas não deve utilizar nenhum outro módulo de terceiros.

## Exemplo de Probabilidade Conjunta

Para ajudar a compreender o cálculo de probabilidades conjuntas, considere o seguinte valor de `people`:

```python
{
    "Harry": {"name": "Harry", "mother": "Lily", "father": "James", "trait": None},
    "James": {"name": "James", "mother": None, "father": None, "trait": True},
    "Lily": {"name": "Lily", "mother": None, "father": None, "trait": False}
}
```

Vamos calcular `joint_probability(people, {"Harry"}, {"James"}, {"James"})`. De acordo com os argumentos:

- `one_gene` é `{"Harry"}`;
- `two_genes` é `{"James"}`;
- `have_trait` é `{"James"}`.

Essa chamada representa a probabilidade conjunta de Lily possuir zero cópias do gene e não manifestar a característica, Harry possuir uma cópia do gene e não manifestar a característica e James possuir duas cópias do gene e manifestar a característica.

Começamos por Lily. A ordem em que as pessoas são consideradas não importa, desde que os valores corretos sejam multiplicados, pois a multiplicação é comutativa.

Lily possui zero cópias do gene com probabilidade `0.96`, valor de `PROBS["gene"][0]`. Sabendo que ela possui zero cópias, a probabilidade de não manifestar a característica é `0.99`, valor de `PROBS["trait"][0][False]`. Portanto, a probabilidade de Lily possuir zero cópias do gene e não manifestar a característica é:

```text
0.96 * 0.99 = 0.9504
```

Em seguida, consideramos James. Ele possui duas cópias do gene com probabilidade `0.01`, valor de `PROBS["gene"][2]`. Sabendo que ele possui duas cópias, a probabilidade de manifestar a característica é `0.65`. Portanto, a probabilidade de James possuir duas cópias do gene e manifestar a característica é:

```text
0.01 * 0.65 = 0.0065
```

Por fim, consideramos Harry. Qual é a probabilidade de ele possuir uma cópia do gene? Isso pode acontecer de duas maneiras: Harry recebe o gene da mãe, mas não do pai, ou recebe o gene do pai, mas não da mãe.

Lily, sua mãe, possui zero cópias do gene. Assim, Harry receberá o gene dela com probabilidade `0.01`, valor de `PROBS["mutation"]`, pois a única forma de isso ocorrer é por meio de uma mutação. A probabilidade de ele não receber o gene da mãe é `0.99`.

James, seu pai, possui duas cópias do gene. Assim, Harry receberá o gene dele com probabilidade `0.99`, valor de `1 - PROBS["mutation"]`, e não o receberá com probabilidade `0.01`, correspondente à probabilidade de mutação.

Os dois casos podem ser somados para calcular a probabilidade de Harry possuir exatamente uma cópia do gene:

```text
0.01 * 0.01 + 0.99 * 0.99 = 0.9802
```

Sabendo que Harry possui uma cópia do gene, a probabilidade de ele não manifestar a característica é `0.44`, valor de `PROBS["trait"][1][False]`. Portanto, a probabilidade de Harry possuir uma cópia do gene e não manifestar a característica é:

```text
0.9802 * 0.44 = 0.431288
```

A probabilidade conjunta completa é obtida multiplicando os valores calculados para as três pessoas:

```text
0.9504 * 0.0065 * 0.431288 = 0.0026643247488
```

## Dicas

- Para calcular a probabilidade conjunta de vários eventos, multiplique as probabilidades correspondentes.
- Para uma criança, lembre-se de que a probabilidade de possuir certa quantidade de cópias do gene é condicional à quantidade de cópias possuída por seus pais.

## Testes

Para acompanhar o progresso da sua implementação, execute:

```bash
python test_heredity.py
```

O script apresenta os testes agrupados por função, mostra os valores esperados e obtidos e fornece dicas quando encontra uma falha. Esses testes são auxiliares e não garantem que todos os casos possíveis estejam corretos.

Você não deve importar módulos que não façam parte da biblioteca padrão do Python, com exceção de `numpy` e `pandas`, expressamente autorizados pela especificação da atividade.

Existem ferramentas capazes de simplificar alguns destes projetos, mas esse não é o objetivo da atividade. O propósito é compreender e implementar os conceitos em um nível mais fundamental. Se o uso de uma ferramenta não foi autorizado, ela não deve ser utilizada.

---

## Atribuição e Licença

Material original: **CS50’s Introduction to Artificial Intelligence with Python — Heredity**, de CS50/Harvard University.

Este documento é uma tradução e adaptação do [material original](https://cs50.harvard.edu/ai/projects/2/heredity/). As imagens permanecem hospedadas no site do CS50.

O material original e esta adaptação estão licenciados sob a [Licença Internacional Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
