# Observabilidade e Logs

## Objetivo

Definir eventos, metricas e logs necessarios para operar o sistema.

## Estado atual

- Health check existe.
- Readiness com banco existe.
- Logs estruturados ainda nao foram implementados.

## Health checks

Endpoints:
- `GET /health`
- `GET /health/ready`

Regras:
- `/health` valida processo da API.
- `/health/ready` valida banco.
- Monitoramento deve alertar se qualquer um falhar.

## Logs obrigatorios

### API

- Startup.
- Erro de migration.
- Erro de banco.
- Erro de autenticacao.
- Erro de autorizacao.
- Erro em upload.
- Erro em download.

### Admin

- Login.
- Criacao/edicao de cliente.
- Criacao/edicao de dispositivo.
- Criacao/edicao de midia.
- Criacao/edicao/publicacao de playlist.
- Alteracao de permissao.
- Configuracao de storage.

### Player

- Ativacao.
- Consulta de manifesto.
- Inicio de download.
- Download concluido.
- Falha de download.
- Hash invalido.
- Playlist ativada.
- Operacao offline.

### Google Drive

- Conexao OAuth.
- Refresh token falhou.
- Pasta raiz inacessivel.
- Upload.
- Importacao.
- Sincronizacao.

## Dados proibidos em log

- Senha.
- Hash de senha.
- Token de sessao.
- Refresh token.
- Access token Google.
- Conteudo sensivel de cliente.

## Tabela planejada: logs

Campos:
- id.
- origem.
- nivel.
- evento.
- cliente_id.
- usuario_id.
- dispositivo_id.
- dados.
- criado_em.

## Alertas

- API down.
- Banco down.
- Disco acima de 80%.
- Falha repetida de player.
- Erro de download em massa.
- Google Drive desconectado.
- Backup falhou.

## Criterios de aceite

- Todo erro critico tem log.
- Nenhum log contem segredo.
- Health e readiness sao monitoraveis.
- Eventos de auditoria sao rastreaveis por usuario/cliente.

