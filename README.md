# automacao-de-planilha
# Descrição do programa
## inicializacao.bat

| O programa inicia, e é devidamente instalado e configurado com o arquivo de inicialização: (**"inicializacao.bat"**)

| Após executar o arquivo de inicialização ele apenas verifica as dependências necessárias para o funcionamento do programa, se não tiver instalado, esta é a hora que o programa vai instalar tudo

    se necessário rodar o programa de inicialização mais de uma vez conforme solicitado pelo mesmo.

| Depois de instalado, ele verifica se a pasta onde o usuário final vai colocar os pacientes chamada: (**"atendimento-rodada"**), se não existir ele vai criar a pasta na área de trabalho

| Após ele move todos os "Pacientes" na pasta: (**"atendimento_rodada"**) para a pasta onde o programa nativamente vai procurar por eles

| E executar o arquivo principal onde reside toda a lógica da aplicação chamado: (**"juntando_boot_GUI.py"**).

## juntando_boot_GUI.py

| Este programa roda em cima de 5 informações cruciais fornecidas pelo usuário para o funcionamento adequado do sistema, são eles:

* **Link do excel da planilha onde os pacientes serão inseridos**
* **email de login do usuário**
* **senha do usuário (cifrada com "*" por segurança)**
* **número de celulas que o programa deve percorrer por linha**
* **pacientes (arquivo de texto onde estarão as informações)**

**Atenção**

    O programa não irá salvar suas informações de Login por uma questão de privacidade e conformidade
    porconta disso é necessário informar toda vez email e senha

| Após coletar as  devidas informações o programa passa diretamente para o navegador, sem salvar em bases de dados externas ou internas e sem enviar nada a lugar algum

| O programa vai procurar pelos pacientes na pasta em que ele está por padrão no momento em que foi executado (por isso recomendo colocar os pacientes na pasta correta: (**"atendimento_rodada"**), **antes de iniciar o programa**, o programa de inicialização vai coloca-los no lugar correto)

| Ele vai pegar todos os arquivos de texto (*.txt) que estiverem na pasta

| Após isto ele vai abrir o navegador direto no link informado pelo usuário

| informar login e senha

| e a planilha será aberta

| por padrão o programa pula 2 linhas antes de começar a escrever as informações do paciente, cada Linha do excel é trarada como um arquivo de texto ou Documento de texto(.txt)

| Recomenda-se que estes arquivos **não** sejam salvos com espaços e sim com um "_" (Underline) no lugar do espaço
______________________________________________________________
## Para iniciar e funcionar corretamnete!

1° passo  - **Salvar** pacientes na pasta **atendimento_rodada**

2° passo - **mover** arquivo **"inicializacao.bat"** para área de Trabalho

3° passo - **executar** arquivo de inicialização, se o arquivo pedir, feche e rode mais uma vvez para que funcione corretamente

4° passo - Para que funcione como foi desenvolvido recomendammos que coloque **email** e **senha** nos campos **corretos**

5° passo informar a quantidade **exata** de células a serem preenchidas
______________________________________________________________
# importante

| O programa em sua base **trata** cada linha da planilha como um arquivo de texto individual

| É necessário informar a quantidade exata de celulas a ser prenchida, o **padrão do sistema é 5** (ou seja, se não for informado a quantidade de celulas a ser percorrida ele vai escrever as informações até a quinta coluna da linha atual)

| O arquivo **atendimento_rodada** será gerado automaticamente após instalação dos recursos necessários para o funcionamento do sistema.

| Caso haja alguma celula que precise ficar em branco é necessário informar ao sistema no arquivo de texto através da tecla "Enter" criando espaços vazios (Como parágrafo vazio) no texto simples

Exemplo
    
    CNS:123456789
    nome do paciente de exemplo
    atendeu



    observações


| pacientes precisam ser informados um a um em arquivo de texto (paciente.txt) o nome do arquivo **não** é relevante para o sistema, porém ele procura por arquivos de texto na pasta onde está o script

| O programa já move automáticamente todos os arquivos da pasta **atendimento_rodada**, porém **ainda não exclui os arquivos da pasta original do arquivo de forma automática**, local da pasta do arquivo C:\Users\%userprofile%\Downloads\automacao-de-planilha-main\automacao-de-planilha-main\executavel

| para **excluir** pacientes antigos para que não sejam passados na planilha, basta entrar no explorador de arquivos ("ctrl"+"e")

| Entrar na pasta de Downloads (**Downloads**), após isto abrir a pasta (**automacao-de-planilha-main**), novamente na unica pasata com o mesmo nome(**automacao-de-planilha-main**), Agora é só abrir a pasta (**executavel**) e apagar os arquivos de texto 

^^^^

Será corrigido na proxima versão.

| Recomendo estritamente que salve os pcts na pasta da área de trabalho com o nome: (**atendimento_rodada**), e não diretamente na pasta do script para evitar falhas no funcionamento da aplicação

______________________________________________________________
### Apagar
url para teste: https://geosaudecombr-my.sharepoint.com/:x:/r/personal/rodrigo_santos_geosaude_com_br/_layouts/15/doc2.aspx?sourcedoc=%7B54C2BF26-827C-4994-BBB9-B1F7CBB2E1BF%7D&file=Book.xlsx&action=editNew&mobileredirect=true&wdOrigin=APPHOME-WEB.OTHER%2CAPPHOME-WEB.BANNER.NEWBLANK&wdPreviousSession=4800de4e-7cb3-456f-ac83-5bfd3741f2f5&wdPreviousSessionSrc=AppHomeWeb&ct=1784610076435

por enquanto é apenas um protótipo que le cada linha de um arquivo de texto e depois escreve um a um em uma planilha do Excel desde a primeira linha da primeira coluna até aonde for idicado pelo programador no caso são 5 linhas mas isto ainda vai se preparado para o usuario final.
<br>
    tratando_Login(email='rodrigo.santos@geosaude.com.br',senha='Fuj1tisul')

______________________________________________
### Apagar
#correção de erros de escrita
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
_______________________________________________
### Apagar
deixa a janela transparente com python

root.attributes('-alpha',0.5)

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
    
