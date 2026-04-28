# Edge Raspberry Pi - PLC Collector v2

Aquesta versió incorpora:
- reconnect robust MQTT amb backoff exponencial
- heartbeat MQTT periòdic
- suport TLS/MQTTS
- logs més clars
- preparació per multi-màquina
- versió simple de configuració (`config_version`)

## Fitxers sensibles
No guardis credencials ni certificats al codi.

### Variables sensibles
Posa-les a `.env`:
- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_USERNAME`
- `MQTT_PASSWORD`
- `MQTT_TLS_*`
- `PLC_IP`
- `OPCUA_URL`
- `OPCUA_USERNAME`
- `OPCUA_PASSWORD`

### Certificats TLS
Posa'ls a:
- `plc-collector/certs/ca.crt`
- `plc-collector/certs/client.crt`
- `plc-collector/certs/client.key`

## Configuració funcional
Aquests fitxers no són sensibles:
- `plc-collector/config/machine_info.yaml`
- `plc-collector/config/machine_tags.yaml`

## Arrencar
1. Copia `.env.example` a `.env`
2. Omple credencials, IPs i certificats
3. Executa:

```bash
docker compose up --build
```

## Topics MQTT
- telemetry: `factory/{plant}/{machine_id}/telemetry`
- heartbeat: `factory/{plant}/{machine_id}/heartbeat`
- status: `factory/{plant}/{machine_id}/status`

## Nota d'arquitectura
Per producció, aquests fitxers de `config/` no s'han d'editar manualment:
- s'han de generar des de `inventory/`
- el `machine_id` ha de coincidir amb el `MQTT_USERNAME`
