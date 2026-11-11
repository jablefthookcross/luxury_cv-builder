import { test as baseTest, expect } from "@playwright/test";
import { ApiClient } from "../services/api.client";
import { buildQaUser, QaUser } from "../data/builders";
import { AuthSession } from "../services/auth.client";

export interface CustomFixtures {
  apiClient: ApiClient;
  testUser: QaUser;
  authSession: AuthSession;
  cleanup: void;
}

export const test = baseTest.extend<CustomFixtures>({
  apiClient: async ({ request }, use) => {
    const client = new ApiClient(request);
    await use(client);
  },

  testUser: async ({}, use) => {
    const user = buildQaUser();
    await use(user);
  },

  authSession: async ({ apiClient, testUser }, use) => {
    const session = await apiClient.auth.registerAndLogin(testUser);
    await use(session);
  },

  cleanup: [
    async ({ apiClient }, use) => {
      // Setup - do nothing prior to test
      await use();
      // Teardown - purge test users, preserving the real owner account
      try {
        await apiClient.admin.cleanup("vitaecraft-nuclear-secret-2026", true);
      } catch (err) {
        console.warn("[Teardown warning] Automated test cleanup failed:", err);
      }
    },
    { auto: false },
  ],
});

export { expect };
