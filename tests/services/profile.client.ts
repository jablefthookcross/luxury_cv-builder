import { APIRequestContext, APIResponse } from "@playwright/test";

export class ProfileClient {
  constructor(private readonly request: APIRequestContext) {}

  private getHeaders(token?: string) {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async getProfile(token?: string): Promise<APIResponse> {
    return this.request.get("/api/profile", {
      headers: this.getHeaders(token),
    });
  }

  async saveProfile(profileData: any, token?: string): Promise<APIResponse> {
    return this.request.post("/api/profile", {
      headers: this.getHeaders(token),
      data: profileData,
    });
  }

  async resetProfile(token?: string): Promise<APIResponse> {
    return this.request.post("/api/profile/reset", {
      headers: this.getHeaders(token),
    });
  }

  async deleteProfile(token?: string): Promise<APIResponse> {
    return this.request.post("/api/profile/delete", {
      headers: this.getHeaders(token),
    });
  }

  async getSettings(): Promise<APIResponse> {
    return this.request.get("/api/settings");
  }
}
