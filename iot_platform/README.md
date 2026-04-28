# Industrial IoT Platform - MQTT Based

Plataforma Industrial IoT distribuïda amb:

- Edge mínim per màquina/Raspberry
- MQTT com a protocol principal
- Mosquitto com a broker backend
- Inventory centralitzat
- Provisioning idempotent d'identitats MQTT
- Configuració edge generada automàticament
- Separació entre codi, secrets, templates, generated i dist

## Regles d'arquitectura

- `inventory/` és la font única de veritat funcional.
- `machine_id == MQTT_USERNAME`.
- L'edge no fa ML ni preprocessat.
- L'edge només llegeix i publica.
- Backend gestiona broker, autenticació, persistència futura i ML futur.
- Docker Compose, sense Kubernetes ni Swarm.
- Secrets fora de Git.
- En producció, TLS obligatori.

## Flux bàsic

```bash
python scripts/provisioning/provision_mqtt_identities.py --env dev
python scripts/rendering/render_edge_config.py --env dev --machine index_ms40_01
python scripts/deploy/package_edge_bundle.py --machine index_ms40_01
```

## Què va on?

### Backend server
- `backend_server/`
- `inventory/`
- `scripts/`
- `secrets/` o futur Azure Key Vault
- `generated/`
- `dist/`

### Edge device
Només el bundle generat de la seva màquina:

- `docker-compose.yml`
- `.env`
- `plc-collector/config/machine_info.yaml`
- `plc-collector/config/machine_tags.yaml`
- `plc-collector/certs/` quan TLS estigui actiu
