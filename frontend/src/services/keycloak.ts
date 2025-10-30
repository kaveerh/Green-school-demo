import Keycloak from 'keycloak-js'

/**
 * Keycloak instance for authentication
 */
let keycloakInstance: Keycloak | null = null

/**
 * Initialize Keycloak
 */
export function initKeycloak(): Keycloak {
  if (!keycloakInstance) {
    keycloakInstance = new Keycloak({
      url: import.meta.env.VITE_KEYCLOAK_URL,
      realm: import.meta.env.VITE_KEYCLOAK_REALM,
      clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID
    })
  }
  return keycloakInstance
}

/**
 * Get the current Keycloak instance
 */
export function getKeycloak(): Keycloak | null {
  return keycloakInstance
}

/**
 * Initialize Keycloak and authenticate
 */
export async function initializeAuth(): Promise<boolean> {
  const keycloak = initKeycloak()

  try {
    console.log('🔑 Keycloak.init() starting...')
    console.log('🔑 Current URL:', window.location.href)

    // Initialize without silent SSO check to avoid CSP issues
    const authenticated = await keycloak.init({
      pkceMethod: 'S256',
      checkLoginIframe: false,
      // Enable token refresh
      enableLogging: true
    })

    console.log('🔑 Keycloak.init() completed')
    console.log('🔑 Authenticated:', authenticated)
    console.log('🔑 Token present:', !!keycloak.token)
    console.log('🔑 Token parsed:', !!keycloak.tokenParsed)

    if (authenticated) {
      console.log('✅ User is authenticated')
      console.log('✅ Token:', keycloak.token?.substring(0, 50) + '...')
      console.log('✅ Token parsed:', keycloak.tokenParsed)

      // Setup token refresh
      setupTokenRefresh(keycloak)
    } else {
      console.log('❌ User is not authenticated')
      console.log('❌ Keycloak object:', {
        authenticated: keycloak.authenticated,
        token: keycloak.token ? 'present' : 'missing',
        tokenParsed: keycloak.tokenParsed ? 'present' : 'missing'
      })
    }

    return authenticated
  } catch (error) {
    console.error('❌ Failed to initialize Keycloak:', error)
    console.error('❌ Error details:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    })
    return false
  }
}

/**
 * Setup automatic token refresh
 */
function setupTokenRefresh(keycloak: Keycloak) {
  // Update token every 60 seconds
  setInterval(() => {
    keycloak
      .updateToken(70)
      .then((refreshed) => {
        if (refreshed) {
          console.log('Token was successfully refreshed')
        }
      })
      .catch((error) => {
        console.error('Failed to refresh token:', error)
        // Redirect to login if token refresh fails
        keycloak.login()
      })
  }, 60000)
}

/**
 * Login with Keycloak
 */
export function login(): void {
  const keycloak = getKeycloak()
  if (keycloak) {
    console.log('🔐 Initiating Keycloak login...')
    console.log('🔐 Redirect URI:', window.location.origin + '/dashboard')
    keycloak.login({
      redirectUri: window.location.origin + '/dashboard'
    })
  } else {
    console.error('❌ Keycloak instance not available for login')
  }
}

/**
 * Logout from Keycloak
 */
export function logout(): void {
  const keycloak = getKeycloak()
  if (keycloak) {
    const redirectUri = window.location.origin
    console.log('🚪 Logging out from Keycloak...')
    console.log('🚪 Logout redirect URI:', redirectUri)
    console.log('🚪 Current authenticated:', keycloak.authenticated)

    keycloak.logout({
      redirectUri: redirectUri
    })
  } else {
    console.error('❌ Cannot logout: Keycloak instance not available')
  }
}

/**
 * Get user profile from Keycloak token
 */
export function getUserProfile() {
  const keycloak = getKeycloak()
  if (!keycloak || !keycloak.tokenParsed) {
    return null
  }

  const token = keycloak.tokenParsed as any

  return {
    id: token.sub || '',
    email: token.email || '',
    firstName: token.given_name || '',
    lastName: token.family_name || '',
    fullName: token.name || '',
    username: token.preferred_username || '',
    roles: token.realm_access?.roles || [],
    persona: getUserPersona(token.realm_access?.roles || [])
  }
}

/**
 * Determine user persona from Keycloak roles
 */
function getUserPersona(roles: string[]): string {
  if (roles.includes('administrator')) return 'administrator'
  if (roles.includes('teacher')) return 'teacher'
  if (roles.includes('parent')) return 'parent'
  if (roles.includes('student')) return 'student'
  if (roles.includes('vendor')) return 'vendor'
  return 'user'
}

/**
 * Check if user has a specific role
 */
export function hasRole(role: string): boolean {
  const keycloak = getKeycloak()
  if (!keycloak || !keycloak.tokenParsed) {
    return false
  }

  const roles = (keycloak.tokenParsed as any).realm_access?.roles || []
  return roles.includes(role)
}

/**
 * Check if user has any of the specified roles
 */
export function hasAnyRole(roles: string[]): boolean {
  return roles.some((role) => hasRole(role))
}

/**
 * Get the current access token
 */
export function getToken(): string | undefined {
  const keycloak = getKeycloak()
  return keycloak?.token
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const keycloak = getKeycloak()
  return keycloak?.authenticated || false
}
