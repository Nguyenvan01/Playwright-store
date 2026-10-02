import { defineConfig, devices } from '@playwright/test';
import { env } from './src/config/env';

export default defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  fullyParallel: true,
  forbidOnly: env.isCI,
  // Môi trường remote (Vercel serverless) có thể cold start -> cho retry 1 lần
  retries: env.isCI ? 2 : env.isLocal ? 0 : 1,
  workers: env.isCI ? 2 : undefined,
  timeout: env.isLocal ? 30_000 : 45_000,
  expect: { timeout: 7_000 },

  reporter: [
    ['list'],
    ['html', { outputFolder: `reports/${env.name}/html`, open: 'never' }],
    ['junit', { outputFile: `reports/${env.name}/junit.xml` }],
    ['json', { outputFile: `reports/${env.name}/results.json` }],
  ],

  use: {
    baseURL: env.baseURL,
    locale: 'vi-VN',
    timezoneId: 'Asia/Ho_Chi_Minh',
    actionTimeout: 10_000,
    navigationTimeout: 20_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // SLOW_MO=500 -> mỗi thao tác chậm 500ms, dễ quan sát khi chạy --headed
    launchOptions: { slowMo: Number(process.env.SLOW_MO) || 0 },
  },

  // Thứ tự quan trọng: UI mode (--ui) mặc định chỉ bật project ĐẦU TIÊN -> để chromium lên đầu.
  projects: [
    // UI test trên Desktop Chrome
    {
      name: 'chromium',
      testDir: './tests/e2e',
      testIgnore: /mobile\//,
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
      dependencies: ['setup'],
    },

    // UI test trên mobile (chỉ thư mục tests/e2e/mobile)
    {
      name: 'mobile',
      testDir: './tests/e2e/mobile',
      use: { ...devices['Pixel 7'] },
      dependencies: ['setup'],
    },

    // Test REST API của backend Express (không cần browser)
    { name: 'api', testDir: './tests/api' },

    // Tạo storageState cho customer/admin trước khi chạy UI test
    { name: 'setup', testDir: './tests/setup', testMatch: /.*\.setup\.ts/ },
  ],

  webServer: env.startServers
    ? [
        {
          command: `npm --prefix "${env.appDir}/backend" run dev`,
          url: `${env.apiURL}/health`,
          reuseExistingServer: true,
          timeout: 120_000,
        },
        {
          command: `npm --prefix "${env.appDir}/frontend" run dev`,
          url: env.baseURL,
          reuseExistingServer: true,
          timeout: 120_000,
        },
      ]
    : undefined,
});
