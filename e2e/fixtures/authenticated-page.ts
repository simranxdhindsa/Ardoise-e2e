import { Page } from '@playwright/test';

export class AuthenticatedPage {
  constructor(readonly page: Page) {}

  async assertAuthenticated(): Promise<void> {
    const cookies = await this.page.context().cookies();
    const hasToken = cookies.some((c) => c.name === 'accessToken');
    if (!hasToken) {
      throw new Error('Not authenticated: accessToken cookie missing');
    }
  }

  async clearAuth(): Promise<void> {
    await this.page.context().clearCookies();
    await this.page.evaluate(() => localStorage.clear());
  }

  async setCookie(name: string, value: string, domain?: string): Promise<void> {
    const url = this.page.url();
    const hostname = domain || new URL(url).hostname;
    await this.page.context().addCookies([
      {
        name,
        value,
        domain: hostname,
        path: '/',
      },
    ]);
  }
}
