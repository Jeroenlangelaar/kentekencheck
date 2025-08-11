-- Schema
create schema if not exists public;

-- Bronregistratie (bestand/leverancier)
create table if not exists public.sources (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,
  uploaded_by   text,
  file_name     text not null,
  file_url      text,
  schema_hint   jsonb,
  uploaded_at   timestamptz not null default now()
);

-- Rauwe regels per bestand (audit-trail voor herleidbaarheid)
create table if not exists public.facts_raw (
  id             bigserial primary key,
  source_id      uuid references public.sources(id) on delete cascade,
  row_data       jsonb not null,
  kenteken_raw   text,
  kenteken_norm  text,
  ingelezen_op   timestamptz not null default now()
);
create index if not exists idx_facts_raw_source on public.facts_raw(source_id);
create index if not exists idx_facts_raw_kenteken_norm on public.facts_raw(kenteken_norm);

-- Canonieke voertuigtabel (laatste waarheid per kenteken)
create table if not exists public.vehicles (
  id               bigserial primary key,
  kenteken         text not null unique,
  bandenmaat       text,
  meldcode         text,
  leasemaatschappij text,
  wiba_status      text,
  first_seen_at    timestamptz,
  last_seen_at     timestamptz not null default now()
);
create index if not exists idx_vehicles_kenteken on public.vehicles(kenteken);

-- View voor publieke weergave (alleen velden die publiek mogen zijn)
create or replace view public.public_vehicles as
select
  kenteken,
  bandenmaat,
  meldcode,
  leasemaatschappij,
  wiba_status,
  last_seen_at
from public.vehicles;

-- Optioneel: fuzzy search ondersteuning
-- create extension if not exists pg_trgm;
-- create index if not exists idx_vehicles_kenteken_trgm on public.vehicles using gin (kenteken gin_trgm_ops);

-- Supabase: schakel Row Level Security in en maak policies
alter table public.vehicles enable row level security;
alter table public.facts_raw enable row level security;
alter table public.sources enable row level security;

-- Policies:
-- 1) Publiek mag de VIEW lezen (rechten op view regelen)
grant usage on schema public to anon, authenticated;
grant select on public.public_vehicles to anon, authenticated;

-- 2) Onderliggende tabellen NIET publiek leesbaar/schrijfbaar
revoke all on public.vehicles from anon;
revoke all on public.facts_raw from anon;
revoke all on public.sources from anon;

-- 3) RLS policies voor service-role of specifieke rol
create policy if not exists vehicles_service_rw on public.vehicles
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy if not exists facts_raw_service_rw on public.facts_raw
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy if not exists sources_service_rw on public.sources
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');