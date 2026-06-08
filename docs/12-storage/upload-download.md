# Storage, Upload e Download Controlado

## Objetivo

Definir como arquivos de midia serao recebidos, armazenados, validados e entregues ao player.

## Estado atual

- Metadados de midia existem no banco.
- Google Drive e o storage principal SaaS das midias.
- Upload Google Drive existe para admin.
- Download controlado existe para o player.
- Upload fisico local permanece apenas fallback tecnico/local.

## Principios

- Player nao deve receber credenciais de storage.
- Player deve baixar arquivo e reproduzir localmente.
- Backend deve validar permissao antes de liberar download.
- Arquivo so entra na playlist se tamanho e hash forem validos.

## Storage principal Google Drive

Estrutura obrigatoria:

```text
MoviProgy_Midias/
  {cliente}/
    Videos/
    Imagens/
    Playlists/
```

Regras:
- Servidor nao deve armazenar copia permanente dos videos.
- Banco armazena metadados e referencias Google Drive.
- Upload de video vai para `Videos`.
- Upload de imagem vai para `Imagens`.
- Remover midia de playlist nao apaga arquivo do Drive.
- Apagar definitivamente exige confirmacao `APAGAR`.

## Storage local fallback

Pasta:
- `runtime/media`

Estrutura:

```text
runtime/media/
  clientes/
    {cliente_id}/
      midias/
        {midia_id}/
          original.ext
```

Regras:
- Nome fisico deve ser gerado pelo servidor.
- Nome original pode ser salvo apenas como metadado.
- Caminho nao deve vir direto do usuario.
- Nao servir diretorio estatico aberto.

## Upload Google Drive

Endpoint implementado:
- `POST /api/integrations/google-drive/upload-media`

Campos:
- cliente_id.
- arquivo.
- tipo.

Validacoes:
- Cliente existe.
- Usuario pode acessar cliente.
- Google Drive conectado.
- Pasta raiz definida.
- Estrutura do cliente criada.
- MIME type recebido do upload.
- Metadados retornados pelo Drive registrados no banco.

Tipos permitidos iniciais:
- Video: `.mp4`
- Imagem: `.jpg`, `.jpeg`, `.png`, `.webp`

Fluxo:
1. Receber arquivo.
2. Criar/localizar estrutura do cliente.
3. Enviar arquivo ao Google Drive.
4. Registrar metadados no banco.
5. Retornar midia cadastrada.

Implementacao atual:
- Usa OAuth Google Drive.
- Usa `google_drive_file_id`, `google_drive_folder_id`, MIME type e link de visualizacao.
- Exige `Authorization: Bearer <access_token>` de usuario admin.
- Retorna modelo `Midia`.

## Download controlado

Endpoint implementado:
- `GET /api/player/midias/{midia_id}/download`

Autenticacao:
- `Authorization: Bearer <token_dispositivo>`

Validacoes:
- Token valido.
- Dispositivo nao bloqueado.
- Midia pertence a playlist atual do dispositivo.
- Midia esta ativa.
- Arquivo existe na origem configurada.

Resposta:
- Arquivo como stream.
- Headers de tamanho.
- Content-Type correto.
- Cache controlado.

Implementacao atual:
- Usa Google Drive como origem principal.
- Usa `MOVIPROGY_MEDIA_DIR` apenas para fallback local.
- Valida token do dispositivo.
- Valida se midia pertence a playlist atual ativa do dispositivo.
- Valida se midia esta ativa.
- Para Google Drive, retransmite via API sem salvar copia permanente.
- Para local, resolve caminho dentro do diretorio base.
- Retorna 404 quando arquivo fisico nao existe.

Regras:
- Nao aceitar caminho por query string.
- Nao expor caminho real no servidor.
- Nao permitir download de midia de outro cliente.
- Nao permitir download de midia fora da playlist atual.

## Erros

- 401: token ausente/invalido.
- 403: dispositivo sem acesso.
- 404: midia ou arquivo nao encontrado.
- 409: midia nao pertence a playlist atual.
- 422: arquivo invalido no upload.
- 507: storage local sem espaco.

## Testes obrigatorios

- Upload valido de imagem.
- Upload valido de video.
- Bloqueio por tipo invalido.
- Bloqueio por tamanho.
- Hash calculado corretamente.
- Download com token valido.
- Bloqueio sem token.
- Bloqueio para midia fora da playlist.
- Bloqueio para dispositivo bloqueado.
- Arquivo ausente retorna erro controlado.
