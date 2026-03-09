import { test, expect } from '@playwright/test';

test.describe('High Contrast Mode', () => {
    test.beforeEach(async ({ page, context }) => {
        // Clear localStorage before each test to ensure a clean state
        await context.clearCookies();
        await page.goto('/');
        await page.evaluate(() => localStorage.removeItem('highContrast'));
    });

    test('should display the high contrast toggle button in the header', async ({ page }) => {
        await test.step('Navigate to homepage', async () => {
            await page.goto('/');
        });

        await test.step('Verify toggle button is present and labelled correctly', async () => {
            const toggle = page.getByTestId('high-contrast-toggle');
            await expect(toggle).toHaveCount(1);
            await expect(toggle).toHaveAttribute('aria-pressed', 'false');
            await expect(toggle).toHaveAttribute('aria-label', 'Enable high contrast mode');
        });
    });

    test('should enable high contrast mode when the toggle is clicked', async ({ page }) => {
        await test.step('Navigate to homepage', async () => {
            await page.goto('/');
        });

        await test.step('Click the high contrast toggle', async () => {
            await page.getByTestId('high-contrast-toggle').click();
        });

        await test.step('Verify high contrast class is applied to <html>', async () => {
            await expect(page.locator('html')).toHaveClass(/high-contrast/);
        });

        await test.step('Verify toggle reflects active state', async () => {
            const toggle = page.getByTestId('high-contrast-toggle');
            await expect(toggle).toHaveAttribute('aria-pressed', 'true');
            await expect(toggle).toHaveAttribute('aria-label', 'Disable high contrast mode');
            await expect(toggle).toContainText('Normal Mode');
        });
    });

    test('should disable high contrast mode when the toggle is clicked a second time', async ({ page }) => {
        await test.step('Navigate to homepage', async () => {
            await page.goto('/');
        });

        await test.step('Enable then disable high contrast mode', async () => {
            const toggle = page.getByTestId('high-contrast-toggle');
            await toggle.click();
            await toggle.click();
        });

        await test.step('Verify high contrast class is removed from <html>', async () => {
            await expect(page.locator('html')).not.toHaveClass(/high-contrast/);
        });

        await test.step('Verify toggle reflects inactive state', async () => {
            const toggle = page.getByTestId('high-contrast-toggle');
            await expect(toggle).toHaveAttribute('aria-pressed', 'false');
            await expect(toggle).toContainText('High Contrast');
        });
    });

    test('should persist high contrast preference in localStorage', async ({ page }) => {
        await test.step('Navigate to homepage', async () => {
            await page.goto('/');
        });

        await test.step('Enable high contrast mode', async () => {
            await page.getByTestId('high-contrast-toggle').click();
        });

        await test.step('Verify preference is saved in localStorage', async () => {
            const stored = await page.evaluate(() => localStorage.getItem('highContrast'));
            expect(stored).toBe('true');
        });
    });

    test('should restore high contrast mode from localStorage on page reload', async ({ page }) => {
        await test.step('Enable high contrast mode', async () => {
            await page.goto('/');
            await page.getByTestId('high-contrast-toggle').click();
        });

        await test.step('Reload the page', async () => {
            await page.reload();
        });

        await test.step('Verify high contrast class is restored after reload', async () => {
            await expect(page.locator('html')).toHaveClass(/high-contrast/);
        });

        await test.step('Verify toggle still shows active state after reload', async () => {
            const toggle = page.getByTestId('high-contrast-toggle');
            await expect(toggle).toHaveAttribute('aria-pressed', 'true');
        });
    });
});
