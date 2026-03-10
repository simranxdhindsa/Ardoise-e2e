import { Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

export interface A11yViolation {
  id: string;
  impact: string;
  description: string;
  nodes: number;
}

export class AccessibilityHelper {
  constructor(private page: Page) {}

  async audit(options?: { exclude?: string[]; include?: string[] }): Promise<A11yViolation[]> {
    let builder = new AxeBuilder({ page: this.page }).withTags([
      'wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa',
    ]);
    if (options?.exclude) {
      for (const selector of options.exclude) builder = builder.exclude(selector);
    }
    if (options?.include) {
      for (const selector of options.include) builder = builder.include(selector);
    }
    const results = await builder.analyze();
    return results.violations.map((v) => ({
      id: v.id,
      impact: v.impact || 'unknown',
      description: v.description,
      nodes: v.nodes.length,
    }));
  }

  async assertNoViolations(options?: {
    exclude?: string[];
    include?: string[];
    allowedIds?: string[];
  }): Promise<void> {
    const violations = await this.audit(options);
    const filtered = options?.allowedIds
      ? violations.filter((v) => !options.allowedIds!.includes(v.id))
      : violations;
    if (filtered.length > 0) {
      const report = filtered
        .map((v) => `  [${v.impact}] ${v.id}: ${v.description} (${v.nodes} elements)`)
        .join('\n');
      throw new Error(`Accessibility violations found:\n${report}`);
    }
  }
}
