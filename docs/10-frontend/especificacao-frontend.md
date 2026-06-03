# Especificacao do Frontend

## Objetivo

Definir as telas, fluxos, estados e criterios de aceite do painel administrativo.
Nenhuma implementacao frontend deve iniciar sem consultar este documento.

## Stack

Status: pendente de aprovacao.

Requisitos tecnicos:
- Aplicacao web responsiva.
- Consumo de API REST.
- Autenticacao por Bearer token.
- Controle de rotas por permissao.
- Estado global minimo.
- Componentes reutilizaveis.
- Tabelas com filtros, paginacao e estados vazios.

## Layout base

Estrutura:
- Login sem sidebar.
- Area autenticada com sidebar fixa.
- Header com usuario, cliente atual e logout.
- Conteudo principal com largura fluida.
- Feedback visual para loading, erro, vazio e sucesso.

Menu inicial:
- Dashboard.
- Clientes.
- Dispositivos.
- Midias.
- Playlists.
- Sincronizacoes.
- Logs.
- Google Drive.
- Usuarios e permissoes.
- Configuracoes.

## Telas

### Login

Objetivo:
- Autenticar usuario administrativo.

Campos:
- Email.
- Senha.

Acoes:
- Entrar.

API:
- `POST /api/auth/login`.

Estados:
- Carregando.
- Credenciais invalidas.
- Usuario sem permissao.
- API indisponivel.

Criterios de aceite:
- Nao permitir envio com campos vazios.
- Salvar token apenas em storage definido pelo projeto.
- Redirecionar para Dashboard apos login.
- Logout deve remover token local.

### Dashboard

Objetivo:
- Exibir visao operacional rapida.

Cards:
- Clientes ativos.
- Dispositivos cadastrados.
- Dispositivos bloqueados.
- Playlists ativas.
- Midias cadastradas.
- Falhas recentes.

Listas:
- Ultimos dispositivos sincronizados.
- Ultimos erros.
- Playlists publicadas recentemente.

Criterios de aceite:
- Nao exibir dados inventados.
- Mostrar estado vazio quando nao houver dados.
- Mostrar erro quando API falhar.

### Clientes

Objetivo:
- Gerenciar clientes.

Funcionalidades:
- Listar clientes.
- Criar cliente.
- Editar cliente.
- Ativar/inativar cliente.
- Abrir detalhes do cliente.

Campos:
- Id.
- Nome.
- Documento.
- Ativo.

API atual:
- `POST /api/admin/clientes`.
- `GET /api/admin/clientes/{cliente_id}`.

APIs pendentes:
- `GET /api/admin/clientes`.
- `PATCH /api/admin/clientes/{cliente_id}`.

Criterios de aceite:
- Validar nome obrigatorio.
- Documento opcional.
- Nao duplicar cliente com mesmo id.
- Exibir mensagens tecnicas de erro sem expor stack trace.

### Dispositivos

Objetivo:
- Gerenciar players instalados.

Funcionalidades:
- Listar dispositivos.
- Criar dispositivo.
- Ver codigo de ativacao.
- Vincular playlist atual.
- Bloquear/desbloquear.
- Ver status e ultima sincronizacao.

Campos:
- Id.
- Cliente.
- Nome.
- Codigo de ativacao.
- Bloqueado.
- Playlist atual.

API atual:
- `POST /api/admin/dispositivos`.
- `GET /api/admin/dispositivos/{dispositivo_id}`.

APIs pendentes:
- `GET /api/admin/dispositivos`.
- `PATCH /api/admin/dispositivos/{dispositivo_id}`.
- `POST /api/admin/dispositivos/{dispositivo_id}/bloquear`.
- `POST /api/admin/dispositivos/{dispositivo_id}/desbloquear`.

Criterios de aceite:
- Nao permitir dispositivo sem cliente.
- Exibir codigo de ativacao apos cadastro.
- Avisar se nao houver playlist vinculada.

### Midias

Objetivo:
- Gerenciar arquivos e metadados de midia.

Funcionalidades:
- Listar midias.
- Criar metadados.
- Upload fisico.
- Importar de Google Drive.
- Validar hash/tamanho.
- Inativar midia.

Campos:
- Id.
- Cliente.
- Nome.
- Tipo.
- Caminho.
- Tamanho.
- SHA-256.
- Duracao.
- Ativo.

API atual:
- `POST /api/admin/midias`.
- `GET /api/admin/midias/{midia_id}`.

APIs pendentes:
- `GET /api/admin/midias`.
- `POST /api/admin/midias/upload`.
- `PATCH /api/admin/midias/{midia_id}`.
- `POST /api/admin/midias/{midia_id}/inativar`.

Criterios de aceite:
- Validar tipo permitido.
- Validar tamanho maximo.
- Mostrar hash calculado.
- Nao permitir upload sem cliente.

### Playlists

Objetivo:
- Gerenciar playlists e publicacao para dispositivos.

Funcionalidades:
- Listar playlists.
- Criar playlist.
- Editar playlist.
- Ativar/inativar playlist.
- Abrir editor.
- Vincular midias.

API atual:
- `POST /api/admin/playlists`.
- `GET /api/admin/playlists/{playlist_id}`.
- `POST /api/admin/playlists/{playlist_id}/midias`.

APIs pendentes:
- `GET /api/admin/playlists`.
- `PATCH /api/admin/playlists/{playlist_id}`.
- `DELETE /api/admin/playlists/{playlist_id}/midias/{midia_id}`.
- `PATCH /api/admin/playlists/{playlist_id}/midias/{midia_id}`.

Criterios de aceite:
- Playlist pertence a um cliente.
- Midia de outro cliente nao pode ser vinculada.
- Alteracao relevante deve incrementar versao.

### Editor de Playlist

Objetivo:
- Montar a ordem de exibicao.

Areas:
- Midias disponiveis.
- Linha do tempo/lista ordenada.
- Propriedades do item.
- Pre-visualizacao simples.

Acoes:
- Adicionar midia.
- Remover midia.
- Reordenar.
- Alterar duracao.
- Salvar.
- Publicar.

Criterios de aceite:
- Ordem visual deve refletir `playlist_midias.ordem`.
- Nao salvar playlist vazia sem confirmacao.
- Nao publicar se houver midia invalida.

### Sincronizacoes

Objetivo:
- Monitorar sincronizacao dos players.

Dados:
- Dispositivo.
- Playlist.
- Status.
- Inicio.
- Fim.
- Mensagem.

APIs pendentes:
- `GET /api/admin/sincronizacoes`.
- `GET /api/admin/dispositivos/{id}/sincronizacoes`.

Criterios de aceite:
- Filtrar por cliente, dispositivo, status e periodo.
- Destacar falhas recentes.

### Logs

Objetivo:
- Auditar eventos do sistema.

Tipos:
- Admin.
- API.
- Player.
- Storage.
- Google Drive.

APIs pendentes:
- `GET /api/admin/logs`.

Criterios de aceite:
- Nao exibir segredos.
- Permitir filtro por origem, nivel e periodo.

### Google Drive

Objetivo:
- Gerenciar integracao de storage externo.

Funcionalidades:
- Conectar conta.
- Validar acesso.
- Selecionar pasta raiz.
- Criar pasta de cliente.
- Listar arquivos.
- Importar midia.
- Fazer upload.

Documento principal:
- `docs/09-google-drive/integracao-google-drive.md`.

Criterios de aceite:
- Nao expor token Google.
- Mostrar status de conexao.
- Bloquear operacao se pasta raiz estiver inacessivel.

### Usuarios e Permissoes

Objetivo:
- Gerenciar acesso administrativo.

Funcionalidades:
- Listar usuarios.
- Criar usuario.
- Alterar perfil.
- Vincular clientes.
- Definir permissoes.
- Inativar usuario.

APIs pendentes:
- `GET /api/admin/usuarios`.
- `POST /api/admin/usuarios`.
- `PATCH /api/admin/usuarios/{usuario_id}`.
- `POST /api/admin/usuarios/{usuario_id}/permissoes`.

Criterios de aceite:
- Senha nunca deve aparecer.
- Usuario inativo nao deve logar.
- Permissao deve respeitar cliente.

### Configuracoes

Objetivo:
- Definir parametros operacionais.

Secoes:
- Storage.
- Upload.
- Player.
- Sincronizacao.
- Segurança.
- Deploy.

Criterios de aceite:
- Alteracoes sensiveis exigem perfil admin.
- Registrar auditoria.

## Estados obrigatorios por tela

- Loading.
- Vazio.
- Erro de API.
- Sem permissao.
- Sucesso.
- Validacao de formulario.
- Confirmacao para acoes destrutivas.

## Regras de UX

- Nao usar tela vazia sem orientacao.
- Nao esconder erro tecnico importante.
- Nao expor stack trace.
- Formularios devem preservar dados em erro de validacao.
- Acoes destrutivas devem exigir confirmacao.
- Datas devem mostrar fuso local.

## Mapa de navegacao

```text
Login
  Dashboard
  Clientes
    Detalhe do Cliente
      Dispositivos
      Midias
      Playlists
  Dispositivos
    Detalhe do Dispositivo
  Midias
    Upload
    Importar Google Drive
  Playlists
    Editor de Playlist
  Sincronizacoes
  Logs
  Google Drive
  Usuarios e Permissoes
  Configuracoes
```

