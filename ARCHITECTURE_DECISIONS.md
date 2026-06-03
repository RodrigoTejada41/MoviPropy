# ARCHITECTURE_DECISIONS.md

## Objetivo

Registrar decisoes arquiteturais do projeto.
Toda decisao deve ter identificador, contexto, decisao, motivo e consequencias.

## Template

### ADR-000 - Titulo

Status:

Data:

Contexto:

Decisao:

Motivo:

Consequencias:

---

## Decisoes

### ADR-001 - Sincronizacao baseada em manifesto

Status: Aprovada

Data: 2026-05-31

Contexto:
- O player precisa operar offline.
- O servidor precisa informar quais arquivos fazem parte da playlist ativa.
- Downloads podem falhar por queda de internet.

Decisao:
- Usar manifesto versionado para sincronizacao de playlists e midias.

Motivo:
- Reduz trafego.
- Permite comparar versao local com versao online.
- Permite validar arquivos por tamanho e hash.
- Permite manter ultima playlist funcional.

Consequencias:
- Playlists precisam de versionamento.
- Midias precisam ter hash e tamanho registrados.
- Player precisa manter manifesto local e backup da ultima versao valida.
- Ativacao de playlist deve depender de validacao completa dos arquivos.

---

### ADR-002 - Offline-first no player

Status: Aprovada

Data: 2026-05-31

Contexto:
- Dispositivos podem ficar sem internet.
- Tela vazia em cliente final e falha critica.

Decisao:
- Player deve priorizar reproducao local e sincronizar em segundo plano quando houver internet.

Motivo:
- Garante continuidade da exibicao.
- Reduz dependencia da conexao.

Consequencias:
- Player precisa de armazenamento local.
- Player precisa tratar conflito entre playlist local e remota.
- Testes offline sao obrigatorios.

---

### ADR-003 - Memoria permanente dentro do projeto

Status: Aprovada

Data: 2026-05-31

Contexto:
- O projeto nao pode depender de memoria da IA ou historico de conversa.
- Erros corrigidos nao devem ser repetidos.

Decisao:
- Manter `PROJECT_RESUME.md`, `LESSONS_LEARNED.md`, `KNOWLEDGE_BASE.md` e `ARCHITECTURE_DECISIONS.md` na raiz do projeto.

Motivo:
- Garante continuidade.
- Reduz regressao.
- Facilita entrada de novos agentes ou desenvolvedores.

Consequencias:
- Toda alteracao critica deve atualizar a memoria permanente.
- Pre-commit deve verificar conflito com decisoes e licoes registradas.

---

### ADR-004 - Backend em FastAPI

Status: Aprovada

Data: 2026-05-31

Contexto:
- O sistema precisa expor contratos REST para painel administrativo e player.
- A base inicial precisa ser simples, testavel e modular.

Decisao:
- Usar Python 3.12+ com FastAPI para o backend.

Motivo:
- Suporte nativo a OpenAPI.
- Boa produtividade para APIs.
- Testes diretos com pytest e `TestClient`.
- Estrutura modular com routers.

Consequencias:
- Projeto deve manter separacao entre rotas, regras de negocio e dados.
- Dependencias devem ser registradas em `pyproject.toml`.
- Toda rota publica deve ter teste minimo.

---

### ADR-005 - Contrato inicial do player antes do banco

Status: Aprovada provisoriamente

Data: 2026-05-31

Contexto:
- O banco ainda nao foi escolhido.
- O player precisa de contratos HTTP validaveis desde o inicio.
- A sincronizacao offline depende de ativacao e manifesto.

Decisao:
- Criar contratos iniciais do player com registro em memoria.

Motivo:
- Permite validar API e testes sem bloquear no banco.
- Mantem foco nos contratos criticos do player.
- Evita implementar persistencia antes da decisao arquitetural.

Consequencias:
- Nao e producao.
- Tokens sao perdidos ao reiniciar a API.
- Deve ser substituido por Repository persistente quando o banco for aprovado.

---

### ADR-006 - Container Docker para simulacao do backend

Status: Aprovada

Data: 2026-05-31

Contexto:
- O backend precisa rodar de forma reproduzivel para simulacoes.
- O banco ainda nao foi definido.

Decisao:
- Criar `Dockerfile` e `docker-compose.yml` somente para o backend.

Motivo:
- Permite executar API sem depender do ambiente Python local.
- Facilita simulacoes do player por HTTP.
- Mantem banco fora do container ate decisao arquitetural.

Consequencias:
- Container atual nao possui persistencia.
- Simulacoes usam dados demo em memoria.
- Compose devera ser expandido quando o banco for aprovado.

---

### ADR-007 - Bind mounts locais para runtime Docker

Status: Aprovada

Data: 2026-05-31

Contexto:
- O projeto deve evitar gravar dados de runtime no disco C.
- O workspace fica em `E:\Projetos\MoviProgy`.

Decisao:
- Usar bind mounts relativos ao projeto para dados, midias, temporarios e logs.
- Manter o container com filesystem interno somente leitura quando possivel.

Motivo:
- Facilita limpeza e auditoria.
- Mantem artefatos de simulacao junto do projeto.
- Reduz escrita acidental na camada interna do container.

Consequencias:
- Dados da aplicacao ficam em `runtime/` e `logs/`.
- Imagens e cache do Docker continuam no armazenamento global do Docker Desktop.
- Para mover imagens/cache para fora do C, e necessario alterar a configuracao global do Docker Desktop.

---

### ADR-008 - Persistencia JSON provisoria para simulacao

Status: Aprovada provisoriamente

Data: 2026-05-31

Contexto:
- O banco oficial ainda nao foi definido.
- A simulacao Docker precisa manter dados dentro da pasta do projeto.
- O contrato do player precisa sobreviver a recriacao do objeto de registro durante testes.

Decisao:
- Persistir sessoes de dispositivo em `device_registry.json` quando `MOVIPROGY_DATA_DIR` estiver configurado.
- Armazenar apenas hash SHA-256 do token.

Motivo:
- Mantem dados em `runtime/data` no projeto.
- Permite validar fluxo sem banco.
- Evita escrever dados de aplicacao no disco C.

Consequencias:
- Nao e adequado para producao.
- Nao resolve multiusuario nem concorrencia robusta.
- Arquivo local nao pode conter token em texto puro.
- Deve ser substituido por Repository com banco assim que o banco for aprovado.

Substituicao:
- Em ambiente Docker, sessoes de dispositivo agora usam PostgreSQL.
- JSON permanece apenas como fallback sem `DATABASE_URL`.

---

### ADR-009 - PostgreSQL como banco local Docker

Status: Aprovada

Data: 2026-05-31

Contexto:
- O sistema precisa ser multiusuario e multi-cliente.
- SQLite nao atende bem o alvo multiusuario.
- Docker deve manter dados dentro da pasta do projeto.

Decisao:
- Usar PostgreSQL no Docker Compose para o ambiente local.
- Persistir dados em `runtime/postgres/data`.
- Validar disponibilidade por `GET /health/ready`.

Motivo:
- PostgreSQL atende melhor isolamento, concorrencia e evolucao multi-tenant.
- Bind mount mantem dados do banco junto ao projeto.
- Readiness evita considerar API pronta quando banco estiver indisponivel.

Consequencias:
- Compose passa a subir backend e banco.
- Repository de sessoes de dispositivo usa PostgreSQL.
- Demais repositories ainda precisam ser criados.
- Senhas locais devem ficar em `.env`, nunca versionadas.

---

### ADR-010 - Repository PostgreSQL para sessoes de dispositivo

Status: Aprovada

Data: 2026-06-01

Contexto:
- O JSON local era apenas fallback de simulacao.
- Tokens nao podem ser persistidos em texto puro.
- O backend ja possui `DATABASE_URL` no Docker.

Decisao:
- Criar migration `001_initial.sql` com tabela `device_sessions`.
- Persistir sessoes no PostgreSQL quando `DATABASE_URL` estiver configurado.
- Continuar usando hash SHA-256 do token como chave.

Motivo:
- Remove dependencia do JSON no ambiente Docker.
- Mantem persistencia em banco multiusuario.
- Preserva regra de nao gravar token em texto puro.

Consequencias:
- API executa migrations no startup.
- Testes de integration com PostgreSQL dependem de `DATABASE_URL`.
- Manifestos demo ainda precisam migrar para banco.

---

### ADR-011 - Tabelas core do dominio em PostgreSQL

Status: Aprovada

Data: 2026-06-01

Contexto:
- O sistema precisa separar cliente, dispositivo, midia e playlist.
- A simulacao atual ainda usa manifestos demo em memoria.
- A proxima etapa exige dados reais para rotas administrativas.

Decisao:
- Criar migration `002_core_domain.sql`.
- Criar tabelas `clientes`, `dispositivos`, `midias`, `playlists` e `playlist_midias`.
- Criar `PostgresCoreRepository` para persistir entidades iniciais.

Motivo:
- Estabelece base multi-cliente.
- Permite evoluir o painel e o manifesto sem dados hardcoded.
- Mantem queries parametrizadas e repositories separados.

Consequencias:
- Ainda faltam rotas administrativas.
- Ainda faltam tabelas de usuarios/permissoes/campanhas/logs.
- Manifesto do player ainda precisa consultar playlists reais.

---

### ADR-012 - Rotas administrativas iniciais sem RBAC

Status: Aprovada provisoriamente

Data: 2026-06-01

Contexto:
- O painel administrativo ainda nao existe.
- A camada de autenticacao/RBAC ainda nao foi criada.
- O backend precisa de contratos basicos para validar fluxo de clientes e dispositivos.

Decisao:
- Criar rotas administrativas iniciais para clientes e dispositivos.
- Manter escopo restrito a ambiente local.
- Documentar explicitamente que autenticacao/RBAC ainda e pendente.

Motivo:
- Permite validar persistencia e contratos administrativos.
- Evita bloquear o backend inteiro ate a camada de auth estar pronta.

Consequencias:
- Essas rotas nao devem ser expostas em producao sem auth/RBAC.
- Proximo passo de seguranca deve proteger `/api/admin/*`.

Atualizacao:
- `/api/admin/*` agora exige `ADMIN_API_TOKEN`.
- Ainda falta RBAC por usuario/perfil.

---

### ADR-013 - Token admin minimo para rotas administrativas

Status: Substituida parcialmente por ADR-015

Data: 2026-06-01

Contexto:
- Rotas administrativas estavam abertas.
- O sistema ainda nao possui usuarios, login e RBAC.

Decisao:
- Proteger `/api/admin/*` com `Authorization: Bearer <ADMIN_API_TOKEN>`.
- Configurar `ADMIN_API_TOKEN` por variavel de ambiente.

Motivo:
- Reduz risco imediato de acesso anonimo.
- Mantem o backend testavel enquanto RBAC completo nao existe.

Consequencias:
- Nao substitui login, usuario, permissao e auditoria.
- Token deve ser trocado fora do codigo.
- Proximo passo de seguranca deve criar auth/RBAC real.

Atualizacao:
- `POST /api/auth/login` e sessoes administrativas foram criados.
- `ADMIN_API_TOKEN` permanece apenas como fallback legado em execucao sem banco/auth repository.

---

### ADR-014 - Google Drive como storage externo controlado pelo backend

Status: Planejada

Data: 2026-06-01

Contexto:
- O sistema precisa armazenar videos e imagens de clientes.
- Storage local pode virar gargalo operacional.
- O player precisa continuar offline-first.
- O cliente solicitou escopo tecnico para Google Drive sem gerar codigo neste momento.

Decisao:
- Documentar Google Drive como opcao planejada de storage externo.
- O backend sera o unico responsavel por OAuth, credenciais, metadados e links de download.
- O player nao acessara Google Drive diretamente.

Motivo:
- Mantem controle de seguranca no backend.
- Evita expor credenciais Google ao player.
- Preserva reproducao offline com cache local.
- Permite importar arquivos ja existentes no Drive.

Consequencias:
- Sera necessario criar tabelas de integracao e auditoria.
- `midias` precisara armazenar metadados do Drive.
- Rotas administrativas exigem RBAC real antes de producao.
- Links de download devem ser controlados pelo backend.
- Testes offline continuam obrigatorios.

---

### ADR-015 - Login administrativo e RBAC minimo

Status: Aprovada

Data: 2026-06-01

Contexto:
- Rotas administrativas nao podem depender somente de token fixo global.
- Integracao Google Drive exige admin autenticado e permissao antes de producao.
- O sistema ainda nao possui painel frontend nem modulo completo de permissoes.

Decisao:
- Criar `POST /api/auth/login`.
- Criar tabelas `usuarios` e `admin_sessions`.
- Proteger `/api/admin/*` por sessao Bearer de usuario com perfil `admin`.
- Manter `ADMIN_API_TOKEN` somente como fallback local sem repository de auth.

Motivo:
- Remove dependencia exclusiva de segredo global.
- Permite evoluir para permissoes por cliente/acao.
- Mantem compatibilidade com simulacoes locais sem banco.

Consequencias:
- Senhas devem ser armazenadas com hash forte e salt.
- Tokens de sessao devem ser armazenados apenas como hash.
- Ainda falta RBAC granular por cliente e permissao.
- Docs, testes e Compose devem refletir o fluxo de login.

---

### ADR-016 - Manifesto real do player via PostgreSQL

Status: Aprovada

Data: 2026-06-02

Contexto:
- O player ainda recebia manifesto demo em memoria.
- O banco ja possui dispositivos, playlists, midias e vinculos.
- O player precisa operar offline com manifesto baseado em dados reais.

Decisao:
- Ativar dispositivo real por `dispositivos.codigo_ativacao` quando `core_repository` existir.
- Gerar manifesto a partir de `dispositivos.playlist_atual_id`.
- Incluir no manifesto apenas playlists ativas e midias ativas.
- Manter manifesto demo apenas como fallback local sem dados reais.

Motivo:
- Remove dependencia do manifesto hardcoded no fluxo com banco.
- Usa a modelagem core ja existente.
- Mantem compatibilidade com simulacao local simples.

Consequencias:
- Dispositivo precisa ter `playlist_atual_id` para receber manifesto real.
- Playlist precisa estar ativa.
- Midias precisam estar vinculadas por `playlist_midias`.
- Download controlado foi definido posteriormente na ADR-018.

---

### ADR-017 - Baseline documental antes da proxima fase

Status: Aprovada

Data: 2026-06-03

Contexto:
- O backend ja possui base operacional.
- O frontend ainda nao existe.
- Faltavam documentos de telas, RBAC, storage, player, deploy, backup, observabilidade, homologacao e manuais.

Decisao:
- Fechar baseline documental antes de continuar backend e frontend.
- Usar a documentacao como fonte de verdade para proximas implementacoes.

Motivo:
- Reduz ambiguidade.
- Evita retrabalho.
- Permite executar backend e frontend por escopo validado.

Consequencias:
- Toda implementacao futura deve referenciar o documento correspondente.
- Mudancas de escopo devem atualizar a documentacao antes do codigo.
- Homologacao passa a usar checklist e matriz de testes documentados.

---

### ADR-018 - Download controlado de midias pelo backend

Status: Aprovada

Data: 2026-06-03

Contexto:
- O player recebe manifesto com arquivos.
- O player precisa baixar midias sem acessar storage diretamente.
- O storage local inicial usa `MOVIPROGY_MEDIA_DIR`.

Decisao:
- Criar `GET /api/player/midias/{midia_id}/download`.
- Validar token do dispositivo.
- Liberar somente midia ativa presente na playlist atual ativa do dispositivo.
- Resolver caminho do arquivo dentro do diretorio base de midias.

Motivo:
- Evita expor caminho interno ou credenciais de storage.
- Preserva isolamento por dispositivo/playlist.
- Prepara o backend para Google Drive e storage externo controlado.

Consequencias:
- Upload fisico local foi definido posteriormente na ADR-019.
- Midias existentes precisam ter `caminho` relativo ao diretorio de midias.
- Download nao deve aceitar caminho informado pelo player.

---

### ADR-019 - Upload fisico local de midias

Status: Aprovada

Data: 2026-06-03

Contexto:
- O cadastro de midias ja persistia metadados.
- O player ja possui download controlado por backend.
- Faltava entrada fisica dos arquivos no storage local.

Decisao:
- Criar `POST /api/admin/midias/upload`.
- Exigir sessao administrativa.
- Validar cliente, tipo, extensao, MIME type e tamanho.
- Calcular SHA-256 no backend.
- Salvar arquivo sob `MOVIPROGY_MEDIA_DIR`.
- Gerar caminho relativo no servidor.

Motivo:
- Fecha o fluxo minimo upload -> playlist -> download.
- Evita aceitar caminho fisico informado pelo usuario.
- Mantem o storage local isolado por cliente e midia.

Consequencias:
- Upload local inicial nao substitui storage externo futuro.
- Videos grandes ainda exigirao testes de performance e espaco em disco.
- RBAC granular por cliente continua pendente antes de producao.

---

### ADR-020 - Telemetria e confirmacao de sincronizacao do player

Status: Aprovada

Data: 2026-06-03

Contexto:
- O player precisa operar offline e sincronizar em segundo plano.
- O backend precisa receber status, logs e confirmacao de sincronizacao.
- Homologacao exige testes de sincronizacao e observabilidade do dispositivo.

Decisao:
- Criar `POST /api/player/status`.
- Criar `POST /api/player/logs`.
- Criar `POST /api/player/sincronizacao/confirmar`.
- Exigir token Bearer do dispositivo.
- Persistir eventos em tabelas PostgreSQL dedicadas.

Motivo:
- Permite monitorar dispositivos.
- Permite auditar falhas de download/sincronizacao.
- Prepara o painel administrativo para exibir saude e eventos do player.

Consequencias:
- Volume de logs pode crescer e exigira politica de retencao.
- Ainda faltam listagens administrativas para consulta desses eventos.
- Consulta de atualizacao foi definida posteriormente na ADR-021.

---

### ADR-021 - Consulta leve de atualizacao do player

Status: Aprovada

Data: 2026-06-03

Contexto:
- O player precisa saber se existe nova playlist sem baixar manifesto completo a cada ciclo.
- A playlist ativa ja possui campo `versao`.
- A sincronizacao deve reduzir trafego e preservar operacao offline.

Decisao:
- Criar `GET /api/player/atualizacao`.
- Exigir token Bearer do dispositivo.
- Receber `playlist_versao_atual`.
- Comparar com a versao da playlist atual ativa do dispositivo.

Motivo:
- Permite polling leve.
- Evita download desnecessario de manifesto.
- Mantem sincronizacao baseada em versionamento.

Consequencias:
- Player ainda precisa consultar manifesto quando houver atualizacao.
- Sem playlist ativa, API retorna erro controlado.
- Listagens administrativas continuam pendentes.
