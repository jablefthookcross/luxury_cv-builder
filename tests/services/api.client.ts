import { APIRequestContext } from "@playwright/test";
import { AdminClient } from "./admin.client";
import { AuthClient } from "./auth.client";
import { ProfileClient } from "./profile.client";
import { TailorClient } from "./tailor.client";

export class ApiClient {
  public readonly admin: AdminClient;
  public readonly auth: AuthClient;
  public readonly profile: ProfileClient;
  public readonly tailor: TailorClient;

  constructor(public readonly request: APIRequestContext) {
    this.admin = new AdminClient(request);
    this.auth = new AuthClient(request);
    this.profile = new ProfileClient(request);
    this.tailor = new TailorClient(request);
  }
}
