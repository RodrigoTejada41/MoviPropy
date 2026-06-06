# Especificacao do Frontend

## Objetivo

Definir as telas, fluxos, estados e criterios de aceite do painel administrativo.
Nenhuma implementacao frontend deve iniciar sem consultar este documento.

## Stack

Status: aprovada para MVP.

Implementacao inicial:
- Vite.
- React.
- TypeScript.
- CSS proprio.
- `lucide-react` para icones.

Requisitos tecnicos:
- Aplicacao web responsiva.
- Consumo de API REST.
- Autenticacao por Bearer token.
- Controle de rotas por permissao.
- Estado global minimo.
- Componentes reutilizaveis.
- Tabelas com filtros, paginacao e estados vazios.

Local:
- Codigo em `frontend/`.
- Servidor dev em `http://127.0.0.1:5173`.
- Proxy local para API em `http://127.0.0.1:8000`.

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
- Usar layout visual dedicado com identidade MoviProgy, painel lateral e estados claros.

Campos:
- Email.
- Senha.

Acoes:
- Entrar.
- Mostrar/ocultar senha.
- Manter conectado.

Limites MVP:
- Recuperacao de senha permanece desabilitada ate existir contrato backend.
- Login social/SSO permanece desabilitado ate existir contrato backend.

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
- Usar layout analitico com cards, eventos e alertas baseados em dados reais da API.

Cards:
- Clientes ativos.
- Dispositivos cadastrados.
- Dispositivos bloqueados.
- Playlists ativas.
- Midias cadastradas.
- Alertas derivados de dados existentes.

Listas:
- Ultimos eventos administrativos quando `GET /api/admin/auditoria/acessos` retornar dados.
- Alertas de dispositivos bloqueados, dispositivos sem playlist, midias inativas e auditoria negada.

Criterios de aceite:
- Nao exibir dados inventados.
- Mostrar estado vazio quando nao houver dados.
- Mostrar erro quando API falhar.
- Mostrar `Nao informado` quando a API nao retornar data ou evento.

### Clientes

Objetivo:
- Gerenciar clientes.
- Exibir visao operacional com indicadores reais e vinculo de dispositivos.

Funcionalidades:
- Listar clientes.
- Criar cliente.
- Buscar localmente por id, nome ou documento.
- Filtrar localmente por status ativo/inativo.
- Exibir quantidade de dispositivos vinculados por cliente.
- Editar cliente.
- Ativar/inativar cliente.
- Abrir detalhes do cliente. Pendente de API.

Campos:
- Id.
- Nome.
- Documento.
- Ativo.
- Quantidade de dispositivos calculada por `GET /api/admin/dispositivos`.
- Sincronizacao: exibir `Nao informado` enquanto a API nao retornar ultimo sync.

API atual:
- `GET /api/admin/clientes`.
- `POST /api/admin/clientes`.
- `GET /api/admin/clientes/{cliente_id}`.
- `PATCH /api/admin/clientes/{cliente_id}`.

APIs pendentes:
- Campo de regiao do cliente.
- Campo de data de criacao do cliente.
- Campo de ultimo sync por cliente/dispositivo.

Criterios de aceite:
- Validar nome obrigatorio.
- Documento opcional.
- Nao duplicar cliente com mesmo id.
- Exibir mensagens tecnicas de erro sem expor stack trace.
- Nao inventar regiao, data de criacao ou ultimo sync.
- Desabilitar acoes sem endpoint backend.

### Dispositivos

Objetivo:
- Gerenciar players instalados.
- Exibir visao operacional de frota com indicadores, busca e tabela detalhada.

Funcionalidades:
- Listar dispositivos.
- Criar dispositivo.
- Buscar localmente por id, nome, cliente, codigo ou playlist.
- Exibir indicadores de total, ativos, bloqueados e sem playlist.
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
- `GET /api/admin/dispositivos`.
- `GET /api/admin/dispositivos/{dispositivo_id}`.
- `PATCH /api/admin/dispositivos/{dispositivo_id}`.

APIs pendentes:
- Campo de ultima comunicacao consolidado no dispositivo.

Criterios de aceite:
- Nao permitir dispositivo sem cliente.
- Exibir codigo de ativacao apos cadastro.
- Avisar se nao houver playlist vinculada.
- Nao inventar ultima comunicacao se a API nao retornar esse dado.
- Acoes sem contrato backend devem aparecer desabilitadas.

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
- `GET /api/admin/midias`.
- `GET /api/admin/midias/{midia_id}`.
- `POST /api/admin/midias/upload`.
- `PATCH /api/admin/midias/{midia_id}`.

APIs pendentes:
- Nenhuma para o fluxo atual de ativacao/inativacao.

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
- `GET /api/admin/playlists`.
- `GET /api/admin/playlists/{playlist_id}`.
- `PATCH /api/admin/playlists/{playlist_id}`.
- `POST /api/admin/playlists/{playlist_id}/midias`.
- `GET /api/admin/playlists/{playlist_id}/midias`.
- `DELETE /api/admin/playlists/{playlist_id}/midias/{midia_id}`.

APIs pendentes:
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

APIs atuais:
- `GET /api/admin/sincronizacoes`.

APIs pendentes:
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
- Tela: Google Drive / Armazenamento.
Status: implementacao inicial.

Funcionalidades:
- Conectar conta.
- Validar acesso.
- Selecionar pasta raiz.
- Criar pasta de cliente.
- Listar arquivos.
- Importar midia.
- Fazer upload.
- Exibir quota usada, disponivel e total quando a API retornar.
- Ocultar IDs, tokens, links internos, MIME type, tamanho e hash como campos de entrada manual.

Layout:
- Card de status da integracao.
- Fluxo de conexao OAuth 2.0.
- Seletor de pasta raiz.
- Gestao de pastas por cliente.
- Tabela de arquivos do Drive.
- Historico resumido de importacoes e erros.

Estados:
- Desconectado.
- Conectando.
- Conectado.
- Erro de autorizacao.
- Token expirado.
- Pasta nao encontrada.
- Permissao negada.
- Arquivo removido do Drive.
- Sem arquivos na pasta.
- Importacao concluida.
- Falha na importacao.
- Validacao em andamento.

APIs atuais:
- `POST /api/integrations/google-drive/connect`.
- `GET /api/integrations/google-drive/callback`.
- `GET /api/integrations/google-drive/status`.
- `POST /api/integrations/google-drive/disconnect`.
- `GET /api/integrations/google-drive/folders`.
- `POST /api/integrations/google-drive/root-folder`.
- `POST /api/integrations/google-drive/client-folder`.
- `GET /api/integrations/google-drive/files`.
- `POST /api/integrations/google-drive/import-media`.
- `POST /api/integrations/google-drive/validate-access`.

Implementacao atual:
- Tela consome os endpoints acima.
- Conexao real exige configuracao Google no backend.
- Pasta raiz e salva por criacao/localizacao automatica no backend.
- Importacao usa arquivo selecionado; metadados tecnicos sao preenchidos pelo backend via Google Drive.

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

APIs atuais:
- `GET /api/admin/usuarios`.
- `POST /api/admin/usuarios`.
- `PATCH /api/admin/usuarios/{usuario_id}`.
- `POST /api/admin/usuarios/{usuario_id}/permissoes`.
- `GET /api/admin/usuarios/{usuario_id}/permissoes`.
- `POST /api/admin/usuarios/{usuario_id}/clientes`.
- `GET /api/admin/usuarios/{usuario_id}/clientes`.

Implementacao atual:
- Cadastro e ativacao/inativacao de usuario.
- Consulta e criacao de vinculos com clientes.
- Consulta e concessao de permissoes por recurso, acao e cliente opcional.

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

Implementacao atual:
- Consulta somente leitura em `GET /api/admin/configuracoes`.
- Exibe provider de storage, limite efetivo de upload e modo offline-first.
- Nao exibe caminhos, tokens, senhas ou variaveis de ambiente.
- Alteracoes sensiveis permanecem por configuracao de ambiente.

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
