# Checklist de Homologacao

## Objetivo

Definir criterios para aprovar uma versao.

## Backend

- Smoke test integrado passa.
- Health responde.
- Readiness responde.
- Login admin funciona.
- Rotas admin exigem token.
- Usuario sem permissao recebe 403.
- Cliente pode ser criado.
- Clientes podem ser listados.
- Dispositivo pode ser criado.
- Dispositivos podem ser listados.
- Eventos do dispositivo podem ser consultados.
- Midia pode ser criada.
- Midias podem ser listadas.
- Playlist pode ser criada.
- Playlists podem ser listadas.
- Midia pode ser vinculada a playlist.
- Player ativa por codigo real.
- Player recebe manifesto real.
- Player consulta atualizacao da playlist.
- Player baixa midia por endpoint controlado.
- Player envia status.
- Player envia logs.
- Player confirma sincronizacao.

## Banco

- Backup gera dump e manifesto com checksum.
- Restore e validado em banco temporario.
- Migrations executam.
- Dados persistem apos restart.
- Queries usam parametros.
- Tokens sao salvos apenas como hash.
- Senhas sao salvas apenas como hash.

## Player

- Ativa dispositivo.
- Consulta manifesto.
- Baixa midias pelo endpoint controlado.
- Valida tamanho/hash.
- Continua offline.
- Nao troca playlist em download falho.

## Frontend

- Health proprio responde em `/health-ui`.
- Login.
- Dashboard.
- Clientes.
- Dispositivos.
- Midias.
- Playlists.
- Editor de playlist.
- Logs.
- Sincronizacoes.
- Configuracoes.

## Storage

- Upload valido.
- Tipo invalido bloqueado.
- Tamanho excedido bloqueado.
- Download controlado por token.
- Midia fora da playlist bloqueada.

## Google Drive

- OAuth.
- Pasta raiz.
- Pasta cliente.
- Importacao.
- Upload.
- Revogacao.
- Falhas registradas.

## Seguranca

- HTTPS em ambiente publicado.
- Token nao aparece em log.
- Senha nao aparece em resposta.
- Cliente nao acessa dados de outro cliente.
- Upload nao permite path traversal.
- Download nao aceita caminho arbitrario.

## Aprovacao

Resultado:
- Aprovado.
- Aprovado com restricoes.
- Reprovado.

Responsaveis:
- CEO Agent.
- QA Agent.
- Cliente/Product Owner.
