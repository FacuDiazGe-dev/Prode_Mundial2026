-- Programa la Edge Function sync-live-eliminatoria cada 5 minutos desde Supabase.
-- Ejecutar recien cuando quieras activar la sincronizacion automatica de eliminatoria.

create extension if not exists pg_cron with schema extensions;
create extension if not exists pg_net with schema extensions;

-- Usa los mismos secretos de Vault que el sync de fase de grupos:
-- project_url: https://TU_PROJECT_REF.supabase.co
-- sync_live_secret: el mismo valor que SYNC_LIVE_SECRET en Edge Functions

do $$
begin
  perform cron.unschedule('sync-live-eliminatoria-every-5-min');
exception
  when others then null;
end $$;

select cron.schedule(
  'sync-live-eliminatoria-every-5-min',
  '*/5 * * * *',
  $$
  select net.http_post(
    url := (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/sync-live-eliminatoria',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-sync-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'sync_live_secret')
    ),
    body := jsonb_build_object(
      'source', 'pg_cron',
      'phase', 'eliminatoria',
      'time', now()
    )
  ) as request_id;
  $$
);

-- Ver jobs activos:
-- select * from cron.job order by jobid desc;

-- Ver ultimas ejecuciones:
-- select * from cron.job_run_details order by start_time desc limit 20;
