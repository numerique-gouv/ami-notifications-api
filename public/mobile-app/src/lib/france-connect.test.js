import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { franceConnectLogout } from './france-connect.js'

describe('/france-connect.js', () => {
  describe('franceConnectLogout', () => {
    test('should call logout endpoint when click on France Connect logout button', async () => {
      // Given
      globalThis.window = {
        location: {
          href: 'fake-link',
        },
      }
      globalThis.localStorage = {
        getItem: vi.fn().mockImplementation(() => {
          return 'fake-id-token'
        }),
      }
      vi.mock('$env/static/public', () => {
        return {
          PUBLIC_APP_URL: 'https://localhost:5173',
          PUBLIC_FC_BASE_URL: 'https://fcp-low.sbx.dev-franceconnect.fr',
          PUBLIC_FC_LOGOUT_ENDPOINT: '/api/v2/session/end',
        }
      })

      // When
      await franceConnectLogout()

      // Then
      expect(globalThis.window.location).equal(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=not-implemented-yet-and-has-more-than-32-chars&post_logout_redirect_uri=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out'
      )
    })
  })
})
