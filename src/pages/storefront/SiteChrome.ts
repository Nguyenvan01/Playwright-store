import { Locator, Page } from '@playwright/test';

/** Phần dùng chung cuối trang: khối "Đăng ký nhận tin" (components/Newsletter.jsx) và Footer. */
export class SiteChrome {
  readonly newsletter: Locator;
  readonly newsletterEmail: Locator;
  readonly newsletterSubmit: Locator;
  readonly newsletterThanks: Locator;
  readonly footer: Locator;
  readonly footerCopyright: Locator;
  /** Vùng nội dung chính của trang (bỏ header/footer). */
  readonly main: Locator;
  /** Toàn bộ chữ trong <body> (dùng cho trang trắng / route không tồn tại). */
  readonly body: Locator;

  constructor(readonly page: Page) {
    this.newsletter = page
      .locator('section')
      .filter({ has: page.getByRole('heading', { name: 'Đăng ký nhận tin', exact: true }) });
    this.newsletterEmail = this.newsletter.getByPlaceholder('Nhập email của bạn');
    this.newsletterSubmit = this.newsletter.getByRole('button', { name: 'Đăng ký' });
    this.newsletterThanks = this.newsletter.getByText('Cảm ơn bạn đã đăng ký!');
    this.footer = page.locator('footer');
    this.footerCopyright = this.footer.getByText('© 2026 Đạt Hoàng. All rights reserved.');
    this.main = page.locator('main');
    this.body = page.locator('body');
  }

  footerHeading(name: string): Locator {
    return this.footer.getByRole('heading', { name, exact: true });
  }

  footerLink(name: string): Locator {
    return this.footer.getByRole('link', { name, exact: true });
  }

  footerLinkTo(href: string): Locator {
    return this.footer.locator(`a[href="${href}"]`);
  }

  mainHeadings(level: 1 | 2 | 3 | 4): Locator {
    return this.main.locator(`h${level}`);
  }
}
