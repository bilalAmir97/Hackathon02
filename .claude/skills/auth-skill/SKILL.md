---
name: auth-skill
description: Implement secure authentication flows including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **Core Authentication Flows**
   - User signup with input validation
   - User signin with credential verification
   - Secure logout and session invalidation

2. **Password Security**
   - Hash passwords using industry-standard algorithms (bcrypt/argon2)
   - Never store plaintext passwords
   - Apply proper salting and cost factors

3. **Token-Based Auth**
   - Generate JWT access tokens
   - Use refresh tokens when required
   - Define token expiry and rotation strategy

4. **Better Auth Integration**
   - Configure Better Auth provider
   - Connect database adapters
   - Enable email/password and OAuth (if required)
   - Handle callbacks and session management

5. **Authorization & Middleware**
   - Protect private routes using auth middleware
   - Validate JWT tokens on each request
   - Enforce role-based or permission-based access

## Best Practices
- Use HTTPS only for auth endpoints
- Store secrets in environment variables
- Implement rate limiting on auth routes
- Return generic error messages for auth failures
- Follow OWASP authentication guidelines

## Example Structure
```ts
// signup.ts
import { hash } from "bcrypt";

export async function signup(email: string, password: string) {
  const hashedPassword = await hash(password, 12);
  // save user with hashedPassword
}

