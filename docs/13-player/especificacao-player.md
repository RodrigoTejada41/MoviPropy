# Especificacao do Player

## Objetivo

Definir o comportamento do player em Android TV Box, Android, Windows, Linux e navegador kiosk.

## Estado atual

- Backend possui ativacao por codigo real.
- Backend retorna manifesto real quando dispositivo tem playlist atual ativa.
- Player real ainda nao foi implementado.

## Plataformas alvo

- Android TV Box.
- Android.
- Windows.
- Linux.
- Navegador kiosk.

## Responsabilidades

- Ativar dispositivo.
- Persistir token local.
- Consultar manifesto.
- Baixar arquivos.
- Validar tamanho e hash.
- Reproduzir playlist em loop.
- Operar offline.
- Enviar status e logs quando API existir.

## Fluxo de ativacao

1. Player abre sem token.
2. Exibe campo de codigo.
3. Envia `POST /api/player/ativar`.
4. Recebe token e versao da playlist.
5. Salva token localmente.
6. Consulta manifesto.

## Fluxo de sincronizacao

1. Consulta `GET /api/player/playlist`.
2. Compara versao local com versao remota.
3. Baixa arquivos ausentes.
4. Salva downloads em pasta temporaria.
5. Valida tamanho.
6. Valida SHA-256.
7. Move arquivos para cache ativo.
8. Atualiza manifesto local.
9. Ativa nova playlist.
10. Remove arquivos antigos somente depois da playlist funcionar.

## Cache local

Estrutura sugerida:

```text
player-data/
  config/
    device.json
  cache/
    active/
    tmp/
    old/
  logs/
```

## Regras offline

- Se internet cair, continuar playlist local.
- Se download falhar, manter playlist anterior.
- Se manifesto remoto estiver invalido, manter manifesto local.
- Se arquivo local estiver corrompido, tentar baixar novamente.
- Nunca mostrar tela vazia se houver playlist local valida.

## Reproducao

Videos:
- MP4 H.264/AAC.

Imagens:
- JPG, PNG, WEBP.

Regras:
- Loop infinito.
- Imagem usa duracao definida na playlist ou padrao.
- Video toca ate fim, salvo configuracao futura.
- Erro em uma midia pula para proxima e registra log.

## Estado visual

Telas:
- Ativacao.
- Baixando conteudo.
- Sem playlist.
- Reproduzindo.
- Erro recuperavel.
- Dispositivo bloqueado.

## API necessaria

Atual:
- `POST /api/player/ativar`.
- `GET /api/player/playlist`.

Pendente:
- `GET /api/player/midias/{midia_id}/download`.
- `POST /api/player/status`.
- `POST /api/player/logs`.
- `POST /api/player/sincronizacao/confirmar`.
- `GET /api/player/atualizacao`.

## Criterios de aceite

- Ativa com codigo valido.
- Rejeita codigo invalido.
- Persiste token.
- Retoma apos reinicio.
- Baixa todos os arquivos.
- Valida hash e tamanho.
- Opera offline.
- Nao substitui playlist valida por download incompleto.
- Recupera sincronizacao quando internet volta.

