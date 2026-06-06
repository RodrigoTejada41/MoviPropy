# Design do Player PWA Offline-First

## Objetivo

Implementar o player real do MoviProgy para navegador kiosk, Windows e Linux,
com base web instalavel. Android e Android TV usam o mesmo PWA em modo kiosk
como primeira entrega.

## Abordagens avaliadas

1. PWA React/TypeScript.
   - Reutiliza a stack aprovada.
   - Entrega multiplataforma imediata.
   - Permite cache offline e instalacao.
2. Aplicativo nativo por plataforma.
   - Melhor integracao com sistema operacional.
   - Aumenta custo, duplicacao e prazo do MVP.
3. Electron.
   - Bom suporte desktop.
   - Nao atende Android e adiciona runtime pesado.

Decisao: PWA React/TypeScript. Electron ou wrapper Android ficam fora do MVP.

## Arquitetura

O player fica em `player/`, separado do painel administrativo. Os modulos sao:

- `api`: ativacao, manifesto, atualizacao, download e telemetria.
- `storage`: token, dispositivo, manifesto e arquivos locais.
- `sync`: comparacao de versao, download, validacao e troca atomica.
- `playback`: reproducao em loop de imagens e videos.
- `telemetry`: fila local de status, logs e confirmacoes.
- `ui`: ativacao e estados operacionais do kiosk.

Nenhum token Google Drive chega ao player. Todo download usa a API MoviProgy.

## Persistencia local

Usar IndexedDB para configuracao, manifestos, fila de telemetria e blobs.

Estrutura logica:

- `device`: token, identificador de hardware e versao do player.
- `active_manifest`: ultima playlist validada.
- `pending_manifest`: playlist em download.
- `media_active`: arquivos da playlist em reproducao.
- `media_pending`: arquivos temporarios.
- `telemetry_queue`: eventos ainda nao enviados.

O Service Worker armazena apenas o shell do aplicativo. Midias ficam no
IndexedDB para permitir validacao e troca atomica controlada.

## Fluxo de ativacao

1. Gerar ou recuperar identificador local do hardware.
2. Receber codigo de ativacao.
3. Enviar `POST /api/player/ativar`.
4. Persistir token e versao retornada.
5. Iniciar sincronizacao.
6. Se o dispositivo estiver bloqueado ou o codigo for invalido, manter estado
   de ativacao com erro recuperavel.

## Fluxo de sincronizacao

1. Consultar `GET /api/player/atualizacao`.
2. Se houver versao nova, buscar `GET /api/player/playlist`.
3. Validar campos obrigatorios do manifesto.
4. Baixar cada midia por `GET /api/player/midias/{midia_id}/download`.
5. Validar tamanho e SHA-256.
6. Manter arquivos em `media_pending` ate todos serem validos.
7. Promover manifesto e arquivos pendentes para ativos em uma transacao.
8. Confirmar em `POST /api/player/sincronizacao/confirmar`.
9. Remover arquivos antigos somente depois da promocao concluida.

Falha em qualquer arquivo preserva integralmente a playlist ativa anterior.

## Reproducao

- Imagem: JPG, PNG ou WEBP pelo tempo definido no item ou na midia.
- Video: MP4 ate o evento de finalizacao.
- Loop infinito seguindo a ordem do manifesto.
- Erro de midia pula para o proximo item e registra telemetria.
- Sem playlist valida exibe estado operacional, nunca tela branca.
- Queda de rede nao interrompe a playlist ativa.

## Telemetria

- Enviar status no inicio, apos sincronizacao e periodicamente.
- Registrar falhas de download, hash, reproducao e API.
- Persistir eventos sem conexao e reenviar em ordem quando a rede voltar.
- Limitar a fila local para evitar crescimento indefinido.
- Nunca registrar token ou conteudo sensivel.

## Interface

Estados:

- Ativacao.
- Sincronizando.
- Reproduzindo.
- Sem playlist.
- Offline com playlist local.
- Erro recuperavel.
- Dispositivo bloqueado.

Durante reproducao, a midia ocupa toda a viewport. Informacoes tecnicas ficam
ocultas e aparecem apenas em uma sobreposicao de diagnostico local.

## Seguranca

- Token persistido apenas no armazenamento local do aplicativo.
- Downloads sempre autenticados.
- URLs e caminhos recebidos nao sao usados como caminhos locais.
- Hash e tamanho sao obrigatorios antes da promocao.
- Limpeza de dados exige acao administrativa local explicita.

## Testes

- Unitarios: validacao de manifesto, hash, ordem e selecao do proximo item.
- Integracao: ativacao, manifesto, download, telemetria e IndexedDB.
- Funcionais: ativacao, sincronizacao completa e reproducao.
- Offline: reinicio sem rede, queda durante download e retorno da conexao.
- Regressao: download incompleto nunca substitui playlist valida.
- Browser: desktop e viewport de Android TV/navegador kiosk.

## Criterios de aceite

- Ativa com codigo real.
- Persiste token e retoma apos reinicio.
- Baixa e valida todos os arquivos.
- Reproduz imagens e videos em loop.
- Continua reproduzindo sem internet.
- Preserva playlist anterior quando uma atualizacao falha.
- Recupera sincronizacao quando a internet volta.
- Envia status, logs e confirmacao.
- Nao expoe tokens ou credenciais externas.
