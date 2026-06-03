# Player offline

## Plataformas alvo

- Android TV Box.
- Android.
- PC Windows.
- PC Linux.
- Navegador em modo kiosk.

## Funcionamento

1. Inicializa em tela cheia.
2. Exibe tela de ativacao se nao houver token local.
3. Autentica com codigo de ativacao.
4. Salva token do dispositivo.
5. Consulta manifesto da playlist ativa.
6. Baixa arquivos ausentes.
7. Valida tamanho e hash.
8. Atualiza manifesto local.
9. Reproduz em loop.
10. Monitora internet.
11. Sincroniza quando conexao voltar.
12. Reinicia fluxo em caso de erro recuperavel.

## Manifesto atual

Status: implementado no backend.

Regras:
- Ativacao real usa `dispositivos.codigo_ativacao`.
- Manifesto real usa `dispositivos.playlist_atual_id`.
- Playlist precisa estar ativa.
- Arquivos sao montados a partir de `playlist_midias`.
- Apenas midias ativas entram no manifesto.
- Manifesto demo permanece apenas como fallback local sem dados reais.
- Ainda falta endpoint de download controlado para arquivos.

## Sincronizacao segura

1. Consultar servidor.
2. Comparar versao local com versao online.
3. Baixar arquivos novos para pasta temporaria.
4. Validar tamanho e hash.
5. Atualizar manifesto local.
6. Ativar nova playlist.
7. Confirmar sincronizacao.
8. Remover arquivos antigos somente depois da nova playlist funcionar.
9. Manter backup da ultima playlist valida.

## Regras obrigatorias

- Nunca apagar midia antiga antes de validar nova.
- Download incompleto nao substitui arquivo valido.
- Playlist local valida sempre tem prioridade sobre tela vazia.
- Falha de internet nao interrompe reproducao.
- Token do dispositivo deve ficar protegido.
- Player bloqueado nao sincroniza.
- Player nao deve fazer streaming direto do Google Drive.
- Player nao deve receber credenciais Google.
- Midia externa deve ser baixada por URL controlada pelo backend.
- Midia baixada deve ser validada por tamanho e hash antes de entrar na playlist ativa.

## Midias suportadas

- Video: MP4 H.264 com AAC.
- Imagem: JPG, PNG, WEBP.
- Resolucao recomendada: 1280x720 e 1920x1080.
- Tamanho maximo: configuravel.
- Duracao padrao de imagem: configuravel.

## Google Drive

Status: planejado.

Fluxo:
1. Backend envia manifesto com metadados e URL controlada.
2. Player baixa o arquivo para pasta temporaria.
3. Player valida tamanho.
4. Player valida hash.
5. Player move arquivo para cache ativo.
6. Player reproduz localmente.

Bloqueios:
- Nao reproduzir arquivo remoto por streaming.
- Nao substituir playlist valida se download falhar.
- Nao armazenar identificadores ou tokens que permitam acesso direto indevido ao Drive.
