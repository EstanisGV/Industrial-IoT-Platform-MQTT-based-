# Edge Raspberry Pi - PLC Collector

Aquest directori conté el codi base que s'executarà a cada edge device/Raspberry.

## Què s'executa a l'edge?

- `plc-collector`
- `.env` generat per màquina
- `machine_info.yaml` generat per màquina
- `machine_tags.yaml` generat per perfil
- certificats TLS quan estiguin activats

## Què NO s'executa a l'edge?

- broker Mosquitto
- inventory global
- scripts de provisioning
- secrets d'altres màquines
- base de dades
- ML
