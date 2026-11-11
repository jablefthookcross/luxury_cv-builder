import { defineConfig, devices } from "@playwright/test";
import dotenv from "dotenv";

dotenv.config();

const isCI = Boolean(process.env.CI);
const baseURL = process.env.BASE_URL || "http://127.0.0.1:5000";
const flaskCommand =
  process.env.FLASK_COMMAND ||
  (process.env.CI ? "python app.py --port 5000" : "./venv/bin/python app.py --port 5000");

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? 2 : 1,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-report" }],
    ["allure-playwright", { outputFolder: "allure-results" }],
  ],
  webServer: {
    command: flaskCommand,
    url: "http://127.0.0.1:5000/api/auth/status",
    reuseExistingServer: !isCI,
    timeout: 120_000,
  },
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "api",
      testDir: "./tests/api",
      use: {
        baseURL,
      },
    },
    {
      name: "chromium",
      testDir: "./tests/e2e",
      use: {
        ...devices["Desktop Chrome"],
        baseURL,
        viewport: { width: 1440, height: 900 },
      },
    },
  ],
});
