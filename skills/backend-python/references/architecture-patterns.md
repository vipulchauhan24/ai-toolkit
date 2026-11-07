# Architecture Patterns

The coding patterns that skills and the project planner build to: MVC, MVVM and layered. A project follows exactly one of them. Read by the project-planner skill and by the frontend-react skill. They cover how code is divided and which way imports point. Appearance and tokens belong to the design system, not here.

**Precedence:** the pattern comes from the phase document, else the codebase, else the default table. If the phase document and the codebase both give a pattern and they differ, that is a Blocked report, not a migration. Import direction is checked by reading the code. No script enforces it.

## Contents

1. How the pattern is pinned
2. MVC
3. MVVM
4. Layered
5. Default pattern per framework
6. Existing codebases

## 1. How the pattern is pinned

The project planner pins the pattern once, in Phase 1, as `Pattern: <mvc|mvvm|layered>` followed by `Reason: <one line>`. Later phases inherit it and never reopen it. Changing it later is a decision of its own, recorded like a stack change: the reason, the alternative considered, and the cost of migrating the code already built. A skill reads the pinned value from the phase document, else from the codebase (see Existing codebases), else from the default table. Pattern names are written in lower case so a script or a reader can match them. A repository that holds more than one part, such as a UI and a service, pins one pattern per part and names the part: `Pattern (web): mvvm` and `Pattern (api): layered`, each followed by its own `Reason:`. A skill reads the line for the part it builds.

## 2. MVC

Roles:

- Model: data types, validation rules and persistence for one kind of record.
- View: renders output (a template or a serialized response) from data it is given.
- Controller: receives a request, calls the model, picks the view.

Allowed imports:

- Controller imports model and view.
- View imports nothing from controller or model, except model types for typing.
- Model imports nothing from controller or view.

Must not contain:

- Model: request or response objects, rendering.
- View: queries, business rules, request handling.
- Controller: queries written inline, markup, business rules (move them to the model).

Directory example:

```text
app/
  models/order.py
  views/order_detail.html
  controllers/order_controller.py
```

Frameworks that default to it: Django. Django does not use these names: `models.py` is the model, the templates are the view, and `views.py` is the controller. The `controllers/` folder above is not a Django layout.

## 3. MVVM

Roles:

- View: renders state and forwards user events. It holds no logic beyond layout and event wiring.
- View model: holds the state the view needs, derives it from the model, and exposes actions the view calls.
- Model: typed data, validation and the data source.

Allowed imports:

- View imports its view model.
- View model imports model.
- Model imports neither. The view model never imports a view.

Must not contain:

- View: fetching, data transformation, business rules.
- View model: markup, styling, direct DOM access. It may call the framework's own hooks (router, query client).
- Model: state tied to one screen.

React mapping: a component is the view, a hook is the view model, and the typed data types plus the data source (query function, API client) are the model. A server-state hook such as `useQuery` sits in the view-model hook or in a data-source hook that the view-model hook calls.

Directory example:

```text
src/features/orders/
  OrderList.tsx
  useOrderList.ts
  order.types.ts
  orderApi.ts
```

Frameworks that default to it: React.

## 4. Layered

Layers, top to bottom: handlers, services, data access, models.

- Handlers: parse and validate the request, call services, shape the response. Request and response schemas (DTOs, Pydantic models) belong here.
- Services: business rules and workflows. They call data access and never see request or response objects.
- Data access: queries and external calls. They return models.
- Models: plain domain data types shared by all layers.

Cross-cutting code (authentication, logging, configuration, error types) goes in a `shared` folder or the framework's own place. Any layer may import it, and it imports no layer.

Imports point downward only. A handler imports a service, a service imports data access, and every layer may import models. A lower layer never imports a higher one, and a layer does not skip the one below it except to import models.

Must not contain:

- Handlers: business rules, queries.
- Services: request or response objects, SQL or client calls.
- Data access: business rules, status codes.
- Models: behavior that reaches into other layers.

In a Next.js project, route handlers, Server Actions, pages and layouts are handlers. A Server Component that reads data calls a service and never data access. Client Components and the components below the page follow `react-rules.md`. They receive props and do not import services or data access.

Directory example for a Node service:

```text
src/
  routes/orders.ts
  services/orderService.ts
  repositories/orderRepository.ts
  models/order.ts
```

Frameworks that default to it: Next.js, Express, NestJS, FastAPI, Oxygen.

## 5. Default pattern per framework

Use this table only when the phase document pins nothing and the project is new. A project with fewer than 3 source files is new. List the choice as an assumption.

- A project that matches more than one row takes the most specific one. A Next.js project is `layered`, not `mvvm`, for its server side. Its React components follow section 4.
- Oxygen is Shopify's hosting for Hydrogen storefronts.
- A framework or project type that is not in the table (Vue, Flask, a CLI, a library) has no default. The planner asks the user. A skill in a non-interactive run writes a Blocked report that names the missing framework.

| Framework | Default pattern |
| --------- | --------------- |
| React     | mvvm            |
| Next.js   | layered         |
| Express   | layered         |
| NestJS    | layered         |
| FastAPI   | layered         |
| Django    | mvc             |
| Oxygen    | layered         |

## 6. Existing codebases

The pinned pattern is the codebase's own. In an existing codebase the pattern is never chosen from the table.

To read it, list the folders directly under the source folder, then take the first 10 source files by path, skipping tests, configuration and generated files. Fewer than 10 means all of them. Note two things: the folder names (for example `controllers`, `hooks`, `services`) and the direction of the imports between files. Match them to the roles above and cite the files with `path:line`.

A pattern fits when the folder names match its roles and at most 1 of the sampled files imports against the allowed direction. These two numbers are starting defaults, not measured values.

Blocked reports:

- A phase document pins a different pattern from the codebase's. Report `Pattern mismatch: phase document pins <a>, codebase uses <b>`.
- The codebase fits none of the three patterns, for example a half-migrated one. Report that, name the closest pattern, and stop.
