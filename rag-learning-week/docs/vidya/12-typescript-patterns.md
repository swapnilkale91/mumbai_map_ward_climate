# TypeScript Patterns for Backend Services

TypeScript's type system catches entire classes of bugs at compile time. These patterns appear consistently in production Node.js services.

## Discriminated Unions
Model domain states explicitly with a shared discriminant field:
```ts
type Result<T> =
  | { ok: true;  value: T }
  | { ok: false; error: string };
```
Exhaustiveness checking then ensures every branch is handled.

## Zod for Runtime Validation
TypeScript types are erased at runtime. Zod validates external data (API responses, env vars, DB rows) at runtime and infers TypeScript types from schemas:
```ts
const Env = z.object({ DATABASE_URL: z.string().url(), ANTHROPIC_API_KEY: z.string() });
const env = Env.parse(process.env);
```

## Branded Types
Prevent mixing up structurally identical primitive types:
```ts
type UserId   = string & { readonly _brand: "UserId" };
type SessionId = string & { readonly _brand: "SessionId" };
```
A function accepting `UserId` will reject a plain `string`.

## async/await Error Handling
Avoid uncaught promise rejections. Either use try/catch at call sites or a Result-typed wrapper. Never swallow errors silently.

## Module Structure
- Keep each module's public API small. Export only what callers need.
- Prefer named exports over default exports for better refactoring and barrel imports.

## Path Aliases
Configure `paths` in tsconfig.json and `moduleNameMapper` in Jest to use `@/` instead of `../../` relative paths.

## Strict Mode
Always enable `strict: true`. The most valuable sub-flags: `strictNullChecks`, `noUncheckedIndexedAccess`, `noImplicitAny`.
