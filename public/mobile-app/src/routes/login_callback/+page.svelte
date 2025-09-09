<script lang="ts">
import { PUBLIC_API_URL } from '$env/static/public'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'

onMount(async () => {
  // We've been redirected to this page by FC after being logged out.
  globalState.isLoggedOut = true
  // TODO:
  // - parse parameters to get all the user tokens from FC
  // - store needed tokens in the local session
  goto('/')
})

//   # FC - Step 8
//   httpx.get(f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_JWKS_ENDPOINT}")
//   # FC - Step 11
//   access_token = response_token_data["access_token"]
//   id_token = response_token_data["id_token"]
//   userinfo_endpoint_headers = {"Authorization": f"Bearer {access_token}"}
//   response = httpx.get(
//       f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_USERINFO_ENDPOINT}",
//       headers=userinfo_endpoint_headers,
//   )
//   userinfo_jws = response.text
//   userinfo = jwt.decode(userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"])
//   # FC - Step 16.1
//   request.session["userinfo"] = userinfo
//   request.session["id_token"] = id_token
//   return Redirect("/")
</script>
