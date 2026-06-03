# Storage, Upload e Download Controlado

## Objetivo

Definir como arquivos de midia serao recebidos, armazenados, validados e entregues ao player.

## Estado atual

- Metadados de midia existem no banco.
- Upload fisico local existe para admin.
- Download controlado local existe para o player.
- Google Drive esta documentado como storage planejado.

## Principios

- Player nao deve receber credenciais de storage.
- Player deve baixar arquivo e reproduzir localmente.
- Backend deve validar permissao antes de liberar download.
- Arquivo so entra na playlist se tamanho e hash forem validos.

## Storage local planejado

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

## Upload

Endpoint implementado:
- `POST /api/admin/midias/upload`

Campos:
- cliente_id.
- arquivo.
- tipo.
- duracao_segundos opcional.

Validacoes:
- Cliente existe.
- Usuario pode acessar cliente.
- Extensao permitida.
- MIME type permitido.
- Tamanho maximo.
- Hash SHA-256 calculado pelo backend.
- Arquivo salvo primeiro em pasta temporaria.
- Caminho relativo gerado pelo servidor.

Tipos permitidos iniciais:
- Video: `.mp4`
- Imagem: `.jpg`, `.jpeg`, `.png`, `.webp`

Fluxo:
1. Receber arquivo.
2. Salvar em `runtime/tmp`.
3. Validar tamanho.
4. Validar tipo.
5. Calcular SHA-256.
6. Mover para `runtime/media`.
7. Registrar midia no banco.
8. Retornar metadados.

Implementacao atual:
- Usa `MOVIPROGY_MEDIA_DIR`.
- Usa `MOVIPROGY_TMP_DIR`.
- Usa `MOVIPROGY_MAX_UPLOAD_BYTES`, default 512 MB.
- Exige `Authorization: Bearer <access_token>` de usuario admin.
- Salva em `clientes/{cliente_id}/midias/{midia_id}/original.ext`.
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
- Arquivo existe.

Resposta:
- Arquivo como stream.
- Headers de tamanho.
- Content-Type correto.
- Cache controlado.

Implementacao atual:
- Usa `MOVIPROGY_MEDIA_DIR`.
- Valida token do dispositivo.
- Valida se midia pertence a playlist atual ativa do dispositivo.
- Valida se midia esta ativa.
- Resolve caminho dentro do diretorio base.
- Retorna 404 quando arquivo fisico nao existe.

Regras:
- Nao aceitar caminho por query string.
- Nao expor caminho real no servidor.
- Nao permitir download de midia de outro cliente.
- Nao permitir download de midia fora da playlist atual.

## Google Drive

Regra:
- Backend deve intermediar.
- Player nao acessa Drive diretamente.
- Link temporario ou stream controlado deve respeitar autorizacao do dispositivo.

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
