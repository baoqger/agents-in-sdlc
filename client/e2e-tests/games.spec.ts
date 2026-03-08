import { test, expect, type Response } from '@playwright/test';

test.describe('Game Listing and Navigation', () => {
  test('should display games with titles on index page', async ({ page }) => {
    await test.step('Navigate to homepage', async () => {
      await page.goto('/');
    });

    await test.step('Verify games grid is visible', async () => {
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Verify game cards are displayed', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
      expect(await gameCards.count()).toBeGreaterThan(0);
    });

    await test.step('Verify game cards have titles with content', async () => {
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first().getByTestId('game-title')).toBeVisible();
      await expect(gameCards.first().getByTestId('game-title')).not.toBeEmpty();
    });
  });

  test('should navigate to correct game details page when clicking on a game', async ({ page }) => {
    let gameId: string | null;
    let gameTitle: string | null;

    await test.step('Navigate to homepage and wait for games to load', async () => {
      await page.goto('/');
      const gamesGrid = page.getByTestId('games-grid');
      await expect(gamesGrid).toBeVisible();
    });

    await test.step('Get first game information and click it', async () => {
      const firstGameCard = page.getByTestId('game-card').first();
      gameId = await firstGameCard.getAttribute('data-game-id');
      gameTitle = await firstGameCard.getAttribute('data-game-title');
      await firstGameCard.click();
    });

    await test.step('Verify navigation to game details page', async () => {
      await expect(page).toHaveURL(`/game/${gameId}`);
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify game title matches clicked game', async () => {
      if (gameTitle) {
        await expect(page.getByTestId('game-details-title')).toHaveText(gameTitle);
      }
    });
  });

  test('should display game details with all required information', async ({ page }) => {
    await test.step('Navigate to specific game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify game title is displayed', async () => {
      const gameTitle = page.getByTestId('game-details-title');
      await expect(gameTitle).toBeVisible();
      await expect(gameTitle).not.toBeEmpty();
    });

    await test.step('Verify game description is displayed', async () => {
      const gameDescription = page.getByTestId('game-details-description');
      await expect(gameDescription).toBeVisible();
      await expect(gameDescription).not.toBeEmpty();
    });

    await test.step('Verify publisher or category information is present', async () => {
      const publisherExists = await page.getByTestId('game-details-publisher').isVisible();
      const categoryExists = await page.getByTestId('game-details-category').isVisible();
      expect(publisherExists || categoryExists).toBeTruthy();

      if (publisherExists) {
        await expect(page.getByTestId('game-details-publisher')).not.toBeEmpty();
      }

      if (categoryExists) {
        await expect(page.getByTestId('game-details-category')).not.toBeEmpty();
      }
    });
  });

  test('should display a button to back the game', async ({ page }) => {
    await test.step('Navigate to game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Verify back game button is visible and enabled', async () => {
      const backButton = page.getByTestId('back-game-button');
      await expect(backButton).toBeVisible();
      await expect(backButton).toContainText('Support This Game');
      await expect(backButton).toBeEnabled();
    });
  });

  test('should be able to navigate back to home from game details', async ({ page }) => {
    await test.step('Navigate to game details page', async () => {
      await page.goto('/game/1');
      await expect(page.getByTestId('game-details')).toBeVisible();
    });

    await test.step('Click back to all games link', async () => {
      const backLink = page.getByRole('link', { name: /back to all games/i });
      await expect(backLink).toBeVisible();
      await backLink.click();
    });

    await test.step('Verify navigation back to homepage', async () => {
      await expect(page).toHaveURL('/');
      await expect(page.getByTestId('games-grid')).toBeVisible();
    });
  });

  test('should handle navigation to non-existent game gracefully', async ({ page }) => {
    let response: Response | null;

    await test.step('Navigate to non-existent game', async () => {
      response = await page.goto('/game/99999');
    });

    await test.step('Verify page handles error gracefully', async () => {
      expect(response?.status()).toBeLessThan(500);
      await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
    });
  });
});

test.describe('Game Filtering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display filter controls on the homepage', async ({ page }) => {
    await test.step('Verify filter section is visible', async () => {
      await expect(page.getByText('Filter Games')).toBeVisible();
    });

    await test.step('Verify category filter is present', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await expect(categoryFilter).toBeVisible();
      await expect(categoryFilter).toBeEnabled();
    });

    await test.step('Verify publisher filter is present', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      await expect(publisherFilter).toBeVisible();
      await expect(publisherFilter).toBeEnabled();
    });

    await test.step('Verify clear filters button is present', async () => {
      const clearButton = page.getByTestId('clear-filters');
      await expect(clearButton).toBeVisible();
      await expect(clearButton).toBeEnabled();
    });
  });

  test('should filter games by category', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      await expect(page.getByTestId('games-grid')).toBeVisible();
    });

    await test.step('Select a category from the filter', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await categoryFilter.selectOption({ index: 1 });
    });

    await test.step('Verify games are filtered', async () => {
      // Wait for the filtered results to load
      await page.waitForLoadState('networkidle');
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
    });
  });

  test('should filter games by publisher', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      await expect(page.getByTestId('games-grid')).toBeVisible();
    });

    await test.step('Select a publisher from the filter', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      await publisherFilter.selectOption({ index: 1 });
    });

    await test.step('Verify games are filtered', async () => {
      // Wait for the filtered results to load
      await page.waitForLoadState('networkidle');
      const gameCards = page.getByTestId('game-card');
      await expect(gameCards.first()).toBeVisible();
    });
  });

  test('should filter games by both category and publisher', async ({ page }) => {
    await test.step('Wait for games to load', async () => {
      await expect(page.getByTestId('games-grid')).toBeVisible();
    });

    await test.step('Select a category from the filter', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await categoryFilter.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    });

    await test.step('Select a publisher from the filter', async () => {
      const publisherFilter = page.getByTestId('publisher-filter');
      await publisherFilter.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    });

    await test.step('Verify filtered results are displayed', async () => {
      // The games grid should still be visible even if there are no results
      await expect(page.getByTestId('games-grid').or(page.getByText('No games available'))).toBeVisible();
    });
  });

  test('should clear all filters when clicking clear filters button', async ({ page }) => {
    let initialGameCount: number;

    await test.step('Wait for games to load and get initial count', async () => {
      await expect(page.getByTestId('games-grid')).toBeVisible();
      initialGameCount = await page.getByTestId('game-card').count();
    });

    await test.step('Apply a category filter', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      await categoryFilter.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    });

    await test.step('Click clear filters button', async () => {
      const clearButton = page.getByTestId('clear-filters');
      await clearButton.click();
      await page.waitForLoadState('networkidle');
    });

    await test.step('Verify all games are displayed again', async () => {
      const gameCards = page.getByTestId('game-card');
      expect(await gameCards.count()).toBe(initialGameCount);
    });

    await test.step('Verify filters are reset to default', async () => {
      const categoryFilter = page.getByTestId('category-filter');
      const publisherFilter = page.getByTestId('publisher-filter');
      await expect(categoryFilter).toHaveValue('');
      await expect(publisherFilter).toHaveValue('');
    });
  });
});
