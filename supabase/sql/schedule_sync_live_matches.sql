-- Programa la Edge Function sync-live-matches cada 5 minutos desde Supabase.
-- Ejecutar una vez en Supabase SQL Editor despues de desplegar la funcion.

create extension if not exists pg_cron with schema extensions;
create extension if not exists pg_net with schema extensions;

-- Guardar estos secretos una sola vez en Vault.
-- Reemplazar los valores antes de ejecutar si todavia no existen.
-- Si ya existen, no vuelvas a crearlos: podes saltar estas dos lineas.
-- select vault.create_secret('https://TU_PROJECT_REF.supabase.co', 'project_url');
-- select vault.create_secret('UN_SECRETO_LARGO_ALEATORIO', 'sync_live_secret');

do $$
begin
  perform cron.unschedule('sync-live-matches-every-5-min');
exception
  when others then null;
end $$;

select cron.schedule(
  'sync-live-matches-every-5-min',
  '*/5 * * * *',
  $$
  select net.http_post(
    url := (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/sync-live-matches',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-sync-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'sync_live_secret')
    ),
    body := jsonb_build_object(
      'source', 'pg_cron',
      'time', now()
    )
  ) as request_id;
  $$
);

-- Ver jobs activos:
-- select * from cron.job order by jobid desc;

-- Ver ultimas ejecuciones:
-- select * from cron.job_run_details order by start_time desc limit 20;
