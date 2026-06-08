# LESSONS_LEARNED.md

## Objetivo

Registrar erros, falhas, decisoes corretivas e regras permanentes para evitar regressao.
Este arquivo deve ser consultado antes de qualquer implementacao.

## Template obrigatorio

### ERR-000

Data:

Descricao do Problema:

Causa Raiz:

Solucao Aplicada:

Como Evitar no Futuro:

Arquivos Afetados:

Status:

---

## Licoes registradas

### ERR-024

Data: 2026-06-08

Descricao do Problema:
- Video unico reproduzia uma vez no player e parava ao terminar.

Causa Raiz:
- O fluxo dependia principalmente do atributo `loop` do navegador.
- Com playlist de 1 item, `currentIndex` nao muda e o React nao remonta o elemento de video.

Solucao Aplicada:
- No `onEnded`, quando a playlist tem zero ou um arquivo, voltar `currentTime` para `0` e chamar `play()`.
- Atualizar cache do service worker do player para entregar a nova versao do shell.

Como Evitar no Futuro:
- Todo ajuste de player deve testar playlist com um unico video e playlist com varios videos.
- Nao depender apenas de `loop` nativo quando o player precisa operar como kiosk continuo.
- Bump de cache do service worker deve acompanhar correcao visivel no player.

Arquivos Afetados:
- `player/src/App.tsx`
- `player/public/sw.js`

Status: Resolvido

---

### ERR-023

Data: 2026-06-07

Descricao do Problema:
- Player retornava `falha HTTP 502` ao ativar dispositivo.

Causa Raiz:
- Nginx do player havia resolvido `moviprogy-api` para um IP antigo.
- A API foi recriada e o IP interno Docker mudou.

Solucao Aplicada:
- Configurar Nginx do player e do painel com resolver Docker `127.0.0.11`.
- Usar upstream via variavel para reavaliar DNS durante execucao.

Como Evitar no Futuro:
- Proxies internos Docker nao devem depender de resolucao DNS estatica quando containers podem ser recriados.
- Rebuild/restart de API deve ser validado pelo player e pelo painel.

Arquivos Afetados:
- `player/nginx.conf`
- `frontend/nginx.conf`

Status: Resolvido

---

### ERR-022

Data: 2026-06-07

Descricao do Problema:
- Cadastro de cliente expunha ID e documento como campos manuais na tela principal.

Causa Raiz:
- Frontend reutilizava o modelo completo do banco como formulario operacional.

Solucao Aplicada:
- Criar payload de cadastro com nome obrigatorio e ID/documento opcionais.
- Gerar ID automaticamente no backend quando ausente.
- Remover campos manuais de ID e documento do cadastro simples.

Como Evitar no Futuro:
- Nao expor campos tecnicos ou administrativos no fluxo operacional simples.
- Backend deve ser fonte autoritativa para identificadores sequenciais.

Arquivos Afetados:
- `backend/moviprogy_api/domain/core.py`
- `backend/moviprogy_api/routes/admin.py`
- `frontend/src/pages/ListPages.tsx`

Status: Resolvido

---

### ERR-018

Data: 2026-06-06

Descricao do Problema:
- O backend passava localmente, mas falhava no GitHub Actions ao importar `TestClient`.

Causa Raiz:
- `httpx` existia no ambiente local, mas nao estava declarado no extra de dependencias de teste.

Solucao Aplicada:
- Adicionar `httpx` ao extra `dev`.
- Fazer CI e validacao PROD instalarem `.[dev]`.

Como Evitar no Futuro:
- Toda dependencia usada por testes deve estar declarada no `pyproject.toml`.
- Validar a suite em ambiente limpo pelo CI antes do merge.

Arquivos Afetados:
- `pyproject.toml`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-production.yml`

Status: Resolvido

---

### ERR-019

Data: 2026-06-06

Descricao do Problema:
- O Vitest tentou executar o arquivo E2E do Playwright durante `npm test`.

Causa Raiz:
- O diretorio `frontend/e2e` nao estava excluido da descoberta do Vitest.

Solucao Aplicada:
- Excluir `e2e/**` na configuracao do Vitest.
- Manter comando separado `npm run test:e2e`.
- Ignorar `test-results` e `playwright-report` no Git.

Como Evitar no Futuro:
- Separar testes unitarios e E2E por runner e diretorio.
- Validar no ambiente local a mesma sequencia executada pelo CI.

Status: Resolvido

---

### ERR-020

Data: 2026-06-06

Descricao do Problema:
- O CI Linux nao encontrou `scripts.load_smoke` e alertou sobre opcao desconhecida do pytest.

Causa Raiz:
- `pythonpath` incluia apenas `backend`.
- A configuracao referenciava `pytest-asyncio`, dependente presente apenas no ambiente local.

Solucao Aplicada:
- Incluir a raiz do repositorio e `backend` no `pythonpath`.
- Remover configuracao de plugin que nao faz parte das dependencias do projeto.

Como Evitar no Futuro:
- Executar testes com dependencias declaradas pelo projeto.
- Nao depender de plugins instalados globalmente.
- Validar imports em ambiente Linux pelo CI.

Status: Resolvido

---

### ERR-021

Data: 2026-06-07

Descricao do Problema:
- O formulario de novo dispositivo exigia digitacao manual de ID e codigo de ativacao.

Causa Raiz:
- O contrato inicial tratava `id` e `codigo_ativacao` como campos obrigatorios informados pelo operador.

Solucao Aplicada:
- Criado payload de cadastro com ID e codigo opcionais.
- Backend gera ID sequencial por nome.
- Backend gera codigo de ativacao unico.
- Frontend remove campos manuais e mostra apenas ID sugerido.

Como Evitar no Futuro:
- Campos tecnicos e codigos operacionais devem ser gerados pelo backend.
- Frontend pode sugerir valores, mas nao deve ser a fonte autoritativa.

Status: Resolvido

---

### ERR-017

Data: 2026-06-06

Descricao do Problema:
- Dispositivo marcado como bloqueado ainda conseguia ativar o player.

Causa Raiz:
- A rota validava o codigo de ativacao, mas nao verificava `dispositivo.bloqueado`.

Solucao Aplicada:
- Bloquear ativacao com HTTP 403.
- Adicionar teste de regressao.

Como Evitar no Futuro:
- Toda ativacao deve validar existencia, bloqueio e permissao antes de emitir token.
- Estados administrativos de seguranca precisam de teste no contrato publico.

Arquivos Afetados:
- `backend/moviprogy_api/routes/player.py`
- `tests/test_player_contracts.py`

Status: Resolvido

---

### ERR-016

Data: 2026-06-06

Descricao do Problema:
- A porta local `8090` retornava HTTP 501 antes de atingir o container do player.

Causa Raiz:
- O processo Wondershare NativePush mantinha listener local na porta `8090`.

Solucao Aplicada:
- Publicado `moviprogy-player` na porta `8091`.

Como Evitar no Futuro:
- Verificar `Get-NetTCPConnection` antes de reservar nova porta local.
- Nao encerrar processos do usuario quando uma porta alternativa estiver disponivel.

Arquivos Afetados:
- `docker-compose.yml`
- `README.md`
- `KNOWLEDGE_BASE.md`

Status: Resolvido

---

### ERR-015

Data: 2026-06-06

Descricao do Problema:
- Blob persistido diretamente no IndexedDB simulado nao preservou tamanho no teste.

Causa Raiz:
- Serializacao de Blob varia entre ambiente jsdom/fake-indexeddb e navegador real.

Solucao Aplicada:
- Persistir `ArrayBuffer` e MIME type.
- Reconstruir Blob ao carregar a midia.

Como Evitar no Futuro:
- Usar formato binario explicito em persistencia IndexedDB testada fora do navegador.
- Manter teste de promocao e leitura de midia.

Arquivos Afetados:
- `player/src/storage.ts`
- `player/src/storage.test.ts`

Status: Resolvido

---

### ERR-015

Data: 2026-06-05

Descricao do Problema:
- Tela Google Drive exigia campos tecnicos manuais e nao dava feedback claro ao salvar pasta raiz.
- Backend reutilizava ID local salvo no banco sem confirmar a existencia real da pasta no Google Drive.

Causa Raiz:
- Implementacao inicial usava simulacao local e metadados informados pelo painel.
- O fluxo nao validava o ID salvo contra a API real do Google Drive antes de reutilizar a pasta raiz.

Solucao Aplicada:
- Pasta raiz passou a ser localizada/criada automaticamente no Google Drive.
- Backend valida acesso, atualiza status, registra operacao e salva o ID real retornado pelo Drive.
- Frontend ocultou IDs, links, MIME, tamanho e hash manuais, exibindo apenas status, pasta, quota, pastas e arquivos.

Como Evitar no Futuro:
- Campos tecnicos de storage externo devem vir da API do provider, nao do usuario.
- IDs salvos para provider externo devem ser validados contra o provider antes de reutilizacao.
- Acoes administrativas devem exibir sucesso ou erro visivel.

Arquivos Afetados:
- `backend/moviprogy_api/routes/integrations.py`
- `backend/moviprogy_api/repositories/postgres_google_drive.py`
- `frontend/src/pages/ListPages.tsx`

Status: Resolvido

---

### ERR-006

Data: 2026-06-06

Descricao do Problema:
- `/health/ready` acessado pela porta do frontend retornava o HTML da SPA.

Causa Raiz:
- O Nginx encaminhava somente a rota exata `/health`.

Solucao Aplicada:
- Alterar o proxy para o prefixo `/health`.
- Criar smoke test estrito para frontend, API, banco, login e logout.

Como Evitar no Futuro:
- Validar health e readiness pela mesma entrada publica usada pelo painel.
- Smoke tests devem falhar quando um campo obrigatorio estiver ausente.

Status: Resolvido

---

### ERR-005

Data: 2026-06-06

Descricao do Problema:
- O build do frontend preenchia email e senha de desenvolvimento na tela de login.

Causa Raiz:
- Estados iniciais do formulario continham credenciais fixas para facilitar testes locais.

Solucao Aplicada:
- Iniciar email e senha vazios.
- Adicionar teste automatizado de regressao.

Como Evitar no Futuro:
- Nunca embutir senha, token ou segredo em bundle frontend.
- Dados de desenvolvimento devem ficar em documentacao local ou variaveis seguras.

Status: Resolvido

---

### ERR-004

Data: 2026-06-06

Descricao do Problema:
- Frontend recebeu `404` ao validar uma rota administrativa recem-criada.

Causa Raiz:
- O container da API ainda executava a imagem anterior ao codigo local.

Solucao Aplicada:
- Reconstruir o servico `moviprogy-api`.
- Validar `/health` e repetir o fluxo no navegador.

Como Evitar no Futuro:
- Apos alterar rotas do backend, executar `docker compose up -d --build moviprogy-api`.
- Nao considerar validacao do frontend concluida usando container desatualizado.

Status: Resolvido

---

### ERR-014

Data: 2026-06-04

Descricao do Problema:
- Teste de integracao PostgreSQL falhou ao verificar que entidade criada aparecia em listagem sem filtro.
- O banco local de testes ja possuia muitos registros e a entidade nova ficou fora da primeira pagina.

Causa Raiz:
- O teste assumia banco vazio.
- A listagem passou a ter `limit` padrao.

Solucao Aplicada:
- Ajustado teste para usar limite explicito amplo ao validar presenca de entidade criada.

Como Evitar no Futuro:
- Testes de integracao com banco reaproveitado nao devem assumir banco vazio.
- Testes de listagem paginada devem usar filtros unicos ou `limit` explicito adequado.
- Quando validar criacao, preferir consulta por ID ou filtro unico.

Arquivos Afetados:
- `tests/test_postgres_core_repository.py`

Status: Resolvido

---

### ERR-013

Data: 2026-06-03

Descricao do Problema:
- Rotas administrativas autenticavam usuario, mas diferenciavam apenas o perfil legado `admin`.
- Esse modelo nao validava permissao granular por cliente e acao.

Causa Raiz:
- A camada inicial de RBAC foi criada apenas para bloquear acesso anonimo.
- Ainda nao existiam tabelas de vinculo usuario/cliente e permissoes.

Solucao Aplicada:
- Criadas tabelas `usuarios_clientes` e `permissoes`.
- Criados checks por `recurso`, `acao` e `cliente_id`.
- Mantido perfil legado `admin` com acesso total para compatibilidade local.

Como Evitar no Futuro:
- Toda rota administrativa nova deve chamar validacao de permissao granular.
- Toda rota com `cliente_id` deve validar vinculo do usuario com o cliente.
- Perfis escopados nao devem listar dados multi-cliente sem filtro `cliente_id`.

Arquivos Afetados:
- `backend/moviprogy_api/security.py`
- `backend/moviprogy_api/routes/admin.py`
- `backend/moviprogy_api/repositories/postgres_auth.py`
- `backend/moviprogy_api/migrations/004_rbac.sql`
- `tests/test_admin_routes.py`
- `tests/test_postgres_auth_repository.py`

Status: Resolvido

---

### ERR-012

Data: 2026-06-03

Descricao do Problema:
- Em ambiente com PostgreSQL, o codigo demo `MOVI-DEMO-001` ativava dispositivo que nao existia na tabela `dispositivos`.
- Ao enviar status do player, a persistencia quebrava FK e retornava erro 500.

Causa Raiz:
- A rota de ativacao caia no fallback demo mesmo quando `core_repository` estava disponivel.
- O fallback demo nao representa um dispositivo persistido no banco.

Solucao Aplicada:
- Quando `core_repository` existe, ativacao aceita somente `codigo_ativacao` real do banco.
- O fallback demo fica restrito a execucao local sem repository.
- Adicionado teste de regressao para bloquear demo com repository.

Como Evitar no Futuro:
- Fallbacks demo nao devem ser misturados com fluxo persistido em banco.
- Fluxos que geram FK devem usar entidades persistidas.
- Validar endpoints novos no Docker com dados reais do banco.

Arquivos Afetados:
- `backend/moviprogy_api/routes/player.py`
- `tests/test_player_contracts.py`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-011

Data: 2026-06-03

Descricao do Problema:
- Upload fisico falhou no Docker com `Invalid cross-device link`.
- O erro ocorreu ao mover arquivo de `runtime/tmp` para `runtime/media`.

Causa Raiz:
- `runtime/tmp` e `runtime/media` sao bind mounts separados no container.
- `Path.replace` usa operacao atomica que nao funciona entre filesystems diferentes.

Solucao Aplicada:
- Trocar movimentacao final para `shutil.move`.
- Adicionar teste de regressao simulando `errno.EXDEV`.

Como Evitar no Futuro:
- Nao usar `Path.replace`/`os.replace` para mover arquivos entre pastas que podem estar em volumes diferentes.
- Fluxos com `MOVIPROGY_TMP_DIR` e `MOVIPROGY_MEDIA_DIR` devem aceitar mounts separados.
- Validar upload real dentro do Docker apos alterar storage.

Arquivos Afetados:
- `backend/moviprogy_api/routes/admin.py`
- `tests/test_admin_routes.py`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-010

Data: 2026-06-01

Descricao do Problema:
- Rotas administrativas dependiam de `ADMIN_API_TOKEN` como protecao principal.
- Esse modelo nao separava usuarios, perfis, sessoes ou permissoes.

Causa Raiz:
- A autenticacao inicial foi criada apenas para remover acesso anonimo rapido.
- Ainda nao existiam tabelas `usuarios` e `admin_sessions`.

Solucao Aplicada:
- Criado login administrativo em `POST /api/auth/login`.
- Criadas tabelas `usuarios` e `admin_sessions`.
- `/api/admin/*` passou a exigir sessao Bearer de usuario com perfil `admin`.
- `ADMIN_API_TOKEN` ficou apenas como fallback local sem repository de auth.

Como Evitar no Futuro:
- Toda rota administrativa nova deve usar dependencia de auth/RBAC.
- Token global nao deve ser usado como protecao principal em producao.
- Senhas devem usar hash forte com salt.
- Tokens de sessao devem ser persistidos apenas como hash.

Arquivos Afetados:
- `backend/moviprogy_api/domain/auth.py`
- `backend/moviprogy_api/repositories/postgres_auth.py`
- `backend/moviprogy_api/routes/auth.py`
- `backend/moviprogy_api/security.py`
- `backend/moviprogy_api/routes/admin.py`
- `backend/moviprogy_api/main.py`
- `backend/moviprogy_api/migrations/003_auth.sql`
- `tests/test_auth_routes.py`
- `tests/test_admin_routes.py`
- `tests/test_postgres_auth_repository.py`

Status: Resolvido

---

### ERR-001

Data: 2026-05-31

Descricao do Problema:
- O projeto iniciou sem arquivos locais de memoria permanente.
- Informacoes criticas estavam em briefing externo e historico de conversa.

Causa Raiz:
- Workspace estava vazio.
- Ainda nao existiam `README.md`, `PROJECT_RESUME.md`, `LESSONS_LEARNED.md`, `KNOWLEDGE_BASE.md` e `ARCHITECTURE_DECISIONS.md`.

Solucao Aplicada:
- Criados arquivos de memoria permanente.
- Atualizado `AGENTS.md` com leitura obrigatoria antes de qualquer alteracao.

Como Evitar no Futuro:
- Sempre consultar os arquivos de memoria permanente antes de implementar.
- Registrar todo conhecimento critico no workspace.
- Nao depender de historico de conversa.

Arquivos Afetados:
- `AGENTS.md`
- `README.md`
- `PROJECT_RESUME.md`
- `LESSONS_LEARNED.md`
- `KNOWLEDGE_BASE.md`
- `ARCHITECTURE_DECISIONS.md`

Status: Resolvido

---

### ERR-009

Data: 2026-06-01

Descricao do Problema:
- Rotas administrativas iniciais foram criadas sem autenticacao.

Causa Raiz:
- A camada de login/RBAC ainda nao existia e as rotas foram priorizadas para validar persistencia.

Solucao Aplicada:
- Criado `require_admin_token`.
- `/api/admin/*` passou a exigir `Authorization: Bearer <ADMIN_API_TOKEN>`.
- Adicionados testes para token ausente, invalido e valido.

Como Evitar no Futuro:
- Toda rota administrativa nova deve usar protecao de admin desde o primeiro teste.
- Quando RBAC completo existir, substituir token simples por permissao por usuario/perfil.

Arquivos Afetados:
- `backend/moviprogy_api/security.py`
- `backend/moviprogy_api/routes/admin.py`
- `tests/test_admin_routes.py`
- `.env.example`
- `docker-compose.yml`

Status: Resolvido

---

### ERR-008

Data: 2026-06-01

Descricao do Problema:
- Teste de readiness travou ao tentar conectar em URL PostgreSQL invalida real.

Causa Raiz:
- Teste unitario dependia de comportamento de socket/rede local.

Solucao Aplicada:
- Teste de rota passou a mockar `check_database`.
- `check_database` passou a usar `connect_timeout=1` e capturar excecoes de conexao.

Como Evitar no Futuro:
- Teste unitario de rota nao deve depender de conexao real invalida.
- Testes reais de banco devem ficar isolados em testes de integracao com `DATABASE_URL`.

Arquivos Afetados:
- `backend/moviprogy_api/database.py`
- `tests/test_readiness.py`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-007

Data: 2026-05-31

Descricao do Problema:
- PostgreSQL no Docker ficou `unhealthy` durante a primeira inicializacao em bind mount local.

Causa Raiz:
- Inicializacao do cluster em `runtime/postgres/data` demorou mais que o `start_period` inicial.
- O health check consultou o banco antes do `CREATE DATABASE` terminar.

Solucao Aplicada:
- Aumentado `start_period` para 60s.
- Aumentado `retries` para 12.

Como Evitar no Futuro:
- Em bind mount Windows, considerar inicializacao de banco mais lenta.
- Health check de banco precisa tolerar bootstrap inicial.

Arquivos Afetados:
- `docker-compose.yml`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-006

Data: 2026-05-31

Descricao do Problema:
- Build Docker falhou com `backend does not exist or is not a directory`.

Causa Raiz:
- `pyproject.toml` restringe pacotes ao diretorio `backend`, mas o Dockerfile executava `pip install .` antes de copiar `backend`.

Solucao Aplicada:
- Alterada a ordem do Dockerfile para copiar `backend` antes de instalar o pacote.

Como Evitar no Futuro:
- Quando `pyproject.toml` usa `where = ["backend"]`, o diretorio `backend` precisa existir antes de `pip install .`.

Arquivos Afetados:
- `Dockerfile`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-005

Data: 2026-05-31

Descricao do Problema:
- `pip install -e .` falhou porque o setuptools tentou empacotar diretorios de runtime como pacotes Python.

Causa Raiz:
- O projeto usa layout com `backend/`, `logs/` e `runtime/` na raiz.
- `pyproject.toml` nao restringia a descoberta de pacotes ao diretorio `backend`.

Solucao Aplicada:
- Configurado `[tool.setuptools.packages.find] where = ["backend"]`.
- Dockerfile passou a atualizar `pip` e `setuptools` antes da instalacao.

Como Evitar no Futuro:
- Manter descoberta de pacotes restrita ao codigo-fonte.
- Nao deixar diretorios de dados/logs serem considerados pacotes.

Arquivos Afetados:
- `pyproject.toml`
- `Dockerfile`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-004

Data: 2026-05-31

Descricao do Problema:
- Persistencia JSON inicial gravava token de dispositivo em texto puro.

Causa Raiz:
- A chave do dicionario de sessoes usava o token original retornado ao player.

Solucao Aplicada:
- Persistir sessoes usando SHA-256 do token.
- Manter token real apenas na resposta HTTP da ativacao.
- Adicionar teste para bloquear token em texto puro no arquivo.

Como Evitar no Futuro:
- Nunca persistir tokens, senhas ou segredos em texto puro.
- Testar explicitamente que arquivos locais nao contem segredos retornados pela API.

Arquivos Afetados:
- `backend/moviprogy_api/domain/devices.py`
- `tests/test_device_registry_persistence.py`
- `LESSONS_LEARNED.md`
- `KNOWLEDGE_BASE.md`
- `ARCHITECTURE_DECISIONS.md`
- `PROJECT_RESUME.md`

Status: Resolvido

---

### ERR-003

Data: 2026-05-31

Descricao do Problema:
- `docker compose up --build -d` falhou porque o Docker daemon nao estava rodando.

Causa Raiz:
- Docker CLI estava instalado, mas Docker Desktop/Linux engine nao estava ativo.

Solucao Aplicada:
- Docker Desktop foi iniciado.
- Build e container foram executados depois que `docker info` respondeu com sucesso.

Como Evitar no Futuro:
- Antes de rodar Docker, validar `docker info`.
- Se falhar, abrir Docker Desktop e aguardar o daemon ficar pronto.

Arquivos Afetados:
- `README.md`
- `KNOWLEDGE_BASE.md`
- `LESSONS_LEARNED.md`

Status: Resolvido

---

### ERR-002

Data: 2026-05-31

Descricao do Problema:
- Testes com fixture `tmp_path` falharam no Windows com `PermissionError` ao acessar o Temp padrao do usuario.

Causa Raiz:
- O pytest tentou usar `C:\Users\Rodrigo Tejada\AppData\Local\Temp\pytest-of-Rodrigo Tejada`, sem permissao de leitura no momento da execucao.

Solucao Aplicada:
- Configurado `pytest.ini` com `addopts = --basetemp=.pytest_tmp`.
- Adicionado `.pytest_tmp/` ao `.gitignore`.

Como Evitar no Futuro:
- Manter diretorio temporario dos testes dentro do workspace.
- Nao depender do Temp global do Windows para testes automatizados.

Arquivos Afetados:
- `pytest.ini`
- `.gitignore`
- `LESSONS_LEARNED.md`

Status: Resolvido
