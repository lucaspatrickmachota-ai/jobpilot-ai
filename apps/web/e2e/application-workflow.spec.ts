import { expect, test } from '@playwright/test';

async function register(page: import('@playwright/test').Page) {
  await page.goto('/');
  await page.getByLabel('Email').fill(`jobpilot-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`);
  await page.getByLabel('Password').fill('A-Strong-Test-Password-123');
  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
}

test('register and sign in to a real account', async ({ page }) => {
  await register(page);
  await expect(page.getByText('Signed in as')).toBeVisible();
});

test('create an application and persist a status change', async ({ page }) => {
  await register(page);
  await page.getByLabel('Company', { exact: true }).fill('Example Systems');
  await page.getByLabel('Position', { exact: true }).fill('Junior Python Engineer');
  await page.getByRole('button', { name: 'Save application' }).click();
  await expect(page.getByText('Junior Python Engineer')).toBeVisible();
  await page.getByLabel('Status').selectOption('APPLIED');
  await expect(page.getByText('Application status updated.')).toBeVisible();
  await expect(page.getByLabel('Status')).toHaveValue('APPLIED');
});

test('dashboard shows data returned by the API', async ({ page }) => {
  await register(page);
  await page.getByLabel('Company', { exact: true }).fill('Dashboard Systems');
  await page.getByLabel('Position', { exact: true }).fill('QA Engineer');
  await page.getByRole('button', { name: 'Save application' }).click();
  const applicationsCard = page.locator('article').filter({ hasText: 'Applications' }).first();
  await expect(applicationsCard).toContainText('1');
});
