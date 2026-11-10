-- Aurora Agent AI — Supabase Postgres + pgvector Schema
-- Run this in your Supabase SQL Editor to set up all tables and vector search RPC.

create extension if not exists vector;

-- 1. Agents Table
create table if not exists agents (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    slug text unique not null,
    description text,
    prompt_instructions text,
    is_master boolean default false,
    is_active boolean default true,
    created_at timestamptz default now()
);

-- 2. Customers Table
create table if not exists customers (
    id uuid primary key default gen_random_uuid(),
    customer_key text unique not null,
    created_at timestamptz default now()
);

-- 3. Conversations Table
create table if not exists conversations (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid references customers(id) on delete cascade,
    agent_id uuid references agents(id) on delete set null,
    channel text default 'chat',
    status text default 'active',
    created_at timestamptz default now()
);

-- 4. Messages Table
create table if not exists messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid references conversations(id) on delete cascade,
    role text not null,
    content text not null,
    created_at timestamptz default now()
);

-- 5. Knowledge Documents Table
create table if not exists knowledge_documents (
    id uuid primary key default gen_random_uuid(),
    agent_id uuid references agents(id) on delete cascade,
    file_name text not null,
    storage_path text not null,
    created_at timestamptz default now()
);

-- 6. Knowledge Chunks Table (1536 dimensions for text-embedding-3-small)
create table if not exists knowledge_chunks (
    id uuid primary key default gen_random_uuid(),
    agent_id uuid references agents(id) on delete cascade,
    document_id uuid references knowledge_documents(id) on delete cascade,
    content text not null,
    embedding vector(1536),
    created_at timestamptz default now()
);

-- 7. Vector Search RPC Function
create or replace function match_knowledge_chunks(
    query_embedding vector(1536),
    agent_uuid uuid,
    match_count int default 5
)
returns table (
    id uuid,
    document_id uuid,
    content text,
    similarity float
)
language sql stable
as $$
    select
        kc.id,
        kc.document_id,
        kc.content,
        1 - (kc.embedding <=> query_embedding) as similarity
    from knowledge_chunks kc
    where kc.agent_id = agent_uuid
    order by kc.embedding <=> query_embedding
    limit match_count;
$$;

-- 8. Seed Default Aurora Agents
insert into agents (name, slug, description, prompt_instructions, is_master, is_active)
values
    (
        'Aurora Master',
        'master',
        'Central intelligence orchestrator that analyzes your intent and seamlessly connects you with the right specialist agent.',
        'Act as the Aurora Master orchestrator. Greet users warmly, clarify ambiguous requests, and route specialized inquiries to Finance, HR, Sales, or Operations.',
        true,
        true
    ),
    (
        'Aurora Finance',
        'finance',
        'Handles payroll, invoices, expense tracking, reimbursements, budgets, tax compliance, and financial reporting.',
        'Provide accurate guidance on payroll schedules, invoice processing, expense reimbursement policies, budget allocations, and financial workflows.',
        false,
        true
    ),
    (
        'Aurora HR',
        'hr',
        'Manages hiring, leave balances, attendance, employee onboarding, workplace policies, benefits, and performance reviews.',
        'Assist with PTO and leave policies, onboarding checklists, employee benefits, attendance guidelines, and talent acquisition processes.',
        false,
        true
    ),
    (
        'Aurora Sales',
        'sales',
        'Accelerates lead qualification, CRM pipeline management, custom pricing quotes, proposals, follow-ups, and deal closing.',
        'Support sales workflows including lead qualification, pricing tiers, proposal templates, CRM updates, and client follow-up strategies.',
        false,
        true
    ),
    (
        'Aurora Operations',
        'operations',
        'Optimizes inventory, supply chain logistics, vendor SLAs, standard operating procedures (SOPs), and daily fulfillment.',
        'Guide users through operational SOPs, inventory restocking, vendor coordination, shipping logistics, and process troubleshooting.',
        false,
        true
    )
on conflict (slug) do update set
    name = excluded.name,
    description = excluded.description,
    prompt_instructions = excluded.prompt_instructions,
    is_master = excluded.is_master,
    is_active = excluded.is_active;
