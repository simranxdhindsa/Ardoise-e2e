import { test as base, expect } from '@playwright/test';
import { AuthenticatedPage } from './authenticated-page';
import { ApiMocker } from './api-mock';
import { AccessibilityHelper } from './accessibility';

type CustomFixtures = {
  authenticatedPage: AuthenticatedPage;
  apiMocker: ApiMocker;
  a11y: AccessibilityHelper;
};

export const test = base.extend<CustomFixtures>({
  authenticatedPage: async ({ page }, use) => {
    await use(new AuthenticatedPage(page));
  },
  apiMocker: async ({ page }, use) => {
    const mocker = new ApiMocker(page);
    await use(mocker);
    await mocker.removeAll();
  },
  a11y: async ({ page }, use) => {
    await use(new AccessibilityHelper(page));
  },
});

export { expect };
