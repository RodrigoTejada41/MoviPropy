# Manual do Administrador

## Objetivo

Orientar uso operacional do painel administrativo.

## Login

1. Acessar tela de login.
2. Informar email.
3. Informar senha.
4. Entrar.

Problemas:
- Credenciais invalidas: conferir email/senha.
- Sem permissao: solicitar acesso ao Super Admin.

## Clientes

Criar cliente:
1. Abrir Clientes.
2. Clicar em Novo.
3. Informar nome.
4. Salvar.

Boas praticas:
- Usar nome claro; o id e gerado automaticamente.
- Inativar cliente em vez de excluir.

## Dispositivos

Criar dispositivo:
1. Abrir Dispositivos.
2. Clicar em Novo.
3. Selecionar cliente.
4. Informar nome.
5. Salvar.
6. Copiar o codigo de ativacao.
7. Vincular playlist publicada no campo `Playlist atual`.

Ativacao:
- Informar o codigo no player.

## Midias

Criar midia:
1. Abrir Midias.
2. Selecionar cliente.
3. Fazer upload ou cadastrar metadados.
4. Conferir tipo, tamanho e hash.

Regra:
- Midia so aparece no player depois de vinculada a playlist.

## Playlists

Criar playlist:
1. Abrir Playlists.
2. Selecionar cliente.
3. Criar playlist.
4. Adicionar midias.
5. Ordenar midias.
6. Ativar playlist.
7. Vincular playlist ao dispositivo.

Loop:
- Uma playlist com um unico video roda o mesmo video em loop continuo.
- Uma playlist com varios videos reproduz em sequencia e retorna ao primeiro automaticamente.

## Monitoramento

Verificar:
- Dispositivos sem sincronizar.
- Falhas de download.
- Logs criticos.
- Storage cheio.

## Google Drive

Quando implementado:
1. Conectar conta.
2. Selecionar pasta raiz.
3. Criar pasta do cliente.
4. Importar arquivos.

## Incidentes

Tela sem conteudo:
1. Verificar se dispositivo tem playlist atual.
2. Verificar se playlist esta ativa.
3. Verificar se playlist tem midias.
4. Verificar se player baixou arquivos.
