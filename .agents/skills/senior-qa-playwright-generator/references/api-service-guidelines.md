# API Service Client Guidelines

## Purpose
Encapsulate all HTTP requests into domain-focused client classes. This guarantees DRY (Don't Repeat Yourself) API interactions, type safety, and painless endpoint updates.

---

## Architecture Standards

### 1. Client Specialization
Split API communication by domain:
- `AuthClient`: Session, registration, login, token refresh.
- `ProfileClient`: User profile CRUD.
- `TailorClient`: CV tailoring, job analysis, prompt refinement, PDF export.
- `AdminClient`: Administrative endpoints like test cleanup.

### 2. Implementation Pattern
```typescript
import { APIRequestContext, APIResponse } from "@playwright/test";

export class AuthClient {
  constructor(private readonly request: APIRequestContext) {}

  async register(email: string, password: string): Promise<APIResponse> {
    return this.request.post("/api/auth/register", {
      data: { email, password },
    });
  }

  async login(email: string, password: string): Promise<{ response: APIResponse; token: string }> {
    const response = await this.request.post("/api/auth/login", {
      data: { email, password },
    });
    let token = "";
    if (response.ok()) {
      const body = await response.json();
      token = body.token || body.access_token || "";
    }
    return { response, token };
  }
}
```

### 3. Authenticated Requests
Pass JWT bearer tokens cleanly in request headers:
```typescript
export class ProfileClient {
  constructor(private readonly request: APIRequestContext) {}

  async getProfile(token: string): Promise<APIResponse> {
    return this.request.get("/api/profile", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }
}
```
