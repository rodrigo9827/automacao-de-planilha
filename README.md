# Automação de Atendimento — Gestantes

Programa de apoio para as enfermeiras lançarem os dados do atendimento
de gestantes diretamente numa planilha Excel Online (SharePoint), sem
precisar digitar linha por linha manualmente.

## ⚠️ Segurança — leia antes de usar

- O programa **nunca salva e-mail ou senha** em nenhum arquivo, log ou
  configuração. Essas informações ficam só na memória enquanto o
  programa está rodando e são apagadas da tela assim que o botão
  "Iniciar" é clicado.
- **Nunca** coloque e-mail, senha ou links reais de planilha dentro
  deste README ou de qualquer arquivo versionado no Git. Se algum dado
  sensível for commitado por engano, ele continua acessível no
  histórico do repositório mesmo depois de apagado num commit novo —
  é preciso reescrever o histórico (ou trocar a senha imediatamente).
- Mantenha este repositório **privado**.

## Uso por outros setores

O botão **"+ Inserir paciente"** abre uma janela com uma única caixa
de texto, onde cada linha digitada vira uma célula da planilha, sem
nenhum campo fixo (CNS, status, etc.). Serve tanto para o setor de
atendimento a gestantes quanto para qualquer outro setor que precise
inserir uma linha de dados numa planilha automatizada por este
programa — o formato de entrada é o mesmo, o que muda é só o que cada
setor decide escrever em cada linha.

## Como funciona

1. Executa `inicializacao.bat`, que verifica/instala o Python e as
   dependências, e abre a interface do programa.
2. Clica em **"+ Inserir paciente"** e digita as informações na caixa
   de texto — cada linha vira uma célula da planilha, na ordem em que
   aparece. Deixar uma linha em branco pula uma célula, igual ao
   comportamento original. O programa gera o arquivo `.txt` sozinho
   na pasta `atendimento_rodada`, na Área de Trabalho. Não precisa
   mais abrir o Bloco de Notas na mão.
   - Repete esse passo para cada paciente da rodada. O contador na
     tela mostra quantos estão na fila.
3. Na interface, informa:
   - o link da planilha (Excel Online / SharePoint)
   - o e-mail e a senha da conta Microsoft
   - quantas células por linha a planilha usa (padrão: 5)
4. Com a fila pronta, clica em "Iniciar automação". O programa abre
   o Edge, faz login, aguarda a planilha carregar e digita os dados
   de cada paciente/registro, célula por célula, pulando de linha
   automaticamente.
5. Ao final, os arquivos `.txt` já processados são movidos para
   `atendimento_rodada/processados/<data>/` — não é mais necessário
   apagar os arquivos manualmente.

## Formato do arquivo de paciente

Cada linha do `.txt` vira uma célula da planilha, na ordem em que
aparece. Uma linha em branco cria uma célula vazia de propósito
(pressione Enter para deixar uma célula em branco). Exemplo digitado
na caixa de texto:

```
CNS:123456789
nome do paciente de exemplo
atendeu
Próxima ligação: 25/12/2026

observações
```

Não existe mais um formato fixo obrigatório — cada setor decide o
que escrever em cada linha, de acordo com a ordem das colunas da sua
própria planilha.

- Nome do arquivo não importa para o sistema — só evite espaços,
  prefira `_` (underline).
- Recomendado salvar sempre em `atendimento_rodada`, e não direto na
  pasta do programa.

## Requisitos técnicos

- Windows com Microsoft Edge instalado (a automação abre o Edge
  controlada pelo Selenium).
- Conexão com a internet (para instalar o Python/dependências na
  primeira vez, e para o Selenium baixar automaticamente o driver do
  Edge compatível com a versão instalada).
- Conta Microsoft **sem verificação em duas etapas (MFA)** — se a
  conta tiver MFA ativado, o login automático vai parar na etapa do
  código/aprovação e vai ser necessário completar manualmente na
  janela aberta.

## Limitações conhecidas

- Antes de começar a digitar, o programa usa o atalho Ctrl+End para
  pular para a última célula com dado na planilha e começar a
  próxima linha a partir dali — assim nunca sobrescreve o que já foi
  preenchido antes (por outra pessoa ou numa rodada anterior). Isso
  depende do comportamento padrão do Ctrl+End do Excel Online; não
  foi possível testar esse passo especificamente fora do ambiente
  real (sandbox de desenvolvimento não tem acesso a navegador/Excel
  Online) — vale confirmar visualmente na primeira rodada em produção.
- O Excel Online desenha a grade de células como imagem (canvas), não
  como elementos individuais na página. Por isso, depois de aberta a
  planilha, a navegação entre células continua sendo feita por teclado
  (Tab / Enter), e não por clique direto numa célula específica.
- Se a Microsoft alterar o layout da página de login, os
  identificadores usados em `core/web_automation.py` podem precisar de
  ajuste (estão comentados no próprio código).
- O navegador é deixado aberto ao final da execução, de propósito,
  para conferência visual antes de fechar manualmente.

## Estrutura do projeto

```
automacao-atendimento/
├── main.py                 # interface (Tkinter) — ponto de entrada
├── core/
│   ├── pacientes.py         # leitura e organização dos arquivos .txt
│   └── web_automation.py    # login e preenchimento via Selenium
├── assets/                  # ícone da janela
├── requirements.txt
├── inicializacao.bat
├── desinstalacao.bat
└── .gitignore
```

## Desinstalação

Execute `desinstalacao.bat`. Ele pede confirmação antes de apagar a
pasta do programa, e pergunta separadamente se deseja também
desinstalar o Python (opcional).
