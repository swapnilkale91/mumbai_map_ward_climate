# REST API Design

A well-designed API is predictable, consistent, and easy to consume. These principles apply to any JSON over HTTP service.

## Resource-Oriented URLs
URLs identify resources, not actions:
- `GET /users/:id` — fetch a user
- `POST /users` — create a user
- `PATCH /users/:id` — partial update
- `DELETE /users/:id` — delete a user

Avoid verbs in paths: `/getUser` is an anti-pattern.

## HTTP Status Codes
Use them semantically:
- 200 OK, 201 Created, 204 No Content
- 400 Bad Request (client validation error), 401 Unauthorised, 403 Forbidden, 404 Not Found, 409 Conflict
- 500 Internal Server Error (never expose stack traces)

## Request Validation
Validate inputs at the API boundary. Return 400 with a structured error body:
```json
{ "error": "VALIDATION_ERROR", "fields": { "email": "must be a valid email" } }
```

## Pagination
Use cursor-based pagination for large datasets:
```
GET /documents?after=cursor_xyz&limit=50
```
Offset-based pagination drifts when rows are inserted/deleted mid-session.

## Versioning
Prefix routes with `/v1/` to allow breaking changes without disrupting existing clients. Never version via a query parameter or header if you can avoid it.

## Idempotency
GET, PUT, DELETE, and PATCH (if correctly implemented) must be idempotent. POST is not idempotent by default; use idempotency keys for critical operations (payments, emails).

## Rate Limiting
Return 429 Too Many Requests with a `Retry-After` header. Apply limits per user/IP, not globally.

## OpenAPI / Swagger
Document your API with an OpenAPI 3.x spec. Auto-generate client SDKs and validation middleware from it.
