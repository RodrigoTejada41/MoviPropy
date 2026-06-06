# Deploy de Producao

## Objetivo

Definir o processo de publicacao em ambiente produtivo.

## Estado atual

- Compose independente para DEV e PROD implementado em `deploy/compose.yml`.
- Deploy automatico DEV configurado para a branch `develop`.
- Deploy PROD configurado como manual, versionado e protegido.
- PROD permanece bloqueado ate dominio, HTTPS, capacidade e aprovacao.
- Detalhes: `docs/14-operacao/ambientes-dev-prod.md`.

## Ambientes

### Local

Uso:
- Desenvolvimento.
- Testes manuais.
- Simulacao.

Comando:
- `docker compose up --build -d`.

### Homologacao

Uso:
- Validar release antes de producao.

Requisitos:
- HTTPS.
- Banco separado.
- Storage separado.
- Dados de teste.
- Logs habilitados.

### Producao

Uso:
- Ambiente real de clientes.

Requisitos:
- HTTPS obrigatorio.
- Backup automatico.
- Monitoramento.
- Logs persistentes.
- Variaveis de ambiente seguras.
- Rollback documentado.

## Variaveis obrigatorias

- `DATABASE_URL`.
- `POSTGRES_DB`.
- `POSTGRES_USER`.
- `POSTGRES_PASSWORD`.
- `MOVIPROGY_ADMIN_EMAIL`.
- `MOVIPROGY_ADMIN_PASSWORD`.
- `ADMIN_API_TOKEN` apenas fallback local.

Futuras:
- `STORAGE_BACKEND`.
- `MEDIA_ROOT`.
- `GOOGLE_CLIENT_ID`.
- `GOOGLE_CLIENT_SECRET`.
- `GOOGLE_REDIRECT_URI`.
- `SECRET_KEY`.

## Checklist pre-deploy

- Testes unitarios passaram.
- Testes de integracao passaram.
- Migrations revisadas.
- Backup do banco realizado.
- `.env` validado.
- Logs configurados.
- Health check validado.
- Rollback definido.
- Versao documentada.

## Processo

1. Congelar release.
2. Rodar testes.
3. Gerar backup.
4. Aplicar migrations.
5. Subir containers.
6. Validar `/health`.
7. Validar `/health/ready`.
8. Validar `/health-ui`.
9. Testar login admin sem credenciais embutidas no HTML/JavaScript.
10. Testar ativacao player.
11. Registrar resultado.

## Rollback

1. Parar versao nova.
2. Restaurar imagem anterior.
3. Restaurar banco se migration for irreversivel.
4. Validar health.
5. Registrar incidente.

## Criterios de aceite

- API responde health.
- Banco disponivel.
- Login admin funciona.
- Player ativa.
- Manifesto retorna.
- Logs registram erros.
- Backup existe antes do deploy.
