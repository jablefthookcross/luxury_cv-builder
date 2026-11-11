import { APIRequestContext, APIResponse } from "@playwright/test";

export class AdminClient {
  constructor(private readonly request: APIRequestContext) {}

  async cleanup(
    secret: string = "vitaecraft-nuclear-secret-2026",
    preserveOwner: boolean = true
  ): Promise<APIResponse> {
    return this.request.post("/admin/cleanup", {
      headers: {
        "x-admin-secret": secret,
        "Content-Type": "application/json",
      },
      data: {
        preserve_owner: preserveOwner,
      },
    });
  }

  async cleanupWithoutSecret(): Promise<APIResponse> {
    return this.request.post("/admin/cleanup", {
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
}
