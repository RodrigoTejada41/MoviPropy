# Arquitetura

## Modulos

### Painel Web Administrativo

Interface online para administradores gerenciarem clientes, usuarios, dispositivos, midias, playlists, campanhas, sincronizacoes e relatorios.

### Backend/API

Camada central de autenticacao, regras de negocio, permissoes, contratos do painel e contratos do player.

### Banco de Dados

Armazena usuarios, clientes, dispositivos, midias, playlists, campanhas, sincronizacoes, logs e configuracoes.

### Armazenamento de Midias

Armazena arquivos enviados.
Pode ser local no servidor no MVP.
Deve permitir evolucao para storage externo ou CDN.
Google Drive esta documentado como storage externo pos-MVP, controlado pelo backend.

### Player Cliente

Executa em Android TV Box, Android, PC Windows/Linux ou navegador kiosk.
Baixa manifestos e arquivos.
Reproduz localmente em loop.
Nao deve fazer streaming direto do Google Drive.

### Servico de Sincronizacao

Compara versoes, baixa arquivos, valida hash/tamanho, atualiza manifesto local e confirma sincronizacao.

### Logs e Monitoramento

Registra status dos dispositivos, falhas, downloads, erros de player e eventos administrativos.

## Fluxo operacional

1. Administrador cadastra cliente.
2. Administrador cadastra dispositivo.
3. Sistema gera codigo de ativacao.
4. Cliente instala ou abre player.
5. Player autentica no servidor.
6. Player baixa playlist e midias.
7. Player salva arquivos localmente.
8. Player reproduz em loop.
9. Painel altera campanha.
10. Player detecta atualizacao.
11. Player baixa arquivos novos.
12. Player valida download.
13. Player ativa nova playlist.
14. Player mantem operacao offline se a internet cair.

## Decisoes pendentes

- Provedor, dominio, HTTPS e estrategia de storage da producao.
- Politica operacional de rotacao da chave de criptografia dos tokens OAuth.
