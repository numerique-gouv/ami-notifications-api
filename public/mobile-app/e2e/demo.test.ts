import { expect, test } from '@playwright/test'

test('home page has FranceConnect button when user is not FranceConnected', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.locator('#fr-connect-button')).toBeVisible()
})
