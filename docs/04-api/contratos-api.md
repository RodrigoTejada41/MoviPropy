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
- Ainda nao possui refresh token.
- Ainda nao possui rate limit.
- Ainda nao possui permissoes granulares por cliente/acao.

## Clientes

### POST /api/admin/clientes

Finalidade: cadastrar cliente.
Quem usa: painel administrativo.
Parametros: id, nome, documento, ativo.
Resposta: cliente criado.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Limite: RBAC granular ainda pendente.

### GET /api/admin/clientes/{cliente_id}

Finalidade: obter cliente por id.
Quem usa: painel administrativo.
Resposta: cliente encontrado ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Limite: RBAC granular ainda pendente.

### GET /api/clientes

Finalidade: listar clientes permitidos.
Quem usa: painel web.
Parametros: filtros opcionais.
Resposta: lista paginada.
Seguranca: RBAC e isolamento por permissao.

## Dispositivos

### POST /api/admin/dispositivos

Finalidade: cadastrar dispositivo administrativo vinculado a cliente.
Quem usa: painel administrativo.
Parametros: id, cliente_id, nome, codigo_ativacao, bloqueado, playlist_atual_id.
Resposta: dispositivo criado.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Limite: RBAC granular ainda pendente.

### GET /api/admin/dispositivos/{dispositivo_id}

Finalidade: obter dispositivo por id.
Quem usa: painel administrativo.
Resposta: dispositivo encontrado ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Limite: RBAC granular ainda pendente.

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
- Fallback: codigo demo local `MOVI-DEMO-001`.

## Midias

### POST /api/admin/midias

Finalidade: cadastrar metadados de midia.
Quem usa: painel administrativo.
Parametros: id, cliente_id, nome, tipo, caminho, tamanho, sha256, duracao_segundos, ativo.
Resposta: midia criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Regra: `cliente_id` precisa existir.

### POST /api/admin/midias/upload

Finalidade: enviar arquivo fisico e registrar metadados da midia.
Quem usa: painel administrativo.
Parametros: cliente_id, tipo, duracao_segundos opcional, arquivo multipart.
Resposta: midia criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Regra: cliente precisa existir; extensao, MIME type e tamanho sao validados.
Storage: arquivo local sob `MOVIPROGY_MEDIA_DIR`.

### GET /api/admin/midias/{midia_id}

Finalidade: obter midia por id.
Quem usa: painel administrativo.
Resposta: midia encontrada ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.

## Playlists

### POST /api/admin/playlists

Finalidade: cadastrar playlist.
Quem usa: painel administrativo.
Parametros: id, cliente_id, nome, versao, ativa.
Resposta: playlist criada.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
Regra: `cliente_id` precisa existir.

### GET /api/admin/playlists/{playlist_id}

Finalidade: obter playlist por id.
Quem usa: painel administrativo.
Resposta: playlist encontrada ou 404.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.

### POST /api/admin/playlists/{playlist_id}/midias

Finalidade: vincular midia a playlist.
Quem usa: painel administrativo.
Parametros: midia_id, ordem, duracao_override.
Resposta: vinculo criado.
Seguranca atual: exige `Authorization: Bearer <access_token>` de usuario `admin`.
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

### POST /api/player/logs

Finalidade: enviar logs do player.
Quem usa: player.
Parametros: nivel, evento, dados, criado_em.
Resposta: confirmacao.
Seguranca: token do dispositivo.

### GET /api/player/atualizacao

Finalidade: verificar se existe playlist nova.
Quem usa: player.
Parametros: playlist_versao_atual.
Resposta: possui_atualizacao, nova_versao.
Seguranca: token do dispositivo.

### POST /api/player/sincronizacao/confirmar

Finalidade: confirmar sincronizacao concluida.
Quem usa: player.
Parametros: playlist_id, versao, arquivos_baixados, status.
Resposta: confirmacao.
Seguranca: token do dispositivo.

## Google Drive

Status: planejado. Sem implementacao atual.

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
