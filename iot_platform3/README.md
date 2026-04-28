# Industrial IoT Platform (improved multi-machine layout)

Aquest paquet parteix del repo públic i reestructura el projecte per eliminar:
- duplicació d'inventory
- provisioning no idempotent
- desalineació entre `machine_id`, `MQTT_USERNAME` i ACL
- regeneració accidental de passwords

## Idees clau
- `inventory/` és la font única de veritat
- `machine_id == MQTT_USERNAME`
- els fitxers d'edge per màquina es generen amb `render_edge_config.py`
- el provisioning MQTT és idempotent
- les ACLs escalen per convenció de topics, no per màquina

## Flux bàsic
1. Declarar màquina a `inventory/machines.yaml`
2. Executar `scripts/provision_mqtt_identities.py`
3. Executar `scripts/render_edge_config.py --machine <machine_id>`
4. Desplegar el bundle generat
