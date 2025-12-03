import { expect, test } from '@playwright/test'

test('home page has FranceConnect button when user is not FranceConnected', async ({
  page,
}) => {
  await page.route('*/**/check-auth', async (route) => {
    await route.fulfill({ status: 401 })
  })
  await page.goto('/')
  await expect(page.locator('#fr-connect-button')).toBeVisible()
})
