import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  abstract get path(): string;

  async goto(): Promise<void> {
    await this.page.goto(this.path);
    await this.waitForPageLoad();
  }

  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  get notification(): Locator {
    return this.page.locator('.mantine-Notification-root');
  }

  get loadingOverlay(): Locator {
    return this.page.locator('.mantine-LoadingOverlay-root');
  }

  async waitForLoadingToDisappear(): Promise<void> {
    const count = await this.loadingOverlay.count();
    if (count > 0) {
      await this.loadingOverlay.first().waitFor({ state: 'hidden', timeout: 15_000 });
    }
  }

  async assertUrl(pattern: string | RegExp): Promise<void> {
    await expect(this.page).toHaveURL(pattern);
  }

  async visualCheck(name: string): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveScreenshot(`${name}.png`, { fullPage: true });
  }
}
