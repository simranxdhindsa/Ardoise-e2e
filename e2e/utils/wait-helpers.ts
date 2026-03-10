import { Page, expect } from '@playwright/test';

export const WaitHelpers = {
  async forLoadingComplete(page: Page, timeout = 15_000): Promise<void> {
    const overlay = page.locator('.mantine-LoadingOverlay-root');
    const count = await overlay.count();
    if (count > 0) {
      await overlay.first().waitFor({ state: 'hidden', timeout });
    }
  },

  async forQueriesSettled(page: Page, timeout = 10_000): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  },

  async forNotification(page: Page, text?: string): Promise<void> {
    const notif = text
      ? page.locator('.mantine-Notification-root').filter({ hasText: text })
      : page.locator('.mantine-Notification-root');
    await notif.first().waitFor({ state: 'visible', timeout: 10_000 });
  },

  async forUrlContaining(page: Page, path: string): Promise<void> {
    await expect(page).toHaveURL(new RegExp(path));
  },

  async forApiResponse(page: Page, urlPattern: string, timeout = 10_000): Promise<void> {
    await page.waitForResponse(
      (response) => response.url().includes(urlPattern) && response.status() === 200,
      { timeout }
    );
  },
};
