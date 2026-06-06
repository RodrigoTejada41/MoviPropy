# Integracao Google Drive

Status: implementacao inicial.

Decisao atual:
- O MVP usa storage local em `MOVIPROGY_MEDIA_DIR` e download controlado pelo backend.
- A integracao Google Drive possui base inicial implementada para simulacao e preparacao de OAuth real.

## Status

Implementado parcialmente.
Este documento define escopo tecnico, riscos, limites atuais e plano de evolucao.

## Objetivo

Integrar o painel administrativo ao Google Drive para armazenar e importar midias de clientes.
O backend deve controlar acesso, metadados, sincronizacao e links de download.
O player nao deve acessar o Google Drive diretamente.

## Limite desta especificacao

- Nao alterar o MVP atual de storage local.
- A integracao inicial nao faz chamada real ao Google Drive sem credenciais configuradas.
- A simulacao local pode ser ativada com `MOVIPROGY_GOOGLE_OAUTH_SIMULATED=true`.
- Este documento define UX/UI, fluxo funcional, endpoints, regras de seguranca e especificacao tecnica.

## Implementacao atual

Backend:
- Migration `006_google_drive.sql`.
- Repository `PostgresGoogleDriveRepository`.
- Rotas em `/api/integrations/google-drive`.
- OAuth URL e callback.
- Criptografia de tokens com `MOVIPROGY_GOOGLE_TOKEN_KEY`.
- Persistencia de pasta raiz e pasta por cliente.
- Importacao de midia por arquivo selecionado, com metadados obtidos pelo backend na API Google Drive.
- Listagem de arquivos encontrados na pasta raiz e arquivos ja importados.

Frontend:
- Tela Google Drive / Armazenamento.
- Status de conexao.
- Acoes de conectar, desconectar e validar.
- Formularios de pasta raiz, pasta de cliente e importacao.

Limites:
- Lista arquivos reais do Google Drive quando a conta esta conectada e a pasta raiz foi salva.
- Busca metadados reais do arquivo no Drive durante importacao.
- O painel nao deve solicitar `folder_id`, `file_id`, links, MIME type, tamanho ou hash como campos manuais.
- Homologacao real exige credenciais Google Cloud.

## Configuracao OAuth local

Arquivo local:
- `.env` na raiz do projeto.
- Nao versionar `.env`.
- Usar `.env.example` como modelo.

Variaveis obrigatorias para OAuth real:
- `MOVIPROGY_GOOGLE_CLIENT_ID`.
- `MOVIPROGY_GOOGLE_CLIENT_SECRET`.
- `MOVIPROGY_GOOGLE_REDIRECT_URI`.
- `MOVIPROGY_GOOGLE_TOKEN_KEY`.

Redirect URI local:
- `http://127.0.0.1:8000/api/integrations/google-drive/callback`.

Script de configuracao:

```powershell
.\scripts\configure_google_oauth.ps1 -ClientId "CLIENT_ID" -ClientSecret "CLIENT_SECRET"
docker compose up --build -d
```

Simulacao local sem conta Google:

```powershell
.\scripts\configure_google_oauth.ps1 -Simulated
docker compose up --build -d
```

Regras:
- `MOVIPROGY_GOOGLE_TOKEN_KEY` deve ter 32 ou mais caracteres.
- Client secret real nunca deve ser salvo em arquivos versionados.
- Em producao, usar HTTPS no redirect URI.

## Tela Google Drive / Armazenamento

Local no painel:
- Menu: Google Drive.
- Titulo: Google Drive / Armazenamento.
- Objetivo: conectar, configurar e gerenciar o Google Drive como storage opcional de midias.

### Card de status da integracao

Campos exibidos:
- Status: `desconectado`, `conectando`, `conectado`, `erro`, `token_expirado`.
- Conta Google conectada.
- Email da conta.
- Data da conexao.
- Ultima validacao.
- Espaco usado, se a API Google retornar.
- Pasta raiz selecionada.

Acoes:
- Conectar Google Drive.
- Desconectar.
- Validar conexao.
- Trocar conta.

Regras de UI:
- Se estiver desconectado, exibir CTA principal de conexao.
- Se estiver conectado sem pasta raiz, bloquear importacao e solicitar selecao da pasta.
- Se houver erro de autorizacao, mostrar mensagem tecnica curta sem tokens.
- Se o token expirar, oferecer validacao ou reconexao.

### Fluxo visual de autenticacao OAuth

1. Admin acessa `Google Drive / Armazenamento`.
2. Clica em `Conectar Google Drive`.
3. Painel chama o backend para gerar URL OAuth.
4. Backend registra `state` temporario e retorna `authorization_url`.
5. Painel redireciona o admin para o Google.
6. Admin escolhe a conta Google.
7. Admin autoriza permissoes minimas necessarias.
8. Google retorna para o callback do backend.
9. Backend valida `state`, troca `code` por tokens e salva credenciais protegidas.
10. Backend redireciona o admin para a tela Google Drive.
11. Painel exibe status conectado ou erro.

### Selecao da pasta raiz

Apos conexao:
- Listar pastas disponiveis no Drive.
- Permitir selecionar uma pasta raiz existente.
- Permitir criar pasta raiz padrao `MoviProgy_Midias`.
- Salvar `root_folder_id` e `root_folder_name`.
- Validar acesso de leitura e escrita antes de liberar importacao.

### Estrutura por cliente

Estrutura sugerida:

```text
MoviProgy_Midias/
  Cliente_001/
    Videos/
    Imagens/
    Campanhas/
  Cliente_002/
    Videos/
    Imagens/
    Campanhas/
```

Funcionalidades:
- Criar pasta para cada cliente.
- Listar pastas de clientes.
- Vincular pasta a cliente.
- Validar se a pasta ainda existe.
- Mostrar status de acesso.

### Listagem de arquivos

Campos:
- Nome.
- Tipo.
- Tamanho.
- Data de modificacao.
- ID do arquivo Google Drive.
- Status de importacao.
- Cliente vinculado.

Acoes:
- Importar midia.
- Atualizar lista.
- Abrir no Google Drive.
- Validar acesso.
- Remover vinculo.

### Importacao de midia

Ao importar um arquivo do Google Drive, registrar:
- `cliente_id`.
- `nome`.
- `tipo`.
- `tamanho`.
- `google_drive_file_id`.
- `google_drive_folder_id`.
- `google_drive_mime_type`.
- `google_drive_web_view_link`.
- `origem_armazenamento = google_drive`.
- `status`.
- Data de importacao.

Regra:
- A midia importada deve aparecer na tela de Midias.
- A midia importada deve poder ser usada em playlists.
- O player continua baixando pelo backend, nunca diretamente pelo Google Drive.

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
- `origem_armazenamento`: `local`, `google_drive`.
- `google_drive_file_id`.
- `google_drive_folder_id`.
- `google_drive_mime_type`.
- `google_drive_web_view_link`.
- `tamanho`.
- `hash_arquivo`.
- `status`: `pendente`, `processando`, `disponivel`, `erro`, `removido`.
- `criado_em`.
- `atualizado_em`.
- `sincronizado_em`.

Novas tabelas planejadas:

### integrations

Finalidade: armazenar credenciais e estado da integracao.

Campos principais:
- `id`.
- `type`.
- `provider`.
- `connected_email`.
- `access_token_encrypted`.
- `refresh_token_encrypted`.
- `expires_at`.
- `status`.
- `created_at`.
- `updated_at`.

### google_drive_settings

Finalidade: armazenar configuracao operacional do Drive.

Campos principais:
- `id`.
- `integration_id`.
- `root_folder_id`.
- `root_folder_name`.
- `last_validation_at`.
- `status`.

### client_storage_folders

Finalidade: vincular clientes a pastas do provider.

Campos principais:
- `id`.
- `cliente_id`.
- `provider`.
- `folder_id`.
- `folder_name`.
- `status`.

### google_drive_integracoes

Status: nome alternativo legado do rascunho. A implementacao futura deve preferir `integrations` + `google_drive_settings`.

### google_drive_operacoes

Status: tabela de auditoria operacional especifica do provider.

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

Contrato futuro canonico:
- Namespace administrativo: `/api/integrations/google-drive`.
- As rotas antigas do rascunho em `/api/admin/google-drive` ficam substituidas por este namespace quando a integracao for implementada.

### POST /api/integrations/google-drive/connect

Finalidade: iniciar fluxo OAuth.
Resposta esperada: `authorization_url`.
Seguranca: sessao admin, RBAC e registro de `state`.

### GET /api/integrations/google-drive/callback

Finalidade: receber retorno do Google OAuth.
Parametros: `code`, `state`.
Resposta: sucesso, erro ou redirecionamento para o painel.
Seguranca: validar `state`, origem e usuario solicitante.

### GET /api/integrations/google-drive/status

Finalidade: consultar status da integracao.
Resposta: conectado, email, pasta raiz, ultima validacao e status operacional.

### POST /api/integrations/google-drive/disconnect

Finalidade: desconectar conta Google Drive.
Regra: revogar tokens quando possivel e registrar auditoria.

### GET /api/integrations/google-drive/folders

Finalidade: listar pastas do Drive.
Query: `parent_folder_id` opcional.

### POST /api/integrations/google-drive/root-folder

Finalidade: definir pasta raiz.
Payload: `folder_name`.
Regra: backend deve localizar ou criar a pasta no Drive, salvar o ID real, validar acesso e registrar operacao.

### POST /api/integrations/google-drive/client-folder

Finalidade: criar ou vincular pasta do cliente.
Payload: `cliente_id`.
Regra: backend define nome e ID da pasta automaticamente.

### GET /api/integrations/google-drive/files

Finalidade: listar arquivos de uma pasta.
Query: `cliente_id`, `folder_id`, `mime_type` opcional.

### POST /api/integrations/google-drive/import-media

Finalidade: importar arquivo do Drive para o cadastro de midias.
Payload: `cliente_id`, `file_id`, `tipo`.
Regra: `nome`, `tamanho`, MIME type, links e pasta sao preenchidos pelo backend usando metadados do Drive.

### POST /api/integrations/google-drive/upload-media

Finalidade: enviar arquivo para o Drive e cadastrar midia.
Payload multipart: `cliente_id`, `tipo`, `arquivo`.
Regra: backend valida conexao, usa pasta raiz salva, envia ao Drive, captura metadados retornados e registra operacao.

### POST /api/integrations/google-drive/validate-access

Finalidade: validar se tokens, pastas e arquivos continuam acessiveis.

### GET /api/player/media-download-url

Finalidade: fornecer ao player uma URL controlada para baixar midia.
Regra: nao expor credenciais Google nem `refresh_token`.

### Compatibilidade com endpoint atual de download

- O MVP ja possui `GET /api/player/midias/{midia_id}/download` para storage local.
- Na implementacao Google Drive, preferir manter esse endpoint como fachada unica do player.
- `GET /api/player/media-download-url` pode ser criado apenas se houver necessidade de contrato separado.

### Historico do rascunho anterior

### POST /api/admin/google-drive/conectar

Status: substituido por `POST /api/integrations/google-drive/connect`.
Finalidade original: iniciar OAuth 2.0.
Retorno: URL de autorizacao.
Seguranca: admin autenticado e permissao de configurar storage.

### GET /api/admin/google-drive/callback

Status: substituido por `GET /api/integrations/google-drive/callback`.
Finalidade original: receber retorno OAuth e gravar credenciais.
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
- Conectando.
- Conectado sem pasta raiz.
- Conectado e pronto.
- Erro de autorizacao.
- Token expirado.
- Pasta nao encontrada.
- Sem permissao na pasta.
- Arquivo removido do Drive.
- Sem arquivos na pasta.
- Importacao concluida.
- Falha na importacao.
- Validacao em andamento.
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

## Logs e auditoria

Registrar:
- Quem conectou Google Drive.
- Quando conectou.
- Qual conta foi conectada.
- Quem alterou a pasta raiz.
- Quem criou ou vinculou pasta de cliente.
- Quem importou arquivo.
- Qual arquivo foi importado.
- Qual cliente recebeu a midia.
- Erros de acesso ao Drive.
- Falhas de importacao.
- Desconexao da conta.

Regras:
- Nao registrar access token.
- Nao registrar refresh token.
- Nao registrar authorization code.
- Nao registrar links temporarios sensiveis.
- Registrar `user_id`, `cliente_id`, acao, status, IP e user-agent quando disponivel.

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
