# Homologacao DEV - 2026-06-06

## Release

- Branch: `develop`
- Commit: `8fd0d7b8c3404bb44d5b5a9dd2996d70061530c9`
- GitHub Actions: `27064778435`
- Release remota: `20260606-142342-8fd0d7b8c340`

## Endpoints

- Painel DEV: `http://172.233.177.135:8081`
- Player DEV: `http://172.233.177.135:8092`

## Resultados

- Backend: 91 testes aprovados; 10 testes condicionais ignorados.
- Frontend: 10 testes aprovados e build concluido.
- Player: 15 testes aprovados e build concluido.
- PostgreSQL: healthy.
- API: healthy.
- Painel: healthy.
- Player: healthy.
- Readiness: banco disponivel.
- Login, rota protegida e logout: aprovados pelo smoke remoto.
- Headers CSP, Referrer-Policy, nosniff e frame deny: aprovados.
- Validacao visual da tela de login: aprovada.
- Console do navegador: sem erros ou avisos.
- Bloqueio PROD: aprovado com codigo de saida 3.

## Recursos

- Memoria dos containers em repouso: aproximadamente 125 MB.
- VPS: aproximadamente 1 GB de RAM e 495 MB de swap.
- Disco livre apos deploy: aproximadamente 17 GB.

## Pendencias para PROD

- Definir dominio do painel.
- Definir dominio do player.
- Configurar HTTPS.
- Configurar URLs e secrets de producao no GitHub.
- Ampliar capacidade antes de manter DEV e PROD simultaneamente.
- Obter aprovacao explicita.
- Alterar `PRODUCTION_APPROVED` somente durante a publicacao aprovada.

## Status

DEV aprovado tecnicamente. PROD nao publicado.
