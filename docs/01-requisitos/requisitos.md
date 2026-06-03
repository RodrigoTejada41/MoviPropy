# Requisitos

## Requisitos funcionais

- Administrar clientes.
- Administrar usuarios.
- Administrar dispositivos.
- Ativar dispositivo por codigo.
- Enviar imagens e videos.
- Criar playlists.
- Definir playlist ativa por cliente ou dispositivo.
- Sincronizar midias para o player.
- Reproduzir midias em loop.
- Operar offline com ultima playlist valida.
- Registrar status do dispositivo.
- Registrar logs de sincronizacao.
- Emitir relatorios basicos.

## Regras de negocio

- Cliente acessa somente seus proprios dados.
- Administrador master acessa todos os clientes.
- Usuario comum acessa apenas clientes permitidos.
- Dispositivo bloqueado nao sincroniza.
- Midia desativada nao deve ser exibida.
- Playlist ativa substitui playlist anterior somente apos sincronizacao valida.
- Download incompleto nao substitui arquivo valido.
- Player deve manter ultima playlist funcional.
- Sistema deve registrar logs de sincronizacao.

## Perfis

### Administrador master

- Acesso total.
- Gerencia clientes, usuarios, dispositivos, midias, playlists, campanhas e configuracoes.

### Administrador do cliente

- Gerencia dados do proprio cliente.
- Nao acessa outros clientes.

### Operador

- Opera midias, playlists e campanhas permitidas.
- Nao altera configuracoes criticas.

### Visualizador

- Consulta dashboards, dispositivos, relatorios e logs.
- Nao altera dados.

## Criterios de aceite iniciais

- Player nao para sem internet.
- Player nao apaga midia antiga antes de validar nova.
- Dispositivo informa status e ultima sincronizacao.
- Permissao impede acesso entre clientes.
- API rejeita dispositivo sem token valido.
