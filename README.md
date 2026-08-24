# Automação de Atendimento — Gestantes

Programa de apoio para as enfermeiras lançarem os dados do atendimento
de gestantes diretamente numa planilha Excel Online (SharePoint), sem
precisar digitar linha por linha manualmente, recomendado o uso ao 
final do expediente.

## Segurança — leia antes de usar

- O programa **nunca salva e-mail ou senha** em nenhum arquivo, log ou
  configuração. Essas informações ficam só na memória enquanto o
  programa está rodando e são apagadas da tela assim que o botão
  "Iniciar" é clicado.

## Uso por outros setores

O botão **"+ Inserir paciente"** abre uma janela com uma única caixa
de texto, onde cada linha digitada vira uma célula da planilha, sem
nenhum campo fixo. Serve tanto para o setor de
atendimento a gestantes quanto para qualquer outro setor que precise
inserir uma linha de dados numa planilha com este
programa.

## Como funciona

1. Executa `inicializacao.bat`, que verifica/instala o Python e as
   dependências, e abre a interface do programa.
2. Clica em **"+ Inserir paciente"** e digita as informações na caixa
   de texto, cada linha vira uma célula da planilha, na ordem em que
   aparece. Deixar uma linha em branco pula uma célula. 
   O programa gera o arquivo `.txt` sozinho
   na pasta `atendimento_rodada`, na Área de Trabalho. Não precisa
   mais abrir o Bloco de Notas na mão.
   - Repete esse passo para cada paciente da rodada. O contador na
     tela mostra quantos pacientes estão na fila para inserir na planilha.
3. Na interface, informa:
   - o link da planilha (Excel Online / SharePoint)
   - o e-mail e a senha da conta Microsoft
   - quantas células por linha a planilha usa (padrão: 5)
4. Com a fila pronta, clica em "Iniciar automação". O programa abre
   o Edge, faz login, aguarda a planilha carregar e digita os dados
   de cada paciente/registro, célula por célula, pulando de linha
   automaticamente.
5. Ao final, os arquivos `.txt` já processados são movidos para
   `atendimento_rodada/processados/<data>/` — não é necessário
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
- Se o navegador já estiver com a sessão da Microsoft em cache (SSO),
  o programa detecta isso automaticamente e pula a etapa de login,
  indo direto para o preenchimento — não precisa se preocupar em
  deslogar antes de testar.

## Limitações conhecidas

- Antes de começar a digitar, o programa usa o atalho Ctrl+End para
  pular para a última célula com dado na planilha e começar a
  próxima linha a partir dali — assim nunca sobrescreve o que já foi
  preenchido antes (por outra pessoa ou numa rodada anterior). Isso
  depende do comportamento padrão do Ctrl+End 
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

```
$origem = "D:\Recovery_20260823_211809"
$destino = "D:\Recovery_20260823_211809\documentos_reais"
New-Item -ItemType Directory -Force -Path "$destino\docx" | Out-Null
New-Item -ItemType Directory -Force -Path "$destino\xlsx" | Out-Null
New-Item -ItemType Directory -Force -Path "$destino\pptx" | Out-Null
New-Item -ItemType Directory -Force -Path "$destino\office_antigo" | Out-Null

Add-Type -AssemblyName System.IO.Compression.FileSystem

$contador = 0
Get-ChildItem -Path $origem -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notlike "*\organizado_programas\*" -and $_.FullName -notlike "*\documentos_reais\*"
} | ForEach-Object {
    $contador++
    if ($contador % 1000 -eq 0) { Write-Host "Verificados: $contador arquivos..." }

    $bytes = Get-Content $_.FullName -Encoding Byte -TotalCount 8 -ErrorAction SilentlyContinue
    if (-not $bytes -or $bytes.Length -lt 4) { return }
    $hex = ($bytes | ForEach-Object { $_.ToString("X2") }) -join ""

    # Office antigo (.doc/.xls/.ppt) - assinatura OLE Compound File
    if ($hex.StartsWith("D0CF11E0A1B11AE1")) {
        Copy-Item $_.FullName -Destination (Join-Path "$destino\office_antigo" "$($_.BaseName).doc_ou_xls_ou_ppt") -ErrorAction SilentlyContinue
        return
    }

    # Office moderno - abre o zip de verdade pra confirmar o conteudo interno
    if ($hex.StartsWith("504B0304")) {
        try {
            $zip = [System.IO.Compression.ZipFile]::OpenRead($_.FullName)
            $nomes = $zip.Entries.FullName
            if ($nomes -contains "word/document.xml") {
                Copy-Item $_.FullName -Destination (Join-Path "$destino\docx" "$($_.BaseName).docx") -ErrorAction SilentlyContinue
            } elseif ($nomes -contains "xl/workbook.xml") {
                Copy-Item $_.FullName -Destination (Join-Path "$destino\xlsx" "$($_.BaseName).xlsx") -ErrorAction SilentlyContinue
            } elseif ($nomes -contains "ppt/presentation.xml") {
                Copy-Item $_.FullName -Destination (Join-Path "$destino\pptx" "$($_.BaseName).pptx") -ErrorAction SilentlyContinue
            }
            $zip.Dispose()
        } catch { }
    }
}

Write-Host "CONCLUIDO! Confira a pasta: $destino"
```
