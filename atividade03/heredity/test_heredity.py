"""
Script de verificação das funções de heredity.py.

Este script NÃO usa o módulo unittest de propósito: a ideia é que qualquer
aluno consiga executar ``python test_heredity.py`` e entender imediatamente,
em português, o que foi testado, o que era esperado e o que o código
realmente retornou.

Os testes ajudam a acompanhar o progresso, mas não substituem a leitura da
especificação nem garantem que todos os casos possíveis foram cobertos.

Como executar:
    cd heredity
    python test_heredity.py
"""

import importlib
import itertools
import math
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Por padrão, os testes sempre verificam o arquivo entregue aos alunos.
# A variável de ambiente é útil apenas para o professor validar outro arquivo
# que preserve a mesma interface, como o gabarito.
MODULE_NAME = os.environ.get("HEREDITY_TEST_MODULE", "heredity")
heredity = importlib.import_module(MODULE_NAME)

joint_probability = heredity.joint_probability
update = heredity.update
normalize = heredity.normalize
load_data = heredity.load_data


class Reporter:
    """Coleta e exibe os resultados dos testes de forma explicativa."""

    def __init__(self):
        self.section_name = None
        self.sections_order = []
        self.sections = {}  # nome -> [passou, total]
        self.failures = []  # (seção, descrição, esperado, obtido, dica)

    def section(self, name):
        self.section_name = name
        self.sections_order.append(name)
        self.sections[name] = [0, 0]
        print()
        print("=" * 72)
        print(f" Testando: {name}")
        print("=" * 72)

    def _register(self, ok, description, expected, actual, hint):
        self.sections[self.section_name][1] += 1

        if ok:
            self.sections[self.section_name][0] += 1
            print(f"  [OK]     {description}")
            return

        self.failures.append(
            (self.section_name, description, expected, actual, hint)
        )
        print(f"  [FALHOU] {description}")
        print(f"           esperado: {expected}")
        print(f"           obtido:   {actual}")
        if hint:
            print(f"           dica: {hint}")

    def check(self, description, actual_fn, expected, hint=None):
        """Executa ``actual_fn`` e compara seu resultado com ``expected``."""
        try:
            actual = actual_fn()
            ok = actual == expected
        except Exception as error:
            actual = f"{type(error).__name__}: {error}"
            ok = False

        self._register(ok, description, expected, actual, hint)

    def check_close(
        self,
        description,
        actual_fn,
        expected,
        hint=None,
    ):
        """Compara números ou estruturas numéricas com pequena tolerância."""
        try:
            actual = actual_fn()
            ok = structures_close(actual, expected)
        except Exception as error:
            actual = f"{type(error).__name__}: {error}"
            ok = False

        self._register(ok, description, expected, actual, hint)

    def summary(self):
        print()
        print("=" * 72)
        print(" RESUMO POR FUNÇÃO")
        print("=" * 72)

        total_passed = 0
        total_all = 0

        for name in self.sections_order:
            passed, total = self.sections[name]
            total_passed += passed
            total_all += total
            status = "OK" if passed == total else "COM FALHAS"
            print(f"  {name:<24} {passed}/{total} testes passaram  [{status}]")

        print()
        print("-" * 72)
        print(f" TOTAL GERAL: {total_passed}/{total_all} testes passaram")
        print("-" * 72)

        if self.failures:
            print()
            print(f" {len(self.failures)} teste(s) falharam. Detalhe:")
            for section, description, _expected, _actual, _hint in self.failures:
                print(f"  - [{section}] {description}")
            print()
            print(" Revise as funções listadas acima. Role para cima para ver")
            print(" o motivo detalhado de cada falha (esperado x obtido).")
            return False

        print()
        print(" Parabéns! Todas as funções passaram em todos os testes.")
        return True


def structures_close(actual, expected):
    """Compara recursivamente números, dicionários e outras estruturas."""
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(
                structures_close(actual[key], expected[key])
                for key in expected
            )
        )

    if isinstance(expected, (list, tuple)):
        return (
            isinstance(actual, type(expected))
            and len(actual) == len(expected)
            and all(
                structures_close(actual_item, expected_item)
                for actual_item, expected_item in zip(actual, expected)
            )
        )

    if (
        isinstance(expected, (int, float))
        and not isinstance(expected, bool)
    ):
        return (
            isinstance(actual, (int, float))
            and not isinstance(actual, bool)
            and math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-12)
        )

    return actual == expected


def person(name, mother=None, father=None, trait=None):
    """Cria um registro de pessoa no formato usado por heredity.py."""
    return {
        "name": name,
        "mother": mother,
        "father": father,
        "trait": trait,
    }


def empty_probabilities(*names):
    """Cria distribuições zeradas para os nomes informados."""
    return {
        name: {
            "gene": {2: 0, 1: 0, 0: 0},
            "trait": {True: 0, False: 0},
        }
        for name in names
    }


def powerset(values):
    """Retorna todos os subconjuntos de ``values`` para o teste integrado."""
    values = list(values)
    return [
        set(combination)
        for combination in itertools.chain.from_iterable(
            itertools.combinations(values, size)
            for size in range(len(values) + 1)
        )
    ]


r = Reporter()


# ---------------------------------------------------------------------------
# joint_probability()
# ---------------------------------------------------------------------------
r.section("joint_probability")

single_person = {"Ada": person("Ada")}

r.check_close(
    "Pessoa sem pais, com 0 genes e sem característica",
    lambda: joint_probability(single_person, set(), set(), set()),
    0.9504,
    hint=(
        "Multiplique PROBS['gene'][0] por "
        "PROBS['trait'][0][False]."
    ),
)

r.check_close(
    "Pessoa sem pais, com 1 gene e com característica",
    lambda: joint_probability(
        single_person,
        {"Ada"},
        set(),
        {"Ada"},
    ),
    0.0168,
    hint=(
        "Para pessoas sem pais registrados, use a probabilidade "
        "incondicional de PROBS['gene']."
    ),
)

r.check_close(
    "Pessoa sem pais, com 2 genes e sem característica",
    lambda: joint_probability(
        single_person,
        set(),
        {"Ada"},
        set(),
    ),
    0.0035,
)

example_family = {
    "Harry": person("Harry", "Lily", "James"),
    "James": person("James", trait=True),
    "Lily": person("Lily", trait=False),
}

r.check_close(
    "Exemplo completo de Harry, James e Lily da especificação",
    lambda: joint_probability(
        example_family,
        {"Harry"},
        {"James"},
        {"James"},
    ),
    0.0026643247488,
    hint=(
        "Para Harry, some os dois casos que produzem exatamente um gene: "
        "receber só da mãe ou receber só do pai."
    ),
)

child_family = {
    "Mãe": person("Mãe"),
    "Pai": person("Pai"),
    "Criança": person("Criança", "Mãe", "Pai"),
}

r.check_close(
    "Criança com 2 genes, quando a mãe tem 1 e o pai tem 0",
    lambda: joint_probability(
        child_family,
        {"Mãe"},
        {"Criança"},
        set(),
    ),
    0.00002195424,
    hint=(
        "Para a criança receber dois genes, ambos os pais precisam "
        "transmitir o gene. Considere também a mutação."
    ),
)

r.check_close(
    "Criança com 0 genes, quando a mãe tem 2 e o pai tem 1",
    lambda: joint_probability(
        child_family,
        {"Pai"},
        {"Mãe"},
        set(),
    ),
    0.00000022869,
    hint=(
        "Para a criança ter zero genes, nenhum dos pais pode transmitir "
        "o gene após considerar a mutação."
    ),
)


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------
r.section("update")


def update_once():
    probabilities = empty_probabilities("Ana", "Beto")
    result = update(
        probabilities,
        {"Ana"},
        {"Beto"},
        {"Beto"},
        0.125,
    )
    return result, probabilities


r.check_close(
    "Deve adicionar p ao gene e à característica corretos de cada pessoa",
    update_once,
    (
        None,
        {
            "Ana": {
                "gene": {2: 0, 1: 0.125, 0: 0},
                "trait": {True: 0, False: 0.125},
            },
            "Beto": {
                "gene": {2: 0.125, 1: 0, 0: 0},
                "trait": {True: 0.125, False: 0},
            },
        },
    ),
    hint=(
        "A função deve alterar probabilities diretamente e retornar None. "
        "Quem não está em one_gene nem two_genes possui zero genes."
    ),
)


def update_accumulates():
    probabilities = empty_probabilities("Ada")

    update(probabilities, {"Ada"}, set(), {"Ada"}, 0.1)
    update(probabilities, {"Ada"}, set(), {"Ada"}, 0.2)
    update(probabilities, set(), {"Ada"}, set(), 0.4)

    return probabilities


r.check_close(
    "Chamadas sucessivas devem somar probabilidades, não sobrescrevê-las",
    update_accumulates,
    {
        "Ada": {
            "gene": {2: 0.4, 1: 0.3, 0: 0},
            "trait": {True: 0.3, False: 0.4},
        }
    },
    hint="Use += p na posição apropriada de cada distribuição.",
)


def update_zero_genes_and_no_trait():
    probabilities = empty_probabilities("Ada")
    update(probabilities, set(), set(), set(), 0.75)
    return probabilities


r.check_close(
    "Pessoa ausente dos conjuntos deve atualizar 0 genes e trait False",
    update_zero_genes_and_no_trait,
    {
        "Ada": {
            "gene": {2: 0, 1: 0, 0: 0.75},
            "trait": {True: 0, False: 0.75},
        }
    },
)


# ---------------------------------------------------------------------------
# normalize()
# ---------------------------------------------------------------------------
r.section("normalize")


def normalize_one_person():
    probabilities = {
        "Ada": {
            "gene": {2: 2.0, 1: 3.0, 0: 5.0},
            "trait": {True: 1.0, False: 3.0},
        }
    }
    result = normalize(probabilities)
    return result, probabilities


r.check_close(
    "Deve normalizar gene e trait separadamente e retornar None",
    normalize_one_person,
    (
        None,
        {
            "Ada": {
                "gene": {2: 0.2, 1: 0.3, 0: 0.5},
                "trait": {True: 0.25, False: 0.75},
            }
        },
    ),
    hint=(
        "Some cada distribuição separadamente e divida cada valor por "
        "essa soma. A função deve modificar o dicionário recebido."
    ),
)


def normalize_multiple_people():
    probabilities = {
        "Ada": {
            "gene": {2: 1.0, 1: 1.0, 0: 2.0},
            "trait": {True: 3.0, False: 1.0},
        },
        "Beto": {
            "gene": {2: 6.0, 1: 3.0, 0: 1.0},
            "trait": {True: 2.0, False: 8.0},
        },
    }
    normalize(probabilities)
    return probabilities


r.check_close(
    "Deve normalizar todas as distribuições de todas as pessoas",
    normalize_multiple_people,
    {
        "Ada": {
            "gene": {2: 0.25, 1: 0.25, 0: 0.5},
            "trait": {True: 0.75, False: 0.25},
        },
        "Beto": {
            "gene": {2: 0.6, 1: 0.3, 0: 0.1},
            "trait": {True: 0.2, False: 0.8},
        },
    },
)


def normalized_sums():
    probabilities = {
        "Ada": {
            "gene": {2: 0.4, 1: 1.7, 0: 7.9},
            "trait": {True: 0.37, False: 0.63},
        }
    }
    normalize(probabilities)
    return (
        sum(probabilities["Ada"]["gene"].values()),
        sum(probabilities["Ada"]["trait"].values()),
    )


r.check_close(
    "Após a normalização, cada distribuição deve somar 1",
    normalized_sums,
    (1.0, 1.0),
)


# ---------------------------------------------------------------------------
# Integração das três funções
# ---------------------------------------------------------------------------
r.section("integração")


def infer_probabilities(people):
    """Executa o mesmo processo de enumeração usado pela função main."""
    probabilities = empty_probabilities(*people)
    names = set(people)

    for have_trait in powerset(names):
        fails_evidence = any(
            (
                people[name]["trait"] is not None
                and people[name]["trait"] != (name in have_trait)
            )
            for name in names
        )
        if fails_evidence:
            continue

        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                probability = joint_probability(
                    people,
                    one_gene,
                    two_genes,
                    have_trait,
                )
                update(
                    probabilities,
                    one_gene,
                    two_genes,
                    have_trait,
                    probability,
                )

    normalize(probabilities)
    return probabilities


def family0_result():
    data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "family0.csv",
    )
    return infer_probabilities(load_data(data_path))


r.check_close(
    "As três funções juntas devem reproduzir o resultado de family0.csv",
    family0_result,
    {
        "Harry": {
            "gene": {
                2: 0.009183119746027276,
                1: 0.4556982701,
                0: 0.5351186101461487,
            },
            "trait": {
                True: 0.2665112452,
                False: 0.7334887548,
            },
        },
        "James": {
            "gene": {
                2: 0.1975683891,
                1: 0.5106382979,
                0: 0.2917933131,
            },
            "trait": {True: 1.0, False: 0.0},
        },
        "Lily": {
            "gene": {
                2: 0.0036190673146520524,
                1: 0.0136490539,
                0: 0.9827318788129458,
            },
            "trait": {True: 0.0, False: 1.0},
        },
    },
    hint=(
        "Se os testes individuais passaram, verifique se update acumula "
        "todos os cenários antes de normalize ser chamada."
    ),
)


if __name__ == "__main__":
    ok = r.summary()
    sys.exit(0 if ok else 1)
