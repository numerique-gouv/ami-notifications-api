import { expect, test } from '@playwright/test'

test('home page has france connect button when user is not france connected', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.locator('#fr-connect-button')).toBeVisible()
})
