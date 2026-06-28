create table if not exists public.pronosticos_eliminatoria (
    usuario text not null,
    n_partido integer not null,
    p1 integer not null,
    p2 integer not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint pronosticos_eliminatoria_pkey primary key (usuario, n_partido),
    constraint pronosticos_eliminatoria_p1_check check (p1 >= 0 and p1 <= 20),
    constraint pronosticos_eliminatoria_p2_check check (p2 >= 0 and p2 <= 20)
);

create or replace function public.set_pronosticos_eliminatoria_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists set_pronosticos_eliminatoria_updated_at
on public.pronosticos_eliminatoria;

create trigger set_pronosticos_eliminatoria_updated_at
before update on public.pronosticos_eliminatoria
for each row
execute function public.set_pronosticos_eliminatoria_updated_at();
