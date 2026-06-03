# Modelo de dados inicial

## Engine definida

PostgreSQL para ambiente Docker local e alvo multiusuario.

Dados locais:
- `runtime/postgres/data`

Status:
- Banco sobe no Docker Compose.
- Migration inicial criada para sessoes de dispositivo.
- Migration core criada para clientes, dispositivos, midias, playlists e relacionamento playlist/midias.
- Migration de auth criada para usuarios e sessoes administrativas.

## device_sessions

Finalidade: persistir sessoes de dispositivo ativado.

Campos principais:
- token_hash
- device_id
- hardware_id
- player_version
- created_at
- updated_at

Regras:
- `token_hash` deve armazenar SHA-256 do token.
- Token original nao pode ser gravado.
- Tabela criada por `backend/moviprogy_api/migrations/001_initial.sql`.

## usuarios

Finalidade: armazenar contas de acesso.

Campos principais:
- id
- nome
- email
- senha_hash
- perfil
- ativo
- criado_em
- atualizado_em

Relacionamentos:
- Pode pertencer a um ou mais clientes.

Status:
- Implementado em `003_auth.sql`.

Regras:
- `senha_hash` deve armazenar hash PBKDF2-HMAC-SHA256 com salt.
- Senha original nao pode ser gravada.
- Perfil `admin` libera rotas `/api/admin/*` no RBAC minimo.

## admin_sessions

Finalidade: persistir sessoes administrativas.

Campos principais:
- token_hash
- user_id
- expires_at
- created_at

Status:
- Implementado em `003_auth.sql`.

Regras:
- `token_hash` deve armazenar SHA-256 do token de sessao.
- Token original nao pode ser gravado.
- Sessao expirada nao deve autenticar.

## clientes

Finalidade: representar empresas atendidas.

Campos principais:
- id
- nome
- documento
- ativo
- criado_em
- atualizado_em

Status:
- Implementado em `002_core_domain.sql`.

Repository:
- `save_midia`
- `get_midia`

## dispositivos

Finalidade: representar players instalados.

Campos principais:
- id
- cliente_id
- nome
- codigo_ativacao
- token_hash
- status
- bloqueado
- ultima_sincronizacao
- versao_player
- playlist_atual_id

Status:
- Implementado em `002_core_domain.sql`.

Repository:
- `save_playlist`
- `get_playlist`

## midias

Finalidade: armazenar metadados de imagens e videos.

Campos principais:
- id
- cliente_id
- nome
- tipo
- caminho
- tamanho
- hash
- duracao
- ativo
- criado_em

Status:
- Implementado em `002_core_domain.sql`.

Repository:
- `add_midia_to_playlist`
- `get_playlist_manifest_for_device`

Regra:
- O backend valida que midia e playlist pertencem ao mesmo cliente antes de criar o vinculo.
- O manifesto do player consulta a playlist atual do dispositivo e retorna midias ativas ordenadas por `ordem`.

Extensao planejada para Google Drive:
- origem_armazenamento
- google_drive_file_id
- google_drive_folder_id
- google_drive_mime_type
- google_drive_web_view_link
- hash_arquivo
- status
- atualizado_em
- sincronizado_em

Regra:
- Player nao deve depender de `google_drive_file_id` para reproduzir midia.
- Backend deve entregar manifesto com URL controlada e metadados de validacao.

## playlists

Finalidade: agrupar midias em ordem de exibicao.

Campos principais:
- id
- cliente_id
- nome
- versao
- ativa
- criado_em
- atualizado_em

Status:
- Implementado em `002_core_domain.sql`.

## playlist_midias

Finalidade: ordenar midias dentro da playlist.

Campos principais:
- id
- playlist_id
- midia_id
- ordem
- duracao_override

Status:
- Implementado em `002_core_domain.sql`.

## campanhas

Finalidade: controlar ativacao de playlists por periodo, cliente ou dispositivo.

Campos principais:
- id
- cliente_id
- playlist_id
- nome
- inicio_em
- fim_em
- ativa

## sincronizacoes

Finalidade: registrar tentativas e resultados de sincronizacao.

Campos principais:
- id
- dispositivo_id
- playlist_id
- status
- mensagem
- iniciado_em
- finalizado_em

## logs

Finalidade: registrar eventos administrativos, API e player.

Campos principais:
- id
- origem
- nivel
- evento
- dados
- criado_em

## permissoes

Finalidade: controlar acesso por usuario, cliente e acao.

Campos principais:
- id
- usuario_id
- cliente_id
- permissao

## configuracoes

Finalidade: armazenar parametros globais e por cliente.

Campos principais:
- id
- cliente_id
- chave
- valor

## google_drive_integracoes

Finalidade: armazenar configuracao OAuth e pasta raiz do Google Drive.

Campos principais:
- id
- cliente_id
- conta_google_email
- root_folder_id
- access_token_criptografado
- refresh_token_criptografado
- token_expira_em
- status
- criado_em
- atualizado_em

Status:
- Planejado.

## google_drive_operacoes

Finalidade: auditar uploads, importacoes, sincronizacoes e falhas.

Campos principais:
- id
- cliente_id
- midia_id
- operacao
- status
- mensagem
- criado_em
- finalizado_em

Status:
- Planejado.
