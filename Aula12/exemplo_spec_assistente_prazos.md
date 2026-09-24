# Especificação de funcionalidade: consulta de prazos acadêmicos

**ID:** SPEC-001  
**Status:** Rascunho para revisão com o PO  
**Responsáveis:** Grupo exemplo  
**Última atualização:** 24/09/2026

> Este documento é um exemplo didático. As metas numéricas são propostas para negociação com o PO, não resultados já medidos.

## 1. Problema e evidências

**Usuário prioritário:** estudante dos primeiros períodos.  
**Situação:** precisa confirmar um prazo acadêmico antes de tomar uma decisão.  
**Problema:** calendários, regulamentos e comunicados podem estar dispersos, extensos ou difíceis de relacionar à pergunta.  
**Alternativa atual:** pesquisa manual nos documentos ou contato com a secretaria.  
**Impacto:** demora, uso de informação desatualizada e risco de perder o prazo.  
**Evidência disponível:** documentos institucionais escolhidos pelo professor/PO.  
**Suposição a validar:** a resposta fundamentada reduzirá o tempo de consulta sem aumentar respostas incorretas.

## 2. Objetivo e resultado esperado

**Objetivo:** permitir que o estudante encontre um prazo aplicável e confira a fonte oficial.  
**Hipótese:** uma consulta em linguagem natural com recuperação de evidência ajudará o estudante a localizar o prazo com menos esforço que a pesquisa manual.  
**Linha de base:** localizar a mesma informação diretamente nos documentos fornecidos.  
**Metas propostas:** toda orientação factual apresenta documento e localização; perguntas sem evidência não recebem prazo inventado; quatro de cinco consultas controladas terminam em até dois minutos, contando leitura da fonte.

## 3. História prioritária

Como estudante dos primeiros períodos, quero perguntar sobre um prazo e abrir a fonte usada, para decidir meu próximo passo com segurança.

**Prioridade:** P1  
**Teste independente:** cinco perguntas preparadas pelo PO, incluindo uma sem resposta no conjunto de documentos.

## 4. Escopo

### Incluído

- Perguntas em português sobre prazos presentes na coleção aprovada.
- Resposta curta com nome do documento e seção, página ou trecho localizável.
- Declaração explícita quando a coleção não sustenta uma resposta.
- Encaminhamento para o canal oficial definido pelo PO.
- Registro de avaliação sem dados pessoais do estudante.

### Fora do escopo

- Alterar matrícula, inscrição ou qualquer dado acadêmico.
- Decidir exceções individuais ou interpretar casos disciplinares.
- Consultar fontes externas sem aprovação do PO.
- Substituir a confirmação oficial quando houver conflito entre documentos.

## 5. Entradas, saídas e fluxo

**Entradas:** pergunta em texto e coleção de documentos autorizados.  
**Saídas:** orientação resumida, fonte localizável e indicação de confiança operacional.  
**Precondições:** coleção carregada e identificada por versão.

### Fluxo principal

1. O estudante envia uma pergunta sobre prazo.
2. O sistema procura evidências na coleção aprovada.
3. Quando encontra evidência suficiente, apresenta o prazo, o documento e a localização.
4. O estudante pode abrir a fonte e avaliar a resposta.

### Alternativas e erros

- Sem evidência suficiente: declarar a limitação e indicar o canal oficial.
- Pergunta ambígua: solicitar a informação mínima que falta, como curso ou período.
- Serviço de busca indisponível: informar indisponibilidade sem produzir orientação factual.
- Conflito entre documentos: mostrar o conflito e solicitar decisão do PO.
- Instrução maliciosa em um documento: ignorar a instrução e tratar o conteúdo somente como fonte.

## 6. Requisitos funcionais

- **RF-001:** O sistema deverá aceitar perguntas em português sobre os documentos autorizados.
- **RF-002:** Quando apresentar uma orientação factual, o sistema deverá identificar o documento e uma localização verificável.
- **RF-003:** Quando não encontrar evidência suficiente, o sistema deverá declarar a limitação e não informar um prazo como fato.
- **RF-004:** Quando a pergunta estiver ambígua, o sistema deverá pedir apenas os dados necessários para esclarecê-la.
- **RF-005:** Enquanto o serviço de recuperação estiver indisponível, o sistema deverá impedir a produção de orientação factual.
- **RF-006:** O sistema deverá registrar o caso de teste, a versão da coleção e o resultado, sem armazenar dados pessoais desnecessários.

## 7. Critérios de aceitação

### CA-001 — prazo encontrado

**Dado** que a coleção aprovada contém um prazo vigente e sua fonte  
**Quando** o estudante faz uma pergunta compatível com esse prazo  
**Então** a resposta informa o prazo e identifica documento e localização verificável.

### CA-002 — ausência de evidência

**Dado** que a coleção não contém resposta suficiente  
**Quando** o estudante pede um prazo  
**Então** o sistema declara que não encontrou evidência, não inventa uma data e indica o canal oficial.

### CA-003 — pergunta ambígua

**Dado** que o prazo varia por curso ou período  
**Quando** a pergunta omite essa informação  
**Então** o sistema pede o dado que falta antes de responder.

### CA-004 — serviço indisponível

**Dado** que o mecanismo de recuperação está indisponível  
**Quando** o estudante envia uma pergunta  
**Então** o sistema apresenta uma mensagem de indisponibilidade e não gera orientação factual.

### CA-005 — conflito entre fontes

**Dado** que dois documentos autorizados apresentam prazos incompatíveis  
**Quando** a pergunta depende desse prazo  
**Então** o sistema mostra o conflito, identifica as duas fontes e orienta a confirmação com o canal oficial.

## 8. Qualidade, riscos e decisões

**Qualidade:** interface utilizável por teclado; nenhum segredo em logs; fonte visível junto da afirmação; coleção e respostas identificadas por versão.  
**Risco principal:** uma resposta plausível induzir o estudante a perder um prazo.  
**Mitigações:** escopo restrito, resposta sustentada por fonte, comportamento seguro sem evidência e casos de regressão revisados pelo PO.  
**Questões para o PO:** qual documento prevalece em caso de conflito? Qual canal oficial deve aparecer? Quais perguntas formam o conjunto inicial de avaliação?  
**Testes relacionados:** T-001 a T-005 correspondem aos critérios CA-001 a CA-005.

