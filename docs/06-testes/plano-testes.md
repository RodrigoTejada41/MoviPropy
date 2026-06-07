# Plano de testes

## Testes unitarios

- Regras de permissao.
- Selecionar playlist ativa.
- Validar manifesto.
- Validar hash e tamanho de arquivo.
- Regras de bloqueio de dispositivo.

## Testes de integracao

- Login.
- Cadastro de cliente.
- Cadastro de dispositivo.
- Cadastro de midia.
- Cadastro de playlist.
- Vinculo de midia em playlist.
- Ativacao do player.
- Consulta de playlist.
- Envio de status.
- Confirmacao de sincronizacao.

## Testes funcionais

- Fluxo completo do painel.
- Playwright valida login, dashboard, navegacao para clientes e logout com API controlada.
- Upload de midia.
- Criacao de playlist.
- Ativacao de campanha.
- Consulta de relatorios.

## Testes offline

- Player inicia sem internet usando playlist local.
- Internet cai durante reproducao.
- Internet cai durante download.
- Player retoma sincronizacao quando internet volta.

## Testes de seguranca

- Login invalido.
- Usuario inativo.
- Usuario sem perfil admin em rota administrativa.
- Token expirado.
- Token de outro cliente.
- Vinculo de midia em playlist de outro cliente.
- Upload com extensao invalida.
- Upload acima do limite.
- Tentativa de SQL Injection.
- OAuth Google Drive com `state` invalido.
- Tentativa de acessar arquivo Drive de outro cliente.
- Vazamento de token Google em resposta ou log.
- Persistencia de senha em texto puro.
- Persistencia de token admin em texto puro.

## Testes de performance

- Baseline local automatizado por `scripts/load_smoke.py`.
- Executar 100 requisicoes por alvo com concorrencia 10, erro zero e p95 menor que 1000 ms.
- Listagem paginada.
- Upload de midia grande.
- Download simultaneo por varios players.
- Atualizacao de status em lote.
- Download de midias externas com arquivos grandes.

## Testes Google Drive pos-MVP

- Conectar conta Google.
- Selecionar pasta raiz.
- Criar pasta de cliente.
- Listar arquivos por cliente.
- Importar arquivo existente.
- Enviar imagem valida.
- Enviar video valido.
- Bloquear extensao invalida.
- Bloquear MIME type invalido.
- Calcular tamanho e hash.
- Vincular midia a playlist.
- Gerar manifesto sem credenciais Google.
- Gerar link controlado de download.
- Player baixar e validar arquivo.
- Player manter playlist antiga em falha de download.
- Revogar integracao e bloquear operacoes novas.
- Registrar auditoria de falha.

## Criterio minimo de homologacao

- Fluxo online completo aprovado.
- Fluxo offline completo aprovado.
- Sincronizacao com falha de internet aprovada.
- Isolamento entre clientes aprovado.
- Logs de erro e status registrados.
