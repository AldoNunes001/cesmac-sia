"""
Script de verificação das funções de generate.py.

Este script NÃO usa o módulo unittest de propósito: a ideia é que qualquer
aluno consiga executar ``python test_crossword.py`` e entender imediatamente,
em português, o que foi testado, o que era esperado e o que o código
realmente retornou.

Os testes ajudam a acompanhar o progresso, mas não substituem a leitura da
especificação nem garantem que todos os casos possíveis foram cobertos.

Como executar:
    cd crossword
    python test_crossword.py

Por padrão, o arquivo testado é generate.py. Para validar outro arquivo que
mantenha a mesma interface, o professor pode definir CROSSWORD_TEST_MODULE.
Por exemplo:
    CROSSWORD_TEST_MODULE=generate_gabarito python test_crossword.py
"""

import importlib
import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from crossword import Crossword, Variable  # noqa: E402


MODULE_NAME = os.environ.get("CROSSWORD_TEST_MODULE", "generate")
generate = importlib.import_module(MODULE_NAME)
CrosswordCreator = generate.CrosswordCreator


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

    def check_condition(
        self,
        description,
        actual_fn,
        condition,
        expected_description,
        hint=None,
    ):
        """Valida o resultado de ``actual_fn`` usando ``condition``."""
        try:
            actual = actual_fn()
            ok = condition(actual)
        except Exception as error:
            actual = f"{type(error).__name__}: {error}"
            ok = False

        self._register(
            ok,
            description,
            expected_description,
            actual,
            hint,
        )

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
            print(f"  {name:<28} {passed}/{total} testes passaram  [{status}]")

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


def make_creator(number=0):
    """Cria um jogo e seu resolvedor usando um conjunto de dados oficial."""
    crossword = Crossword(
        os.path.join(BASE_DIR, "data", f"structure{number}.txt"),
        os.path.join(BASE_DIR, "data", f"words{number}.txt"),
    )
    return crossword, CrosswordCreator(crossword)


def get_variable(crossword, i, j, direction, length):
    """Localiza uma variável por suas quatro propriedades."""
    matches = [
        var
        for var in crossword.variables
        if (
            var.i == i
            and var.j == j
            and var.direction == direction
            and var.length == length
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Não foi possível localizar uma única variável com "
            f"os dados {(i, j, direction, length)}."
        )

    return matches[0]


def variable_id(var):
    """Converte uma variável para uma representação simples e estável."""
    return var.i, var.j, var.direction, var.length


def structure0_variables(crossword):
    """Retorna as quatro variáveis de structure0 com nomes descritivos."""
    across_3 = get_variable(crossword, 0, 1, Variable.ACROSS, 3)
    down_5 = get_variable(crossword, 0, 1, Variable.DOWN, 5)
    down_4 = get_variable(crossword, 1, 4, Variable.DOWN, 4)
    across_4 = get_variable(crossword, 4, 1, Variable.ACROSS, 4)
    return across_3, down_5, down_4, across_4


r = Reporter()


# ---------------------------------------------------------------------------
# enforce_node_consistency()
# ---------------------------------------------------------------------------
r.section("enforce_node_consistency")


def exact_node_consistent_domains():
    crossword, creator = make_creator(0)
    across_3, down_5, _down_4, _across_4 = structure0_variables(crossword)
    returned = creator.enforce_node_consistency()
    return (
        returned,
        creator.domains[across_3],
        creator.domains[down_5],
    )


r.check(
    "Deve manter exatamente as palavras com o comprimento correto",
    exact_node_consistent_domains,
    (
        None,
        {"ONE", "SIX", "TEN", "TWO"},
        {"EIGHT", "SEVEN", "THREE"},
    ),
    hint=(
        "Para cada variável, remova toda palavra cujo len seja diferente "
        "de var.length. A função não precisa retornar valor."
    ),
)


def all_domains_have_correct_lengths():
    crossword, creator = make_creator(1)
    creator.enforce_node_consistency()
    return all(
        len(word) == var.length
        for var in crossword.variables
        for word in creator.domains[var]
    )


r.check(
    "Depois da consistência de nó, todos os valores devem ter tamanho válido",
    all_domains_have_correct_lengths,
    True,
)


def valid_words_are_not_removed():
    crossword, creator = make_creator(0)
    _across_3, _down_5, down_4, across_4 = structure0_variables(crossword)
    creator.enforce_node_consistency()
    expected = {"FIVE", "FOUR", "NINE"}
    return creator.domains[down_4], creator.domains[across_4]


r.check(
    "Palavras válidas não devem ser removidas apenas por seu conteúdo",
    valid_words_are_not_removed,
    ({"FIVE", "FOUR", "NINE"}, {"FIVE", "FOUR", "NINE"}),
    hint="A restrição unária considera somente o comprimento da palavra.",
)


# ---------------------------------------------------------------------------
# revise()
# ---------------------------------------------------------------------------
r.section("revise")


def revise_removes_unsupported_values():
    crossword, creator = make_creator(0)
    x, y, _down_4, _across_4 = structure0_variables(crossword)
    creator.domains[x] = {"ONE", "SIX", "TEN"}
    creator.domains[y] = {"SEVEN", "THREE"}
    y_before = creator.domains[y].copy()
    returned = creator.revise(x, y)
    return returned, creator.domains[x], creator.domains[y] == y_before


r.check(
    "Deve remover de x os valores sem suporte em y e retornar True",
    revise_removes_unsupported_values,
    (True, {"SIX", "TEN"}, True),
    hint=(
        "Na interseção (0, 0), ONE não combina com nenhuma palavra de y. "
        "O domínio de y deve permanecer inalterado."
    ),
)


def revise_without_changes():
    crossword, creator = make_creator(0)
    x, y, _down_4, _across_4 = structure0_variables(crossword)
    creator.domains[x] = {"SIX"}
    creator.domains[y] = {"SEVEN"}
    returned = creator.revise(x, y)
    return returned, creator.domains[x], creator.domains[y]


r.check(
    "Deve retornar False quando todos os valores de x possuem suporte",
    revise_without_changes,
    (False, {"SIX"}, {"SEVEN"}),
)


def revise_non_neighbors():
    crossword, creator = make_creator(0)
    across_3, _down_5, down_4, _across_4 = structure0_variables(crossword)
    creator.domains[across_3] = {"ONE"}
    creator.domains[down_4] = {"FIVE"}
    returned = creator.revise(across_3, down_4)
    return returned, creator.domains[across_3], creator.domains[down_4]


r.check(
    "Variáveis sem interseção não devem ter seus domínios alterados",
    revise_non_neighbors,
    (False, {"ONE"}, {"FIVE"}),
    hint="Consulte self.crossword.overlaps[x, y] antes de comparar letras.",
)


# ---------------------------------------------------------------------------
# ac3()
# ---------------------------------------------------------------------------
r.section("ac3")


def ac3_structure0_domains():
    crossword, creator = make_creator(0)
    variables = structure0_variables(crossword)
    creator.enforce_node_consistency()
    returned = creator.ac3()
    domains = tuple(
        tuple(sorted(creator.domains[var]))
        for var in variables
    )
    return returned, domains


r.check(
    "AC-3 completo deve propagar as restrições por todos os arcos",
    ac3_structure0_domains,
    (
        True,
        (
            ("SIX",),
            ("SEVEN",),
            ("FIVE", "NINE"),
            ("NINE",),
        ),
    ),
    hint=(
        "Quando revise(x, y) alterar x, recoloque na fila os arcos "
        "(z, x) para cada vizinha z diferente de y."
    ),
)


def ac3_respects_initial_arcs():
    crossword, creator = make_creator(0)
    x, y, down_4, across_4 = structure0_variables(crossword)
    creator.domains[x] = {"ONE", "SIX"}
    creator.domains[y] = {"SEVEN"}
    other_before = (
        creator.domains[down_4].copy(),
        creator.domains[across_4].copy(),
    )
    returned = creator.ac3(arcs=[(x, y)])
    other_after = (
        creator.domains[down_4],
        creator.domains[across_4],
    )
    return returned, creator.domains[x], other_after == other_before


r.check(
    "Com arcs informado, a fila deve começar somente com esses arcos",
    ac3_respects_initial_arcs,
    (True, {"SIX"}, True),
)


def ac3_detects_empty_domain():
    crossword, creator = make_creator(0)
    x, y, _down_4, _across_4 = structure0_variables(crossword)
    creator.domains[x] = {"ONE"}
    creator.domains[y] = {"SEVEN"}
    returned = creator.ac3(arcs=[(x, y)])
    return returned, creator.domains[x]


r.check(
    "Se uma revisão esvaziar um domínio, AC-3 deve retornar False",
    ac3_detects_empty_domain,
    (False, set()),
    hint="Verifique o domínio de x imediatamente depois de revise(x, y).",
)


# ---------------------------------------------------------------------------
# assignment_complete()
# ---------------------------------------------------------------------------
r.section("assignment_complete")

r.check(
    "Uma atribuição vazia não deve ser considerada completa",
    lambda: make_creator(0)[1].assignment_complete({}),
    False,
)


def partial_assignment_is_incomplete():
    crossword, creator = make_creator(0)
    first_variable = next(iter(crossword.variables))
    return creator.assignment_complete({first_variable: "QUALQUER"})


r.check(
    "Uma atribuição com apenas parte das variáveis deve ser incompleta",
    partial_assignment_is_incomplete,
    False,
)


def every_variable_is_complete_regardless_of_values():
    crossword, creator = make_creator(0)
    assignment = {var: None for var in crossword.variables}
    return creator.assignment_complete(assignment)


r.check(
    "Todas as variáveis presentes devem formar uma atribuição completa",
    every_variable_is_complete_regardless_of_values,
    True,
    hint=(
        "assignment_complete verifica se as variáveis receberam valores; "
        "a validade dos valores pertence a consistent."
    ),
)


# ---------------------------------------------------------------------------
# consistent()
# ---------------------------------------------------------------------------
r.section("consistent")

r.check(
    "A atribuição vazia deve ser consistente",
    lambda: make_creator(0)[1].consistent({}),
    True,
)


def wrong_length_is_inconsistent():
    crossword, creator = make_creator(0)
    across_3, _down_5, _down_4, _across_4 = structure0_variables(crossword)
    return creator.consistent({across_3: "FOUR"})


r.check(
    "Uma palavra com comprimento incorreto deve ser inconsistente",
    wrong_length_is_inconsistent,
    False,
)


def repeated_word_is_inconsistent():
    crossword, creator = make_creator(0)
    _across_3, _down_5, down_4, across_4 = structure0_variables(crossword)
    return creator.consistent({down_4: "FIVE", across_4: "FIVE"})


r.check(
    "A mesma palavra atribuída a duas variáveis deve ser inconsistente",
    repeated_word_is_inconsistent,
    False,
    hint="Compare len(assignment.values()) com len(set(assignment.values())).",
)


def conflicting_overlap_is_inconsistent():
    crossword, creator = make_creator(0)
    across_3, down_5, _down_4, _across_4 = structure0_variables(crossword)
    return creator.consistent({across_3: "ONE", down_5: "SEVEN"})


r.check(
    "Palavras que discordam na interseção devem ser inconsistentes",
    conflicting_overlap_is_inconsistent,
    False,
    hint=(
        "Use o par de índices em self.crossword.overlaps para comparar "
        "os caracteres das duas palavras."
    ),
)


def valid_complete_assignment_is_consistent():
    crossword, creator = make_creator(0)
    across_3, down_5, down_4, across_4 = structure0_variables(crossword)
    assignment = {
        across_3: "SIX",
        down_5: "SEVEN",
        down_4: "FIVE",
        across_4: "NINE",
    }
    return creator.consistent(assignment)


r.check(
    "Uma solução completa com palavras distintas e compatíveis deve passar",
    valid_complete_assignment_is_consistent,
    True,
)


# ---------------------------------------------------------------------------
# order_domain_values()
# ---------------------------------------------------------------------------
r.section("order_domain_values")


def least_constraining_order():
    crossword, creator = make_creator(0)
    var, neighbor, _down_4, _across_4 = structure0_variables(crossword)
    creator.domains[var] = {"ONE", "SIX", "TEN"}
    creator.domains[neighbor] = {"SEVEN", "THREE"}
    return creator.order_domain_values(var, {})


r.check_condition(
    "O valor que elimina mais opções deve aparecer por último",
    least_constraining_order,
    lambda result: (
        isinstance(result, list)
        and len(result) == 3
        and set(result[:2]) == {"SIX", "TEN"}
        and result[2] == "ONE"
    ),
    "uma lista com SIX e TEN nas duas primeiras posições e ONE por último",
    hint=(
        "Conte, para cada palavra, quantos valores incompatíveis existem "
        "nos domínios das vizinhas ainda não atribuídas."
    ),
)


def assigned_neighbors_are_ignored():
    crossword, creator = make_creator(0)
    assigned_neighbor, var, _down_4, free_neighbor = structure0_variables(
        crossword
    )
    creator.domains[var] = {"SAAAA", "TBBBB"}
    creator.domains[assigned_neighbor] = {"SXX", "SYY", "SZZ"}
    creator.domains[free_neighbor] = {"BXXX"}
    assignment = {assigned_neighbor: "SXX"}
    return creator.order_domain_values(var, assignment)


r.check(
    "Vizinhas já atribuídas não devem participar da contagem",
    assigned_neighbors_are_ignored,
    ["TBBBB", "SAAAA"],
)


def ordering_does_not_change_domains():
    crossword, creator = make_creator(0)
    var, neighbor, _down_4, _across_4 = structure0_variables(crossword)
    creator.domains[var] = {"ONE", "SIX", "TEN"}
    creator.domains[neighbor] = {"SEVEN", "THREE"}
    before = {
        variable: values.copy()
        for variable, values in creator.domains.items()
    }
    creator.order_domain_values(var, {})
    return creator.domains == before


r.check(
    "Ordenar os valores não deve modificar nenhum domínio",
    ordering_does_not_change_domains,
    True,
)


# ---------------------------------------------------------------------------
# select_unassigned_variable()
# ---------------------------------------------------------------------------
r.section("select_unassigned_variable")


def selects_minimum_remaining_values():
    crossword, creator = make_creator(0)
    across_3, down_5, down_4, across_4 = structure0_variables(crossword)
    creator.domains[across_3] = {"ONE"}
    creator.domains[down_5] = {"EIGHT", "SEVEN"}
    creator.domains[down_4] = {"FIVE", "FOUR", "NINE"}
    creator.domains[across_4] = {"FIVE", "FOUR", "NINE"}
    return variable_id(creator.select_unassigned_variable({}))


r.check(
    "MRV deve escolher a variável com menos valores restantes",
    selects_minimum_remaining_values,
    (0, 1, Variable.ACROSS, 3),
)


def degree_breaks_mrv_tie():
    crossword, creator = make_creator(0)
    across_3, down_5, down_4, across_4 = structure0_variables(crossword)

    for var in crossword.variables:
        creator.domains[var] = {"A", "B"}

    selected = creator.select_unassigned_variable({})
    return variable_id(selected), {
        variable_id(down_5),
        variable_id(across_4),
    }, {
        variable_id(across_3),
        variable_id(down_4),
    }


r.check_condition(
    "Em empate de MRV, deve escolher uma variável com o maior grau",
    degree_breaks_mrv_tie,
    lambda result: result[0] in result[1] and result[0] not in result[2],
    "uma das duas variáveis de grau 2",
    hint="Use len(self.crossword.neighbors(var)) como segundo critério.",
)


def assigned_variable_is_not_selected():
    crossword, creator = make_creator(0)
    _across_3, down_5, _down_4, across_4 = structure0_variables(crossword)

    for var in crossword.variables:
        creator.domains[var] = {"A"}

    selected = creator.select_unassigned_variable({down_5: "ABCDE"})
    return variable_id(selected), variable_id(across_4)


r.check(
    "Uma variável que já está em assignment não pode ser selecionada",
    assigned_variable_is_not_selected,
    (
        (4, 1, Variable.ACROSS, 4),
        (4, 1, Variable.ACROSS, 4),
    ),
)


# ---------------------------------------------------------------------------
# backtrack()
# ---------------------------------------------------------------------------
r.section("backtrack")


def backtrack_solves_structure0():
    crossword, creator = make_creator(0)
    creator.enforce_node_consistency()
    assignment = creator.backtrack({})

    if assignment is None:
        return False, False, False, set()

    return (
        True,
        creator.assignment_complete(assignment),
        creator.consistent(assignment),
        set(assignment.values()),
    )


r.check(
    "Deve encontrar uma atribuição completa e consistente para structure0",
    backtrack_solves_structure0,
    (True, True, True, {"SIX", "SEVEN", "FIVE", "NINE"}),
    hint=(
        "Escolha uma variável, teste os valores na ordem indicada, chame "
        "backtrack recursivamente e desfaça a tentativa quando ela falhar."
    ),
)


def backtrack_respects_partial_assignment():
    crossword, creator = make_creator(0)
    across_3, _down_5, _down_4, _across_4 = structure0_variables(crossword)
    creator.enforce_node_consistency()
    assignment = creator.backtrack({across_3: "SIX"})

    if assignment is None:
        return None, False, False

    return (
        assignment.get(across_3),
        creator.assignment_complete(assignment),
        creator.consistent(assignment),
    )


r.check(
    "Uma atribuição parcial válida deve ser preservada e completada",
    backtrack_respects_partial_assignment,
    ("SIX", True, True),
)


def backtrack_returns_none_for_empty_domain():
    crossword, creator = make_creator(0)
    across_3, _down_5, _down_4, _across_4 = structure0_variables(crossword)
    creator.enforce_node_consistency()
    creator.domains[across_3] = set()
    return creator.backtrack({})


r.check(
    "Se uma variável não possui valores possíveis, deve retornar None",
    backtrack_returns_none_for_empty_domain,
    None,
)


# ---------------------------------------------------------------------------
# Integração
# ---------------------------------------------------------------------------
r.section("integração: solve")


def solve_dataset(number):
    _crossword, creator = make_creator(number)
    assignment = creator.solve()

    if assignment is None:
        return False, False, False

    return (
        True,
        creator.assignment_complete(assignment),
        creator.consistent(assignment),
    )


r.check(
    "As funções juntas devem resolver structure1/words1",
    lambda: solve_dataset(1),
    (True, True, True),
)

r.check(
    "As funções juntas devem resolver structure2/words2",
    lambda: solve_dataset(2),
    (True, True, True),
    hint=(
        "Se este teste estiver lento, revise AC-3, MRV, grau e a ordem dos "
        "valores do domínio."
    ),
)


if __name__ == "__main__":
    ok = r.summary()
    sys.exit(0 if ok else 1)
