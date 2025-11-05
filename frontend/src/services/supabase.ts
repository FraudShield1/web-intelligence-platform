import { createClient } from '@supabase/supabase-js';

const url =
  (process.env.REACT_APP_SUPABASE_URL as string) ||
  (process.env.NEXT_PUBLIC_SUPABASE_URL as string) ||
  '';

const anonKey =
  (process.env.REACT_APP_SUPABASE_ANON_KEY as string) ||
  (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string) ||
  '';

if (!url || !anonKey) {
  // eslint-disable-next-line no-console
  console.warn('Supabase URL/ANON KEY not set; supabase client will be disabled.');
}

export const supabase = url && anonKey ? createClient(url, anonKey) : (null as any);
