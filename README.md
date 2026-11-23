# SE3200 Project 5 - Authentication

## Resources

### User

The User resource represents a registered application user.

Attributes:

- `id`
- `first_name`
- `last_name`
- `email`
- `password_hash`
- `password_salt`

The plain-text password is never stored in the database.

### Supply

The Supply resource represents a supply record within the Rapture Supply Terminal.

Attributes:

- `id`
- `name`
- `category`
- `location`
- `quantity`
- `status`

The Supply resource is restricted to authenticated users.

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL
);