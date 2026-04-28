# Guia de fitxers del projecte

## Root

- `.gitignore`: evita pujar secrets, `.env`, configs generades, logs i runtime.
- `.env.example`: exemple de variables globals locals.
- `README.md`: documentació general i fluxos principals.

## `inventory/`

- `machines.yaml`: font única de veritat de les màquines. Defineix `machine_id`, planta, línia, protocol i perfil de tags.
- `environments/dev.yaml`: configuració de desenvolupament.
- `environments/prod.yaml`: configuració de producció, amb TLS activat.
- `tag_profiles/*.yaml`: perfils reutilitzables de tags per família de màquina.

## `backend_server/`

- `docker-compose.yml`: arrenca Mosquitto i `mqtt-debug`.
- `mosquitto/config/mosquitto.conf`: configuració MQTT sense TLS.
- `mosquitto/config/mosquitto.tls.conf`: configuració MQTT amb TLS.
- `mosquitto/config/aclfile`: permisos MQTT escalables basats en `%u`.
- `mosquitto/config/passwords`: fitxer real generat, no versionat.
- `mosquitto/config/passwords.example`: explica el format esperat.
- `secrets/*.env.example`: exemples de secrets per serveis backend.
- `mqtt-ingestor/`: esquelet funcional del futur consumidor backend.

## `edge-rpi-v2/`

- `docker-compose.yml`: arrenca el collector edge.
- `docker-compose.tls.yml`: extensió per TLS.
- `.env.example`: exemple de variables edge.
- `templates/`: plantilles per generar bundles per màquina.
- `plc-collector/`: aplicació Python que llegeix dades i publica MQTT.

## `edge-rpi-v2/plc-collector/app/`

- `main.py`: punt d'entrada de l'edge.
- `config.py`: carrega `.env`, `machine_info.yaml` i `machine_tags.yaml`.
- `logger.py`: logging JSON.
- `collectors/mock_client.py`: dades simulades.
- `collectors/s7_client.py`: placeholder per S7 real.
- `collectors/opcua_client.py`: placeholder per OPC UA real.
- `mqtt/publisher.py`: connexió MQTT, TLS opcional i reconnect.
- `services/polling_service.py`: bucle de lectura/publicació telemetry/status.
- `services/heartbeat_service.py`: heartbeat periòdic.

## `scripts/`

- `utils/inventory_loader.py`: funcions comunes per llegir inventory i entorns.
- `utils/secret_store.py`: capa de secrets local/dev substituïble per Azure Key Vault.
- `utils/topic_builder.py`: construeix topics MQTT per convenció.
- `provisioning/provision_mqtt_identities.py`: crea/reutilitza credencials MQTT.
- `provisioning/rotate_mqtt_credentials.py`: rota credencials d'una màquina.
- `provisioning/generate_mosquitto_password_file.py`: reconstrueix el password file.
- `rendering/render_edge_config.py`: genera config edge per una màquina.
- `deploy/package_edge_bundle.py`: crea ZIP desplegable per una màquina.
- `deploy/deploy_edge_bundle.py`: envia bundle per SCP/SSH i arrenca Docker Compose.

## `generated/`

Resultat generat pels scripts. No s'edita manualment i no es versiona.

## `dist/`

Artefactes empaquetats per desplegar. No es versiona.
