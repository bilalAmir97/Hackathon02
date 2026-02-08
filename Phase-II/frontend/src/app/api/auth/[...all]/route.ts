/**
 * Better Auth API Route Handler
 *
 * Handles all authentication routes via Better Auth.
 * Catch-all route: /api/auth/*
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Export GET and POST handlers for Next.js App Router
export const { GET, POST } = toNextJsHandler(auth);
