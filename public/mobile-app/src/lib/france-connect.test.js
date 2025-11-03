import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { franceConnectLogout } from './france-connect.js'

describe('/france-connect.js', () => {
  describe('franceConnectLogout', () => {
    test('should call logout endpoint when click on France Connect logout button', async () => {
      // When
      await franceConnectLogout('fake-id-token')

      // Then
      expect(globalThis.window.location).equal(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out&post_logout_redirect_uri=https%3A%2F%2Fami-fc-proxy-dev.osc-fr1.scalingo.io%2F'
      )
    })
  })
})
