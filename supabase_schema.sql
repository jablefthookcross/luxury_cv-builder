-- =========================================================
-- VitaeCraft AI - Supabase Database Schema & RLS Policies
-- Execute this script in Supabase Dashboard -> SQL Editor
-- =========================================================

-- 1. Create Profiles Table (Stores user's baseline master profile)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT DEFAULT 'Michał Kosowski',
    email TEXT UNIQUE,
    phone TEXT DEFAULT '',
    location TEXT DEFAULT 'Warszawa',
    linkedin TEXT DEFAULT '',
    github TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    skills JSONB DEFAULT '[]'::jsonb,
    experience JSONB DEFAULT '[]'::jsonb,
    languages JSONB DEFAULT '[]'::jsonb,
    education JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. Create Saved Tailored CVs Table (Stores company-tailored CVs)
CREATE TABLE IF NOT EXISTS public.saved_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    target_title TEXT DEFAULT 'Software QA Engineer',
    lang TEXT DEFAULT 'pl',
    match_score INTEGER DEFAULT 100,
    profile_data JSONB NOT NULL,
    job_text TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. Enable Row Level Security (RLS) on both tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_cvs ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies for Profiles Table
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- 5. RLS Policies for Saved CVs Table
CREATE POLICY "Users can view their own saved CVs"
    ON public.saved_cvs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own saved CVs"
    ON public.saved_cvs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own saved CVs"
    ON public.saved_cvs FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own saved CVs"
    ON public.saved_cvs FOR DELETE
    USING (auth.uid() = user_id);

-- 6. Trigger to automatically create a profile entry when a user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (new.id, new.email, COALESCE(new.raw_user_meta_data->>'full_name', 'Michał Kosowski'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
