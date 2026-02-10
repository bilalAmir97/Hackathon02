'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loading } = useAuth();

  useEffect(() => {
    // Get the redirect URL from query parameters
    const redirect = searchParams.get('redirect') || '/dashboard';

    // Wait for auth to initialize and redirect to the appropriate page
    if (!loading) {
      router.push(redirect);
    }
  }, [loading, router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-300">Completing authentication...</p>
      </div>
    </div>
  );
}