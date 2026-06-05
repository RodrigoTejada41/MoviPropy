# Contratos de API

## Saude

### GET /health

Finalidade: verificar se a API responde.
Quem usa: Docker healthcheck, monitoramento e desenvolvimento.
Resposta: status da API.

### GET /health/ready

Finalidade: verificar se a API esta pronta para operar com banco.
Quem usa: monitoramento, deploy e simulacao local.
Resposta: status da API e disponibilidade do banco.

## Autenticacao

### POST /api/auth/login

Finalidade: autenticar usuario do painel.
Quem usa: painel web.
Parametros: email, senha.
Resposta: access_token, token_type, usuario.
Seguranca: senha com hash, token salvo apenas como hash, HTTPS.

Implementacao atual:
- Rota: `POST /api/auth/login`
- Payload: `email`, `senha`
- Resposta: `access_token`, `token_type`, `usuario`
- Sessao: tabela `admin_sessions`
- Usuario: tabela `usuarios`

Limite:
- Ainda nao possui rate limit.
- Permissoes granulares por cliente/acao existem para rotas administrativas.

### POST /api/auth/refresh

Finalidade: renovar sessao administrativa.
Quem usa: painel web.
Autenticacao: `Authorization: Bearer <access_token>`.
Resposta: novo `access_token`, `token_type`, usuario.
Regra: token antigo e invalidado no banco.

### POST /api/auth/logout

Finalidade: encerrar sessao administrativa.
Quem usa: painel web.
Autenticacao: `Authorization: Bearer <access_token>`.
Resposta: status do logout.
Regra: token atual e removido de `admin_sessions`.

## Usuarios administrativos

### POST /api/admin/usuarios

Finalidade: criar usuario administrativo.
Quem usa: painel administrativo.
Parametros: id opcional, nome, email, senha, perfil, ativo.
Resposta: usuario publico sem senha e sem hash.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:criar`.

### GET /api/admin/usuarios

Finalidade: listar usuarios administrativos.
Quem usa: painel administrativo.
Query: `limit`, `offset`, `ativo`, `perfil`.
Resposta: envelope paginado com `items`, `limit`, `offset` e `total`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:ler`.

### GET /api/admin/usuarios/{user_id}

Finalidade: obter usuario administrativo por ID.
Quem usa: painel administrativo.
Resposta: usuario publico sem senha e sem hash.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:ler`.

### PATCH /api/admin/usuarios/{user_id}

Finalidade: atualizar nome, email, senha, perfil ou status do usuario.
Quem usa: painel administrativo.
Resposta: usuario publico sem senha e sem hash.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:editar`.

### POST /api/admin/usuarios/{user_id}/clientes

Finalidade: vincular usuario a cliente.
Quem usa: painel administrativo.
Parametros: cliente_id, ativo.
Resposta: vinculo criado ou atualizado.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:administrar`.

### GET /api/admin/usuarios/{user_id}/clientes

Finalidade: listar clientes vinculados ao usuario.
Quem usa: painel administrativo.
Resposta: lista de vinculos.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:ler`.

### POST /api/admin/usuarios/{user_id}/permissoes

Finalidade: conceder permissao granular ao usuario.
Quem usa: painel administrativo.
Parametros: recurso, acao, cliente_id opcional, permitido.
Resposta: permissao criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:administrar`.

### GET /api/admin/usuarios/{user_id}/permissoes

Finalidade: listar permissoes do usuario.
Quem usa: painel administrativo.
Resposta: lista de permissoes.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `usuarios:ler`.

## Clientes

### POST /api/admin/clientes

Finalidade: cadastrar cliente.
Quem usa: painel administrativo.
Parametros: id, nome, documento, ativo.
Resposta: cliente criado.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Limite: frontend de gestao ainda pendente.

### GET /api/admin/clientes/{cliente_id}

Finalidade: obter cliente por id.
Quem usa: painel administrativo.
Resposta: cliente encontrado ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Limite: frontend de gestao ainda pendente.

### GET /api/admin/clientes

Finalidade: listar clientes.
Quem usa: painel administrativo.
Query: `limit`, `offset`, `ativo`.
Resposta: envelope paginado com `items`, `limit`, `offset` e `total`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.

## Dispositivos

### POST /api/admin/dispositivos

Finalidade: cadastrar dispositivo administrativo vinculado a cliente.
Quem usa: painel administrativo.
Parametros: id, cliente_id, nome, codigo_ativacao, bloqueado, playlist_atual_id.
Resposta: dispositivo criado.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Limite: frontend de gestao ainda pendente.

### GET /api/admin/dispositivos/{dispositivo_id}

Finalidade: obter dispositivo por id.
Quem usa: painel administrativo.
Resposta: dispositivo encontrado ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Limite: frontend de gestao ainda pendente.

### GET /api/admin/dispositivos

Finalidade: listar dispositivos.
Quem usa: painel administrativo.
Query: `limit`, `offset`, `cliente_id`, `bloqueado`.
Resposta: envelope paginado com `items`, `limit`, `offset` e `total`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.

### GET /api/admin/dispositivos/{dispositivo_id}/eventos

Finalidade: consultar status, logs e confirmacoes de sincronizacao do dispositivo.
Quem usa: painel administrativo.
Resposta: status, logs e sync.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Limite: filtro por periodo e paginacao de eventos ainda pendentes.

## Auditoria

### GET /api/admin/auditoria/acessos

Finalidade: consultar auditoria de acessos administrativos.
Quem usa: painel administrativo.
Query: `limit`, `offset`, `user_id`, `cliente_id`, `recurso`, `acao`, `status`.
Resposta: envelope paginado com `items`, `limit`, `offset` e `total`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `auditoria:ler`.
Regra: usuario escopado precisa informar `cliente_id`.

### POST /api/admin/auditoria/retencao/executar

Finalidade: aplicar politica de retencao da auditoria.
Quem usa: administracao operacional.
Query: `dias`, default 180.
Resposta: `retention_days`, `deleted_count`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC `auditoria:administrar`.

### POST /api/dispositivos

Finalidade: cadastrar dispositivo e gerar codigo de ativacao.
Quem usa: painel web.
Parametros: cliente_id, nome.
Resposta: dispositivo, codigo_ativacao.
Seguranca: permissao de administracao do cliente.

### POST /api/player/ativar

Finalidade: ativar player com codigo.
Quem usa: player.
Parametros: codigo_ativacao, identificador_hardware, versao_player.
Resposta: token_dispositivo, configuracoes iniciais.
Seguranca: codigo unico, expirable e uso unico.

Implementacao atual:
- Rota: `POST /api/player/ativar`
- Payload: `activation_code`, `hardware_id`, `player_version`
- Resposta: `device_id`, `token`, `playlist_version`
- Persistencia: PostgreSQL quando `DATABASE_URL` existe.
- Fluxo real: consulta `dispositivos.codigo_ativacao`.
- Fallback: codigo demo local `MOVI-DEMO-001` apenas sem repository/banco.

## Midias

### POST /api/admin/midias

Finalidade: cadastrar metadados de midia.
Quem usa: painel administrativo.
Parametros: id, cliente_id, nome, tipo, caminho, tamanho, sha256, duracao_segundos, ativo.
Resposta: midia criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Regra: `cliente_id` precisa existir.

### POST /api/admin/midias/upload

Finalidade: enviar arquivo fisico e registrar metadados da midia.
Quem usa: painel administrativo.
Parametros: cliente_id, tipo, duracao_segundos opcional, arquivo multipart.
Resposta: midia criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Regra: cliente precisa existir; extensao, MIME type e tamanho sao validados.
Storage: arquivo local sob `MOVIPROGY_MEDIA_DIR`.

### GET /api/admin/midias/{midia_id}

Finalidade: obter midia por id.
Quem usa: painel administrativo.
Resposta: midia encontrada ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.

### GET /api/admin/midias

Finalidade: listar midias.
Quem usa: painel administrativo.
Query: `limit`, `offset`, `cliente_id`, `ativo`.
Resposta: envelope paginado com `items`, `limit`, `offset` e `total`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.

## Playlists

### POST /api/admin/playlists

Finalidade: cadastrar playlist.
Quem usa: painel administrativo.
Parametros: id, cliente_id, nome, versao, ativa.
Resposta: playlist criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Regra: `cliente_id` precisa existir.

### GET /api/admin/playlists/{playlist_id}

Finalidade: obter playlist por id.
Quem usa: painel administrativo.
Resposta: playlist encontrada ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.

### GET /api/admin/playlists

Finalidade: listar playlists.
Quem usa: painel administrativo.
Query: `limit`, `offset`, `cliente_id`, `ativa`.
Resposta: envelope paginado com `items`, `limit`, `offset` e `total`.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.

### POST /api/admin/playlists/{playlist_id}/midias

Finalidade: vincular midia a playlist.
Quem usa: painel administrativo.
Parametros: midia_id, ordem, duracao_override.
Resposta: vinculo criado.
Seguranca atual: exige `Authorization: Bearer <access_token>` e permissao RBAC.
Regra: midia e playlist devem pertencer ao mesmo cliente.

### GET /api/player/playlist

Finalidade: obter playlist ativa e manifesto de midias.
Quem usa: player.
Parametros: versao_local.
Resposta: playlist, versao, midias, hashes, urls.
Seguranca: token unico do dispositivo.

Implementacao atual:
- Rota: `GET /api/player/playlist`
- Autenticacao: `Authorization: Bearer <token>`
- Resposta: `playlist_id`, `version`, `files`
- Fluxo real: consulta `dispositivos.playlist_atual_id`, playlist ativa e midias vinculadas.
- Fallback: manifesto demo local.

Regra:
- Dispositivo bloqueado nao ativa pelo fluxo real.
- Apenas midias ativas entram no manifesto.
- Arquivos sao ordenados por `playlist_midias.ordem`.

### POST /api/player/status

Finalidade: informar status do dispositivo.
Quem usa: player.
Parametros: status, playlist_atual, versao_player, espaco_livre.
Resposta: confirmacao.
Seguranca: token do dispositivo.

Implementacao atual:
- Rota: `POST /api/player/status`
- Autenticacao: `Authorization: Bearer <token>`
- Resposta: `202 {"status": "registrado"}`
- Persistencia: tabela `player_status_events`

### POST /api/player/logs

Finalidade: enviar logs do player.
Quem usa: player.
Parametros: nivel, evento, dados, criado_em.
Resposta: confirmacao.
Seguranca: token do dispositivo.

Implementacao atual:
- Rota: `POST /api/player/logs`
- Autenticacao: `Authorization: Bearer <token>`
- Resposta: `202 {"status": "registrado"}`
- Persistencia: tabela `player_log_events`

### GET /api/player/atualizacao

Finalidade: verificar se existe playlist nova.
Quem usa: player.
Parametros: playlist_versao_atual.
Resposta: possui_atualizacao, nova_versao.
Seguranca: token do dispositivo.

Implementacao atual:
- Rota: `GET /api/player/atualizacao`
- Autenticacao: `Authorization: Bearer <token>`
- Query: `playlist_versao_atual`
- Compara com `playlists.versao` da playlist atual ativa do dispositivo.
- Resposta: `possui_atualizacao`, `nova_versao`

### POST /api/player/sincronizacao/confirmar

Finalidade: confirmar sincronizacao concluida.
Quem usa: player.
Parametros: playlist_id, versao, arquivos_baixados, status.
Resposta: confirmacao.
Seguranca: token do dispositivo.

Implementacao atual:
- Rota: `POST /api/player/sincronizacao/confirmar`
- Autenticacao: `Authorization: Bearer <token>`
- Resposta: `202 {"status": "registrado"}`
- Persistencia: tabela `player_sync_confirmations`

## Google Drive

Status: adiado para pos-MVP por decisao arquitetural. Sem implementacao atual.

### POST /api/admin/google-drive/conectar

Finalidade: iniciar OAuth 2.0 com Google Drive.
Quem usa: painel administrativo.
Resposta: URL de autorizacao.
Seguranca: admin autenticado e RBAC.

### GET /api/admin/google-drive/callback

Finalidade: receber retorno OAuth e registrar credenciais protegidas.
Quem usa: Google OAuth.
Resposta: status da conexao.
Seguranca: validar `state` e tenant.

### GET /api/admin/google-drive/pastas

Finalidade: listar pastas do Drive.
Quem usa: painel administrativo.
Resposta: pastas disponiveis.
Seguranca: isolamento por cliente/tenant.

### POST /api/admin/google-drive/pasta-raiz

Finalidade: selecionar pasta raiz da integracao.
Quem usa: painel administrativo.
Resposta: configuracao atualizada.

### POST /api/admin/google-drive/clientes/{cliente_id}/pasta

Finalidade: criar ou localizar pasta do cliente.
Quem usa: painel administrativo.
Resposta: identificador da pasta.

### GET /api/admin/google-drive/clientes/{cliente_id}/arquivos

Finalidade: listar arquivos de um cliente.
Quem usa: painel administrativo.
Resposta: arquivos com metadados.

### POST /api/admin/google-drive/importar

Finalidade: importar arquivo existente do Drive como midia.
Quem usa: painel administrativo.
Resposta: midia registrada.

### POST /api/admin/google-drive/upload

Finalidade: enviar arquivo para o Drive e registrar midia.
Quem usa: painel administrativo.
Resposta: midia criada.

### POST /api/admin/google-drive/midias/{midia_id}/sincronizar

Finalidade: atualizar metadados da midia a partir do Drive.
Quem usa: painel administrativo ou job interno.
Resposta: status da sincronizacao.

### GET /api/admin/google-drive/validar-acesso

Finalidade: verificar se credencial e pasta raiz continuam acessiveis.
Quem usa: painel administrativo e monitoramento.
Resposta: status da integracao.

### GET /api/player/midias/{midia_id}/download

Finalidade: fornecer download controlado ao player.
Quem usa: player.
Resposta: redirect temporario ou stream controlado.
Seguranca: token do dispositivo.
Regra: nao expor credenciais Google ao player.

Implementacao atual:
- Rota: `GET /api/player/midias/{midia_id}/download`
- Autenticacao: `Authorization: Bearer <token>`
- Storage: arquivo local sob `MOVIPROGY_MEDIA_DIR`
- Retorno: stream de arquivo via backend

Regras:
- Midia precisa estar na playlist atual ativa do dispositivo.
- Midia precisa estar ativa.
- Caminho fisico e resolvido dentro do diretorio base.
- Nao aceita caminho por query string.
