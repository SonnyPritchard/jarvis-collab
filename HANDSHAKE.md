# Federation Handshake Config (Corey ↔ Sonny)

Use this file as the canonical bootstrap input for Phase 1 capability exchange.

## Corey peer (required)

- `corey_api_url`: `<SET_ME_PUBLIC_URL>`
- `corey_federation_api_key`: `<SET_ME_API_KEY>`
- `corey_hmac_secret`: `<SET_ME_SHARED_SECRET>`
- `corey_instance_id`: `corey-jarvis`
- `corey_capabilities_path`: `/federation/capabilities`
- `corey_negotiate_path`: `/federation/negotiate`
- `corey_result_path`: `/federation/result`
- `corey_progress_path`: `/federation/progress`

## Sonny peer (current)

- `sonny_api_url`: `https://d437-109-155-119-133.ngrok-free.app`
- `sonny_instance_id`: `sonny-jarvis`
- `sonny_capabilities_path`: `/federation/capabilities`
- `sonny_negotiate_path`: `/federation/negotiate`
- `sonny_result_path`: `/federation/result`
- `sonny_progress_path`: `/federation/progress`

## Handshake sequence

1. Corey → Sonny: `GET /federation/capabilities`
2. Sonny → Corey: `GET /federation/capabilities`
3. Corey → Sonny: `POST /federation/negotiate`
4. Sonny → Corey: `POST /federation/result`
5. Both sides post one `POST /federation/progress` event
6. Verify timeline retrieval with `GET /federation/progress/{task_id}`

## Security notes

- Rotate any API key shared in chat immediately after tests.
- Keep `federation_api_key` and `hmac_secret` in env/secret store, not in git for production.
- Enforce timestamp drift <=60s and nonce replay checks.
