import { APIRequestContext, APIResponse } from "@playwright/test";
import { QaUser } from "../data/builders";

export interface AuthSession {
  token: string;
  user: {
    id: string;
    email: string;
    full_name?: string;
  };
}

export class AuthClient {
  constructor(private readonly request: APIRequestContext) {}

  async register(user: QaUser): Promise<APIResponse> {
    return this.request.post("/api/auth/register", {
      data: {
        email: user.email,
        password: user.password,
        full_name: user.fullName,
      },
    });
  }

  async login(credentials: { email: string; password: string }): Promise<APIResponse> {
    return this.request.post("/api/auth/login", {
      data: {
        email: credentials.email,
        password: credentials.password,
      },
    });
  }

  async registerAndLogin(user: QaUser): Promise<AuthSession> {
    const regRes = await this.register(user);
    const regData = await regRes.json();

    if (regData.status !== "success") {
      throw new Error(`Registration failed for ${user.email}: ${JSON.stringify(regData)}`);
    }

    const loginRes = await this.login(user);
    const loginData = await loginRes.json();

    if (loginData.status !== "success" || !loginData.access_token) {
      throw new Error(`Login failed for ${user.email}: ${JSON.stringify(loginData)}`);
    }

    return {
      token: loginData.access_token,
      user: loginData.user,
    };
  }

  async status(): Promise<APIResponse> {
    return this.request.get("/api/auth/status");
  }
}
