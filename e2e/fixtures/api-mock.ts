import { Page, Route } from '@playwright/test';

interface MockResponseOptions {
  status?: number;
  body?: unknown;
  headers?: Record<string, string>;
  delay?: number;
}

export class ApiMocker {
  private activeRoutes: string[] = [];

  constructor(private page: Page) {}

  async mock(urlPattern: string, response: MockResponseOptions = {}): Promise<void> {
    this.activeRoutes.push(urlPattern);
    await this.page.route(urlPattern, async (route: Route) => {
      if (response.delay) {
        await new Promise((r) => setTimeout(r, response.delay));
      }
      await route.fulfill({
        status: response.status || 200,
        contentType: 'application/json',
        headers: { 'Access-Control-Allow-Origin': '*', ...response.headers },
        body: JSON.stringify(response.body ?? {}),
      });
    });
  }

  async mockGet(urlPattern: string, body: unknown, status = 200): Promise<void> {
    await this.mock(urlPattern, { body, status });
  }

  async mockError(urlPattern: string, status = 500, message = 'Internal Server Error'): Promise<void> {
    await this.mock(urlPattern, { status, body: { error: message } });
  }

  async mockSlow(urlPattern: string, body: unknown, delayMs = 3000): Promise<void> {
    await this.mock(urlPattern, { body, delay: delayMs });
  }

  async intercept(urlPattern: string): Promise<{ requests: Array<{ url: string; method: string; body: unknown }> }> {
    const requests: Array<{ url: string; method: string; body: unknown }> = [];
    this.activeRoutes.push(urlPattern);
    await this.page.route(urlPattern, async (route) => {
      const req = route.request();
      requests.push({ url: req.url(), method: req.method(), body: req.postDataJSON() });
      await route.continue();
    });
    return { requests };
  }

  async removeAll(): Promise<void> {
    for (const pattern of this.activeRoutes) {
      await this.page.unroute(pattern);
    }
    this.activeRoutes = [];
  }
}
