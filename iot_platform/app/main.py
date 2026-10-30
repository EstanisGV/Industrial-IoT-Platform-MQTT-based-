import asyncio
import json
import logging
import os
import signal
import uuid
from datetime import datetime, timezone
from psycopg import AsyncConnection
from psycopg.errors import OperationalError
from .config import load_devices
from .reader import MockReader, OPCUAReader
from .spool import Spool

logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'), format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('collector')

async def run_device(machine, spool, lock, stop):
    reader = MockReader(machine) if machine['mode']=='mock' else OPCUAReader(machine)
    interval = float(machine['interval_seconds'])
    log.info('Starting %s mode=%s interval=%ss',machine['id'],machine['mode'],interval)
    try:
        while not stop.is_set():
            try:
                values = await reader.read()
                record = dict(sample_id=str(uuid.uuid4()), ts=datetime.now(timezone.utc).isoformat(),
                              machine_id=machine['id'],source=machine['mode'], values=values)
                async with lock:
                    spool.add(record)
                log.info('sample machine=%s source=%s variables=%s',machine['id'],machine['mode'],len(values))
            except Exception as exc:
                log.warning('reading failed machine=%s: %s',machine['id'],exc)
            try:
                await asyncio.wait_for(stop.wait(),timeout=interval)
            except asyncio.TimeoutError:
                pass
    finally:
        if isinstance(reader,OPCUAReader):
            await reader.close()

async def drain(spool, lock, stop):
    conninfo = 'host={host} port={port} dbname={db} user={user} password={pwd} connect_timeout=5'.format(
       host=os.environ.get('DB_HOST','database'),port=os.environ.get('DB_PORT','5432'),
       db=os.environ.get('DB_NAME','industrial_iot'),user=os.environ.get('DB_USER','iot'),pwd=os.environ['DB_PASSWORD'])
    while not stop.is_set():
        try:
            async with lock:
                batch = spool.batch(100)
            if batch:
                async with await AsyncConnection.connect(conninfo, autocommit=False) as conn:
                    async with conn.cursor() as cur:
                        await cur.executemany("""INSERT INTO telemetry (sample_id,time,machine_id,source,values_json)
                          VALUES (%s,%s,%s,%s,%s::jsonb) ON CONFLICT (time,machine_id,sample_id) DO NOTHING""",
                          [(sid,ts,mid,source,payload) for _,sid,ts,mid,source,payload in batch])
                    await conn.commit()
                async with lock:
                    spool.delete([row[0] for row in batch])
                log.info('persisted=%d spool_remaining=%d',len(batch),spool.count())
        except Exception as exc:
            log.warning('database unavailable, retaining spool: %s',exc)
        try:
            await asyncio.wait_for(stop.wait(), timeout=2)
        except asyncio.TimeoutError:
            pass

async def main():
    devices = load_devices(os.environ.get('INVENTORY_FILE','/app/config/machines.yaml'))
    if not devices:
        raise RuntimeError('No enabled devices')
    spool = Spool(os.path.join(os.environ.get('SPOOL_DIR','/spool'),'queue.db'))
    lock = asyncio.Lock()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    tasks = [asyncio.create_task(run_device(item,spool,lock,stop)) for item in devices]
    tasks.append(asyncio.create_task(drain(spool,lock,stop)))
    await stop.wait()
    await asyncio.gather(*tasks,return_exceptions=True)

if __name__=='__main__':
    asyncio.run(main())
