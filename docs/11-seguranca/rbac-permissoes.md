# RBAC e Matriz de Permissoes

## Objetivo

Definir o controle de acesso definitivo do painel e da API administrativa.

## Estado atual

- Login administrativo existe.
- Sessao admin usa Bearer token.
- `/api/admin/*` exige perfil `admin`.
- `ADMIN_API_TOKEN` e fallback local sem repository de auth.

## Limite atual

- Ainda nao existe permissao granular por cliente.
- Ainda nao existe perfil operacional.
- Ainda nao existe auditoria completa.

## Perfis planejados

### Super Admin

Escopo:
- Todos os clientes.
- Todas as configuracoes.
- Usuarios e permissoes.
- Deploy e integracoes.

### Admin Cliente

Escopo:
- Clientes vinculados ao usuario.
- Dispositivos, midias, playlists e relatorios do cliente.

### Operador

Escopo:
- Operacao de midias e playlists.
- Sem acesso a usuarios, permissoes ou configuracoes globais.

### Suporte

Escopo:
- Leitura de dispositivos, logs e sincronizacoes.
- Sem alteracao de campanhas.

### Visualizador

Escopo:
- Somente leitura.

## Permissoes

Formato:
- `recurso:acao`

Recursos:
- `clientes`
- `usuarios`
- `dispositivos`
- `midias`
- `playlists`
- `sincronizacoes`
- `logs`
- `storage`
- `google_drive`
- `configuracoes`

Acoes:
- `criar`
- `ler`
- `editar`
- `excluir`
- `publicar`
- `bloquear`
- `importar`
- `upload`
- `administrar`

## Matriz

| Recurso | Super Admin | Admin Cliente | Operador | Suporte | Visualizador |
|---|---|---|---|---|---|
| Clientes | CRUD | Ler vinculado | Nao | Ler vinculado | Ler vinculado |
| Usuarios | CRUD | Gerenciar cliente | Nao | Nao | Nao |
| Dispositivos | CRUD | CRUD vinculado | Ler | Ler | Ler |
| Midias | CRUD | CRUD vinculado | Criar/editar | Ler | Ler |
| Playlists | CRUD/publicar | CRUD/publicar vinculado | CRUD sem publicar | Ler | Ler |
| Sincronizacoes | Ler | Ler vinculado | Ler vinculado | Ler vinculado | Ler vinculado |
| Logs | Ler | Ler vinculado | Nao | Ler vinculado | Nao |
| Storage | Administrar | Ver status | Upload | Nao | Nao |
| Google Drive | Administrar | Configurar vinculado | Importar | Nao | Nao |
| Configuracoes | Administrar | Config cliente | Nao | Nao | Nao |

## Regras obrigatorias

- Toda rota administrativa deve autenticar usuario.
- Toda rota com `cliente_id` deve validar acesso ao cliente.
- Usuario inativo nao acessa.
- Sessao expirada nao acessa.
- Token global nao pode ser protecao principal de producao.
- Respostas nao devem retornar senha, hash de senha ou token.
- Logs nao devem gravar tokens.

## Modelo de dados planejado

### usuarios_clientes

Campos:
- usuario_id.
- cliente_id.
- ativo.
- criado_em.

### permissoes

Campos:
- id.
- usuario_id.
- cliente_id.
- recurso.
- acao.
- permitido.

### auditoria_acessos

Campos:
- id.
- usuario_id.
- cliente_id.
- recurso.
- acao.
- status.
- ip.
- user_agent.
- criado_em.

## Criterios de aceite

- Usuario sem permissao recebe 403.
- Usuario sem cliente vinculado nao enxerga dados do cliente.
- Super Admin enxerga todos os clientes.
- Admin Cliente nao altera configuracao global.
- Operador nao gerencia usuarios.
- Visualizador nao executa POST/PATCH/DELETE.

