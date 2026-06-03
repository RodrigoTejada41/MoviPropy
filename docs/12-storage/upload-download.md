# Storage, Upload e Download Controlado

## Objetivo

Definir como arquivos de midia serao recebidos, armazenados, validados e entregues ao player.

## Estado atual

- Metadados de midia existem no banco.
- Upload fisico ainda nao existe.
- Download controlado ainda nao existe.
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

Endpoint planejado:
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

## Download controlado

Endpoint planejado:
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

