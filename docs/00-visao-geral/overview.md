# Visao geral

## Objetivo

Sistema Online de Midia Indoor com Sincronizacao Offline.

O sistema permite administrar propagandas remotamente e enviar imagens, videos e playlists para dispositivos instalados em clientes.
O painel administrativo opera online.
O player baixa conteudo, salva localmente e continua reproduzindo mesmo sem internet.

## Problema resolvido

Empresas precisam controlar campanhas em telas remotas sem depender de acesso fisico ao equipamento.
O player nao pode parar quando houver queda de internet.

## Escopo inicial

- Painel administrativo online.
- Cadastro de usuarios, clientes e dispositivos.
- Upload de videos e imagens.
- Playlists por cliente.
- Sincronizacao remota.
- Player em loop com cache local.
- Status dos dispositivos.
- Relatorios basicos.
- Controle de permissao.

## Fora do escopo inicial

- Codigo-fonte.
- Layout final do painel.
- App nativo publicado em loja.
- CDN obrigatoria.
- BI avancado.
- Faturamento.

## Estado atual

- Backend, banco PostgreSQL e painel administrativo implementados.
- Docker Compose integrado e validado localmente.
- Google Drive integrado pelo backend, com OAuth configuravel e metadados automaticos.
- Player PWA offline-first especificado, implementado e homologado localmente.
- Deploy publico ainda depende de infraestrutura externa.
