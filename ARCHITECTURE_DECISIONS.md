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

Status: Adiada para pos-MVP

Data: 2026-06-01

Contexto:
- O sistema precisa armazenar videos e imagens de clientes.
- Storage local pode virar gargalo operacional.
- O player precisa continuar offline-first.
- O cliente solicitou escopo tecnico para Google Drive sem gerar codigo neste momento.

Decisao:
- Documentar Google Drive como opcao pos-MVP de storage externo.
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

Atualizacao:
- Implementacao foi adiada formalmente para pos-MVP na ADR-031.

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
- Listagens administrativas de eventos foram definidas posteriormente na ADR-022.
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
- Listagens administrativas iniciais foram definidas posteriormente na ADR-022.

---

### ADR-022 - Listagens administrativas iniciais para painel

Status: Aprovada

Data: 2026-06-03

Contexto:
- O painel frontend precisa consultar colecoes de clientes, dispositivos, midias e playlists.
- Eventos do player ja sao persistidos em PostgreSQL.
- O backend possuia apenas criacao e consulta por ID.

Decisao:
- Criar `GET /api/admin/clientes`.
- Criar `GET /api/admin/dispositivos`.
- Criar `GET /api/admin/midias`.
- Criar `GET /api/admin/playlists`.
- Criar `GET /api/admin/dispositivos/{dispositivo_id}/eventos`.
- Exigir sessao administrativa em todas as rotas.

Motivo:
- Desbloqueia telas principais do painel.
- Permite consultar saude/eventos do player.
- Mantem as rotas dentro do namespace administrativo protegido.

Consequencias:
- Listagens possuem paginacao e filtros iniciais definidos na ADR-023.
- Isolamento granular por cliente ainda depende de RBAC por permissao.
- Performance deve ser revisada antes de producao com muitos registros.

---

### ADR-023 - Paginacao e filtros nas listagens administrativas

Status: Aprovada

Data: 2026-06-03

Contexto:
- O painel administrativo precisa consultar colecoes sem carregar todos os registros.
- Clientes, dispositivos, midias e playlists podem crescer por cliente.
- A ADR-022 identificou paginacao e filtros como lacuna de performance.

Decisao:
- Adicionar `limit` e `offset` nas listagens administrativas.
- Limitar `limit` entre 1 e 200.
- Adicionar filtros iniciais por status e cliente quando aplicavel.
- Manter resposta como lista simples nesta etapa.

Motivo:
- Reduz risco de consultas grandes.
- Mantem compatibilidade com as telas iniciais.
- Evita criar envelope de paginacao antes do frontend consumir a API.

Consequencias:
- Ainda falta retorno de `total` para paginacao completa no painel.
- RBAC granular por cliente/acao continua pendente.
- Indices devem ser revisitados quando houver carga real.

Atualizacao:
- O envelope paginado com `total` foi aprovado posteriormente na ADR-027.

---

### ADR-024 - RBAC granular inicial por cliente e acao

Status: Aprovada

Data: 2026-06-03

Contexto:
- O backend ja possui login administrativo e sessao Bearer.
- O perfil unico `admin` nao atende isolamento multi-cliente.
- Rotas administrativas manipulam clientes, dispositivos, midias, playlists e logs.

Decisao:
- Manter o perfil legado `admin` com acesso total para compatibilidade local.
- Criar `usuarios_clientes` para vincular usuario a cliente.
- Criar `permissoes` com `recurso`, `acao` e `cliente_id` opcional.
- Exigir permissao granular nas rotas administrativas.
- Bloquear usuario escopado sem `cliente_id` em listagens de dados por cliente.

Motivo:
- Reduz risco de vazamento entre clientes.
- Prepara perfis como `admin_cliente`, `operador`, `suporte` e `visualizador`.
- Mantem compatibilidade com o admin seed atual.

Consequencias:
- Auditoria de acessos foi definida posteriormente na ADR-025.
- Frontend de gestao de usuarios/permissoes ainda nao existe.
- Retorno de listagens para usuario escopado exige filtro por cliente.

---

### ADR-025 - Auditoria de acessos administrativos

Status: Aprovada

Data: 2026-06-04

Contexto:
- O RBAC granular controla acesso por usuario, cliente, recurso e acao.
- Permissoes negadas precisam ficar rastreaveis.
- Tokens e senhas nao podem ser gravados em logs ou auditoria.

Decisao:
- Criar tabela `auditoria_acessos`.
- Registrar `user_id`, `cliente_id`, `recurso`, `acao`, `status`, IP e user-agent.
- Registrar acessos permitidos e negados no fluxo central de permissao administrativa.
- Nao registrar token Bearer nem senha.

Motivo:
- Facilita investigacao de tentativa indevida de acesso.
- Ajuda homologacao de seguranca e rastreabilidade LGPD.
- Centraliza auditoria sem duplicar codigo em cada rota.

Consequencias:
- A auditoria aumenta volume de escrita no banco.
- Sera necessaria politica de retencao.
- Endpoint administrativo de consulta de auditoria foi criado posteriormente.

---

### ADR-026 - Backend 100% antes do frontend

Status: Aprovada

Data: 2026-06-04

Contexto:
- O backend ainda possui pendencias de seguranca, paginacao completa, gestao de usuarios e homologacao.
- O frontend depende de contratos estaveis.
- Iniciar interface antes de fechar contratos gera retrabalho.

Decisao:
- Priorizar fechamento do backend antes de iniciar frontend.
- Nao iniciar telas administrativas enquanto houver pendencias backend criticas.
- Manter `PROJECT_RESUME.md` como fonte da fila backend.

Motivo:
- Evita telas acopladas a contratos instaveis.
- Reduz retrabalho.
- Aumenta confianca para homologacao.

Consequencias:
- Frontend fica bloqueado ate fechamento backend.
- Mudancas de API devem ser resolvidas antes da interface.

---

### ADR-027 - Envelope paginado nas listagens administrativas

Status: Aprovada

Data: 2026-06-04

Contexto:
- O frontend precisa saber o total de registros para paginacao.
- Listagens administrativas ja tinham `limit`, `offset` e filtros.
- O contrato ainda retornava lista simples, insuficiente para paginacao completa.

Decisao:
- Listagens administrativas passam a retornar `items`, `limit`, `offset` e `total`.
- O `total` deve respeitar os mesmos filtros da listagem.
- Metodos de listagem dos repositories continuam retornando listas; contadores ficam em metodos dedicados.

Motivo:
- Estabiliza contrato antes do frontend.
- Evita carregar todos os registros apenas para calcular paginacao.
- Mantem baixo acoplamento entre rota e repository.

Consequencias:
- Ha quebra controlada do contrato antigo de lista simples.
- Frontend deve consumir `items` para dados e `total` para paginacao.
- Consultas de contagem precisam ser consideradas nos testes de performance.

---

### ADR-028 - Endpoints administrativos para usuarios e permissoes

Status: Aprovada

Data: 2026-06-04

Contexto:
- O RBAC granular ja possuia tabelas de usuarios, vinculos e permissoes.
- Faltava API administrativa para manter esses dados.
- O frontend nao deve iniciar com gestao de acesso dependente de manipulacao manual no banco.

Decisao:
- Criar endpoints em `/api/admin/usuarios`.
- Respostas de usuario nao retornam senha nem hash.
- Criacao e atualizacao de senha usam hash no backend.
- Vinculos com clientes e permissoes sao mantidos por endpoints dedicados.
- As rotas exigem permissoes `usuarios:criar`, `usuarios:ler`, `usuarios:editar` ou `usuarios:administrar`.

Motivo:
- Fecha a base minima de administracao de acesso antes do frontend.
- Evita manutencao manual de RBAC no banco.
- Mantem auditoria centralizada por `require_admin_permission`.

Consequencias:
- Frontend deve consumir os endpoints administrativos para tela de usuarios.
- Perfis escopados precisam de permissao explicita para administrar usuarios.
- Ainda falta refresh/logout de sessao administrativa.

---

### ADR-029 - Refresh e logout de sessoes administrativas

Status: Aprovada

Data: 2026-06-05

Contexto:
- Login administrativo ja emitia token Bearer persistido por hash.
- Faltava renovar sessao sem reutilizar token antigo.
- Faltava encerrar sessao no banco.

Decisao:
- Criar `POST /api/auth/refresh`.
- Criar `POST /api/auth/logout`.
- Refresh invalida o token antigo e cria nova sessao.
- Logout remove a sessao atual.

Motivo:
- Reduz risco de token reutilizado.
- Permite frontend controlar ciclo de sessao.
- Mantem token real fora do banco.

Consequencias:
- Cliente deve trocar o token local apos refresh.
- Token antigo deixa de autenticar imediatamente.

---

### ADR-030 - Retencao de auditoria administrativa

Status: Aprovada

Data: 2026-06-05

Contexto:
- Auditoria administrativa registra acessos permitidos e negados.
- Volume de auditoria cresce continuamente.
- Era necessario definir limpeza operacional.

Decisao:
- Criar `POST /api/admin/auditoria/retencao/executar`.
- Usar retencao padrao de 180 dias.
- Exigir permissao `auditoria:administrar`.

Motivo:
- Controla crescimento da tabela.
- Mantem rastreabilidade recente.
- Evita limpeza manual direta no banco.

Consequencias:
- Deploy deve agendar execucao periodica se necessario.
- Auditorias antigas podem ser removidas conforme politica.

---

### ADR-031 - Google Drive adiado para pos-MVP

Status: Aprovada

Data: 2026-06-05

Contexto:
- Storage local com upload e download controlado ja cobre o MVP backend.
- Integracao Google Drive exige OAuth, criptografia de refresh token, rotas e operacao externa.
- Incluir Google Drive agora aumentaria risco antes do frontend.

Decisao:
- Adiar implementacao Google Drive para pos-MVP.
- Manter documentacao tecnica existente como escopo futuro.
- MVP backend usa storage local em `MOVIPROGY_MEDIA_DIR`.

Motivo:
- Fecha backend com menor risco.
- Preserva arquitetura para storage externo futuro.
- Evita bloquear frontend por dependencia externa.

Consequencias:
- Nao existem endpoints reais Google Drive no MVP.
- Player continua baixando pelo backend, sem credenciais externas.
- Implementacao futura deve seguir `docs/09-google-drive/integracao-google-drive.md`.

Atualizacao:
- A implementacao inicial foi aprovada posteriormente na ADR-034.

---

### ADR-032 - Frontend MVP em Vite, React e TypeScript

Status: Aprovada

Data: 2026-06-05

Contexto:
- Backend MVP foi fechado.
- O painel administrativo precisa consumir contratos REST existentes.
- A interface precisa ser responsiva, simples e testavel.

Decisao:
- Criar frontend em `frontend/`.
- Usar Vite, React e TypeScript.
- Usar CSS proprio para reduzir dependencias.
- Usar `lucide-react` para icones.
- Consumir API por cliente HTTP centralizado.

Motivo:
- Stack leve para MVP.
- Build rapido.
- Boa compatibilidade com API REST.
- Permite evoluir para testes e componentes sem acoplar ao backend.

Consequencias:
- O frontend passa a ter `package.json` e `package-lock.json` proprios.
- Deploy futuro precisa publicar artefato estatico ou container separado.
- Telas que dependem de endpoints ausentes devem exibir placeholder explicito.

---

### ADR-033 - Namespace para integracoes externas

Status: Aprovada

Data: 2026-06-05

Contexto:
- A integracao Google Drive foi inicialmente adiada para pos-MVP.
- O rascunho inicial usava rotas em `/api/admin/google-drive`.
- O escopo funcional define a integracao como modulo externo de storage, nao apenas uma tela administrativa.

Decisao:
- Usar `/api/integrations/google-drive` como namespace canonico da integracao.
- Manter o player sem acesso direto ao Google Drive.
- Manter `GET /api/player/midias/{midia_id}/download` como fachada preferencial para download pelo player.
- Criar `GET /api/player/media-download-url` apenas se houver necessidade de contrato separado.

Motivo:
- Separa integracoes externas das rotas CRUD administrativas.
- Facilita adicionar novos providers de storage no futuro.
- Mantem o backend como unico ponto de controle de tokens e downloads.

Consequencias:
- Documentos de API e frontend devem referenciar `/api/integrations/google-drive`.
- Rotas antigas `/api/admin/google-drive` ficam apenas como historico de rascunho.
- Implementacao deve validar OAuth `state`, RBAC, auditoria e criptografia de tokens antes de producao.

Atualizacao:
- Namespace implementado na ADR-034.

---

### ADR-035 - Configuracoes operacionais somente leitura no MVP

Status: Aprovada

Data: 2026-06-06

Contexto:
- O painel precisa mostrar a configuracao efetiva da operacao.
- Edicao remota de storage, seguranca e deploy aumenta risco e exige contratos adicionais.

Decisao:
- Criar `GET /api/admin/configuracoes`.
- Retornar somente provider de storage, limite efetivo de upload e modo offline-first.
- Manter alteracoes sensiveis em configuracao de ambiente.
- Nao retornar caminhos, tokens, senhas ou valores secretos.

Consequencias:
- A tela de Configuracoes deixa de ser placeholder.
- Mudancas sensiveis continuam controladas pelo ambiente e processo de deploy.

---

### ADR-036 - Frontend integrado por Nginx no Compose

Status: Aprovada

Data: 2026-06-06

Contexto:
- O Compose publicava apenas API e PostgreSQL.
- O fluxo documentado exige frontend e backend integrados.

Decisao:
- Construir o frontend em imagem Node e servir o artefato por Nginx.
- Publicar localmente na porta `8080`.
- Encaminhar `/api` e `/health` para `moviprogy-api`.
- Criar health check independente em `/health-ui`.
- Manter o container final somente leitura.

Consequencias:
- `docker compose up --build -d` entrega o painel completo.
- HTTPS continua responsabilidade do proxy de borda no ambiente publicado.

---

### ADR-037 - Log HTTP estruturado sem dados sensiveis

Status: Aprovada

Data: 2026-06-06

Contexto:
- Health checks existem, mas os logs HTTP nao tinham formato correlacionavel.
- Headers e corpos podem conter tokens, senhas e dados pessoais.

Decisao:
- Registrar cada requisicao em JSON com request ID, metodo, path, status e duracao.
- Retornar `X-Request-ID` ao cliente.
- Nao registrar headers, query, corpo ou credenciais.

Consequencias:
- Operacao pode correlacionar erro do cliente com logs do backend.
- Eventos de dominio continuam nas tabelas de auditoria e telemetria existentes.

---

### ADR-034 - Implementacao inicial Google Drive controlada pelo backend

Status: Aprovada

Data: 2026-06-05

Contexto:
- O cliente aprovou iniciar a implementacao Google Drive.
- A especificacao exige OAuth 2.0, tokens protegidos, backend como unico controlador e player sem acesso direto ao Drive.
- Ainda nao existem credenciais Google Cloud no ambiente local.

Decisao:
- Implementar base inicial em `/api/integrations/google-drive`.
- Criar tabelas `integrations`, `google_drive_settings`, `client_storage_folders`, `google_drive_oauth_states` e `google_drive_operations`.
- Adicionar campos Google Drive em `midias` sem quebrar o contrato publico atual de midias.
- Criptografar tokens com `MOVIPROGY_GOOGLE_TOKEN_KEY`.
- Permitir simulacao local do callback com `MOVIPROGY_GOOGLE_OAUTH_SIMULATED=true`.
- Criar tela Google Drive / Armazenamento no frontend.
- Manter `GET /api/player/midias/{midia_id}/download` como fachada preferencial do player.

Motivo:
- Entrega fluxo testavel sem expor tokens.
- Permite homologar UX e persistencia antes da conta Google real.
- Preserva storage local do MVP.
- Mantem o player desacoplado do Google Drive.

Consequencias:
- OAuth real depende de credenciais Google Cloud.
- Listagem real de pastas/arquivos do Drive ainda precisa ser implementada sobre a API Google.
- Importacao inicial exige metadados conhecidos do arquivo (`nome`, `tamanho`, `sha256`).
- Testes automatizados cobrem a simulacao e a regra de nao persistir token em texto puro.
