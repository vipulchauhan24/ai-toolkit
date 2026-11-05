# Link shortener API

Product: an HTTP API that turns a long URL into a short code and redirects the short code to the long URL. It also reports how many times each code was used.

Engineering: Node.js with TypeScript and Express, SQLite for storage, deployed as one container. Pattern is not fixed. No authentication in v1.

Acceptance:
- POST /links returns a short code for a valid URL and a 400 error for an invalid one.
- GET /:code redirects to the long URL and counts the visit.
- GET /links/:code/stats returns the visit count.
