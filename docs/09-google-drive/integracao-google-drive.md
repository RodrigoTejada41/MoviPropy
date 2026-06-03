# Integracao Google Drive

## Status

Planejado.
Nao implementado.
Este documento define escopo tecnico, riscos e plano de implementacao.

## Objetivo

Integrar o painel administrativo ao Google Drive para armazenar e importar midias de clientes.
O backend deve controlar acesso, metadados, sincronizacao e links de download.
O player nao deve acessar o Google Drive diretamente.

## Arquitetura proposta

Componentes:
- Painel administrativo: conecta conta Google, seleciona pasta raiz, importa ou envia midias.
- Backend/API: executa OAuth, valida permissoes, gerencia tokens, consulta Drive e controla metadados.
- PostgreSQL: armazena vinculos entre cliente, midia, pasta e arquivo do Drive.
- Google Drive: armazena arquivos fisicos de imagem e video.
- Player: recebe manifesto do backend, baixa arquivo por link controlado, valida tamanho/hash e reproduz localmente.

Fluxo resumido:
1. Admin conecta conta Google no painel.
2. Backend executa OAuth 2.0 e armazena credenciais protegidas.
3. Admin escolhe pasta raiz do projeto no Drive.
4. Backend cria ou localiza pasta por cliente.
5. Admin importa ou envia midias.
6. Backend registra metadados no banco.
7. Admin vincula midias a playlists.
8. Player recebe manifesto com URL controlada pelo backend.
9. Player baixa para cache local.
10. Player valida tamanho e hash.
11. Player reproduz offline.

## Fluxo OAuth 2.0

1. Painel solicita conexao com Google Drive.
2. Backend gera URL de autorizacao.
3. Admin autoriza a aplicacao no Google.
4. Google redireciona para callback do backend.
5. Backend troca `code` por access token e refresh token.
6. Backend armazena tokens de forma protegida.
7. Backend valida acesso ao Drive antes de habilitar operacao.

Regras:
- Nunca enviar refresh token ao frontend.
- Nunca enviar credenciais Google ao player.
- Usar HTTPS em ambiente publicado.
- Registrar auditoria de conexao, desconexao e falhas.
- Permitir revogar integracao por cliente.

## Estrutura de pastas no Google Drive

Estrutura proposta:

```text
MoviProgy/
  clientes/
    {cliente_id}-{nome_cliente}/
      midias/
        imagens/
        videos/
      importados/
      lixeira-logica/
```

Regras:
- A pasta raiz deve ser selecionada no painel.
- Cada cliente deve ter pasta isolada.
- Arquivo de um cliente nao pode ser listado para outro cliente.
- Exclusao no sistema deve ser logica por padrao.
- Remocao fisica deve exigir permissao elevada e auditoria.

## Modelo de dados proposto

Extensao planejada para `midias`:
- origem_armazenamento: `local`, `google_drive`.
- google_drive_file_id.
- google_drive_folder_id.
- google_drive_mime_type.
- google_drive_web_view_link.
- tamanho.
- hash_arquivo.
- status: `pendente`, `processando`, `disponivel`, `erro`, `removido`.
- criado_em.
- atualizado_em.
- sincronizado_em.

Novas tabelas planejadas:

### google_drive_integracoes

Finalidade: armazenar configuracao da integracao por cliente ou tenant.

Campos principais:
- id.
- cliente_id.
- conta_google_email.
- root_folder_id.
- access_token_criptografado.
- refresh_token_criptografado.
- token_expira_em.
- status.
- criado_em.
- atualizado_em.

### google_drive_operacoes

Finalidade: auditar importacoes, uploads, sincronizacoes e erros.

Campos principais:
- id.
- cliente_id.
- midia_id.
- operacao.
- status.
- mensagem.
- criado_em.
- finalizado_em.

## Endpoints planejados

### POST /api/admin/google-drive/conectar

Finalidade: iniciar OAuth 2.0.
Retorno: URL de autorizacao.
Seguranca: admin autenticado e permissao de configurar storage.

### GET /api/admin/google-drive/callback

Finalidade: receber retorno OAuth e gravar credenciais.
Retorno: status da conexao.
Seguranca: validar `state` e tenant.

### GET /api/admin/google-drive/pastas

Finalidade: listar pastas disponiveis.
Parametros: `parent_folder_id` opcional.
Retorno: lista de pastas.

### POST /api/admin/google-drive/pasta-raiz

Finalidade: selecionar pasta raiz do cliente/tenant.
Parametros: `folder_id`.
Retorno: configuracao atualizada.

### POST /api/admin/google-drive/clientes/{cliente_id}/pasta

Finalidade: criar ou localizar pasta do cliente.
Retorno: `folder_id`.

### GET /api/admin/google-drive/clientes/{cliente_id}/arquivos

Finalidade: listar arquivos da pasta do cliente.
Retorno: arquivos com id, nome, mime type, tamanho e link de visualizacao.

### POST /api/admin/google-drive/importar

Finalidade: importar arquivo existente no Drive como midia do sistema.
Parametros: `cliente_id`, `file_id`, `tipo`.
Retorno: midia registrada.

### POST /api/admin/google-drive/upload

Finalidade: enviar nova midia para o Drive e registrar no banco.
Parametros: arquivo, cliente_id, tipo.
Retorno: midia criada.

### POST /api/admin/playlists/{playlist_id}/midias

Finalidade: vincular midia importada ou enviada a uma playlist.
Parametros: `midia_id`, `ordem`, `duracao_override`.
Retorno: playlist atualizada.

### GET /api/player/midias/{midia_id}/download

Finalidade: gerar link controlado de download para o player.
Retorno: redirect temporario ou stream controlado pelo backend.
Seguranca: token do dispositivo e validacao de permissao por cliente.

### POST /api/admin/google-drive/midias/{midia_id}/sincronizar

Finalidade: atualizar metadados da midia a partir do Drive.
Retorno: status da sincronizacao.

### GET /api/admin/google-drive/validar-acesso

Finalidade: validar se a credencial atual ainda acessa a pasta raiz.
Retorno: status, email da conta e pasta raiz.

## Fluxo do painel administrativo

1. Admin acessa configuracoes de storage.
2. Clica em conectar Google Drive.
3. Autoriza conta Google.
4. Seleciona pasta raiz.
5. Sistema cria estrutura padrao.
6. Admin entra no cliente.
7. Admin lista arquivos existentes ou faz upload.
8. Admin importa arquivo como midia.
9. Admin vincula midia a playlist.
10. Admin publica playlist.

Estados de UI:
- Nao conectado.
- Conectado sem pasta raiz.
- Conectado e pronto.
- Token expirado.
- Sem permissao na pasta.
- Erro de sincronizacao.

## Fluxo do player

1. Player consulta manifesto.
2. Backend retorna midias com tamanho, hash e URL controlada.
3. Player baixa cada arquivo para pasta temporaria local.
4. Player valida tamanho.
5. Player valida hash.
6. Player move arquivo para cache ativo.
7. Player ativa playlist somente apos validar todos os arquivos.
8. Player reproduz localmente.

Regras:
- Player nao faz streaming direto do Google Drive.
- Player nao recebe `google_drive_file_id` se isso expuser acesso indevido.
- Player nao recebe credenciais Google.
- Link de download deve ser temporario ou protegido pelo backend.
- Falha de download nao pode remover playlist local valida.

## Regras de seguranca

- OAuth 2.0 obrigatorio.
- HTTPS obrigatorio fora do ambiente local.
- Refresh token deve ser criptografado ou protegido por cofre de segredo.
- Access token nao deve ser persistido em texto puro.
- Acesso deve ser isolado por cliente.
- Logs nao podem conter tokens.
- Upload deve validar extensao, MIME type e tamanho.
- Arquivos devem ter hash calculado pelo backend.
- Toda operacao critica deve gerar auditoria.
- Rotas administrativas devem usar RBAC real antes de producao.

## Casos de erro

- Conta Google desconectada.
- Refresh token revogado.
- Pasta raiz removida.
- Pasta do cliente removida.
- Arquivo removido no Drive.
- Arquivo sem permissao de leitura.
- Quota do Drive excedida.
- Upload interrompido.
- MIME type invalido.
- Hash divergente.
- Tamanho divergente.
- Tentativa de acessar arquivo de outro cliente.
- Player offline durante publicacao.

## Checklist de testes

- Conectar conta Google com sucesso.
- Rejeitar callback OAuth com `state` invalido.
- Selecionar pasta raiz.
- Criar pasta de cliente.
- Listar arquivos por cliente.
- Bloquear listagem de outro cliente.
- Importar arquivo existente.
- Upload de imagem valido.
- Upload de video valido.
- Bloquear extensao invalida.
- Bloquear MIME type invalido.
- Calcular e persistir tamanho/hash.
- Vincular midia a playlist.
- Gerar manifesto sem expor credenciais Google.
- Gerar link temporario de download.
- Player baixar arquivo.
- Player validar hash e tamanho.
- Player manter playlist antiga se download falhar.
- Revogar integracao e bloquear novas operacoes.
- Registrar auditoria de erro.

## Plano de implementacao

### Fase 1 - Preparacao

- Aprovar escopo e limites da integracao.
- Definir se a integracao e global, por tenant ou por cliente.
- Criar credenciais OAuth no Google Cloud.
- Definir estrategia de protecao de tokens.

### Fase 2 - Banco

- Criar migration para campos Google Drive em `midias`.
- Criar tabela `google_drive_integracoes`.
- Criar tabela `google_drive_operacoes`.
- Adicionar indices por `cliente_id`, `google_drive_file_id` e `status`.

### Fase 3 - Backend

- Criar service Google Drive.
- Criar repository de integracao.
- Criar endpoints administrativos.
- Criar endpoint controlado de download para player.
- Adicionar auditoria e logs.

### Fase 4 - Painel

- Criar tela de conexao.
- Criar seletor de pasta raiz.
- Criar listagem de arquivos.
- Criar fluxo de importacao/upload.
- Criar vinculo de midia com playlist.

### Fase 5 - Player

- Ajustar manifesto para midias externas.
- Baixar via backend.
- Validar tamanho/hash.
- Manter cache local offline-first.

### Fase 6 - Testes e homologacao

- Executar testes unitarios.
- Executar testes de integracao com Drive.
- Executar testes offline do player.
- Executar testes de seguranca.
- Executar testes de performance com arquivos grandes.

## Correcoes obrigatorias antes de implementar

1. Criar RBAC real para rotas administrativas.
2. Definir protecao de tokens OAuth.
3. Definir estrategia de auditoria.
4. Definir limites de tamanho por tipo de midia.
5. Definir politica de exclusao fisica no Drive.

## Riscos

- Quota do Google Drive pode bloquear uploads/downloads.
- Permissoes manuais no Drive podem quebrar isolamento.
- Link direto do Drive pode expor arquivo indevidamente.
- Streaming direto do Drive prejudica operacao offline.
- Token OAuth mal protegido pode comprometer arquivos.
- Arquivo alterado fora do sistema pode invalidar hash.
