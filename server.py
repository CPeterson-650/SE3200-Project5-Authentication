from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie

import hashlib
import hmac
import json
import os
import secrets

from database import AppDatabase


HOST = "localhost"
PORT = 8080

HASH_ITERATIONS = 600000

database = AppDatabase()

# In-memory session store
sessions = {}


# -------------------------
# PASSWORD FUNCTIONS
# -------------------------

def hash_password(password):
    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS
    )

    return (
        password_hash.hex(),
        salt.hex()
    )


def verify_password(password, stored_hash, stored_salt):
    salt = bytes.fromhex(stored_salt)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS
    )

    return hmac.compare_digest(
        password_hash.hex(),
        stored_hash
    )


# -------------------------
# HTTP HANDLER
# -------------------------

class AppHandler(BaseHTTPRequestHandler):

    # -------------------------
    # CORS
    # -------------------------

    def send_cors_headers(self):
        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:8000"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.send_header(
            "Access-Control-Allow-Credentials",
            "true"
        )


    # -------------------------
    # JSON RESPONSE
    # -------------------------

    def send_json_response(self, status_code, data):
        response = json.dumps(data)

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_cors_headers()

        self.end_headers()

        self.wfile.write(
            response.encode("utf-8")
        )


    # -------------------------
    # REQUEST BODY
    # -------------------------

    def read_json_body(self):
        try:
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            return json.loads(
                body.decode("utf-8")
            )

        except (
            json.JSONDecodeError,
            ValueError
        ):
            return None


    # -------------------------
    # SESSION HELPERS
    # -------------------------

    def get_session_id(self):
        cookie_header = self.headers.get(
            "Cookie"
        )

        if not cookie_header:
            return None

        cookie = SimpleCookie()
        cookie.load(cookie_header)

        if "session_id" not in cookie:
            return None

        return cookie[
            "session_id"
        ].value


    def get_authenticated_user_id(self):
        session_id = self.get_session_id()

        if session_id is None:
            return None

        session = sessions.get(
            session_id
        )

        if session is None:
            return None

        return session["user_id"]


    def require_authentication(self):
        user_id = (
            self.get_authenticated_user_id()
        )

        if user_id is None:
            self.send_json_response(
                401,
                {
                    "error":
                    "Authentication required."
                }
            )

            return None

        return user_id


    # -------------------------
    # SUPPLY HELPERS
    # -------------------------

    def get_supply_id(self):
        parts = (
            self.path
            .strip("/")
            .split("/")
        )

        if (
            len(parts) == 2
            and parts[0] == "supplies"
        ):
            try:
                return int(parts[1])

            except ValueError:
                return None

        return None


    def valid_supply(self, supply):
        if not isinstance(supply, dict):
            return False

        required_fields = [
            "name",
            "category",
            "location",
            "quantity",
            "status"
        ]

        for field in required_fields:
            if field not in supply:
                return False

        return True


    # -------------------------
    # OPTIONS
    # -------------------------

    def do_OPTIONS(self):
        self.send_response(204)

        self.send_cors_headers()

        self.end_headers()


    # -------------------------
    # GET
    # -------------------------

    def do_GET(self):

        # Check current session
        # GET /session

        if self.path == "/session":

            user_id = (
                self.get_authenticated_user_id()
            )

            if user_id is None:
                self.send_json_response(
                    401,
                    {
                        "error":
                        "Not authenticated."
                    }
                )

                return

            self.send_json_response(
                200,
                {
                    "authenticated": True,
                    "user_id": user_id
                }
            )

            return


        # List supplies
        # GET /supplies

        if self.path == "/supplies":

            if self.require_authentication() is None:
                return

            supplies = (
                database.get_all_supplies()
            )

            self.send_json_response(
                200,
                supplies
            )

            return


        # Retrieve one supply
        # GET /supplies/{id}

        supply_id = self.get_supply_id()

        if supply_id is not None:

            if self.require_authentication() is None:
                return

            supply = database.get_supply(
                supply_id
            )

            if supply is None:
                self.send_json_response(
                    404,
                    {
                        "error":
                        "Supply not found."
                    }
                )

                return

            self.send_json_response(
                200,
                supply
            )

            return


        self.send_json_response(
            404,
            {
                "error":
                "Route not found."
            }
        )


    # -------------------------
    # POST
    # -------------------------

    def do_POST(self):

        # -------------------------
        # REGISTER
        # POST /users
        # -------------------------

        if self.path == "/users":

            data = self.read_json_body()

            if data is None:
                self.send_json_response(
                    400,
                    {
                        "error":
                        "Invalid JSON data."
                    }
                )

                return


            required_fields = [
                "first_name",
                "last_name",
                "email",
                "password"
            ]


            for field in required_fields:

                if (
                    field not in data
                    or not str(
                        data[field]
                    ).strip()
                ):

                    self.send_json_response(
                        400,
                        {
                            "error":
                            "All registration fields are required."
                        }
                    )

                    return


            first_name = (
                data["first_name"].strip()
            )

            last_name = (
                data["last_name"].strip()
            )

            email = (
                data["email"]
                .strip()
                .lower()
            )

            password = data["password"]


            existing_user = (
                database.get_user_by_email(
                    email
                )
            )


            if existing_user is not None:

                self.send_json_response(
                    409,
                    {
                        "error":
                        "An account with that email already exists."
                    }
                )

                return


            password_hash, password_salt = (
                hash_password(password)
            )


            user_id = database.create_user(
                first_name,
                last_name,
                email,
                password_hash,
                password_salt
            )


            self.send_json_response(
                201,
                {
                    "id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                }
            )

            return


        # -------------------------
        # LOGIN
        # POST /sessions
        # -------------------------

        if self.path == "/sessions":

            data = self.read_json_body()

            if data is None:
                self.send_json_response(
                    400,
                    {
                        "error":
                        "Invalid JSON data."
                    }
                )

                return


            email = str(
                data.get(
                    "email",
                    ""
                )
            ).strip().lower()


            password = str(
                data.get(
                    "password",
                    ""
                )
            )


            if (
                email == ""
                or password == ""
            ):

                self.send_json_response(
                    400,
                    {
                        "error":
                        "Email and password are required."
                    }
                )

                return


            user = (
                database.get_user_by_email(
                    email
                )
            )


            if user is None:

                self.send_json_response(
                    401,
                    {
                        "error":
                        "Invalid email or password."
                    }
                )

                return


            if not verify_password(
                password,
                user["password_hash"],
                user["password_salt"]
            ):

                self.send_json_response(
                    401,
                    {
                        "error":
                        "Invalid email or password."
                    }
                )

                return


            session_id = (
                secrets.token_hex(32)
            )


            sessions[session_id] = {
                "user_id": user["id"]
            }


            response = {
                "id": user["id"],
                "first_name":
                    user["first_name"],
                "last_name":
                    user["last_name"],
                "email":
                    user["email"]
            }


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Set-Cookie",
                "session_id="
                + session_id
                + "; HttpOnly; SameSite=Lax; Path=/"
            )

            self.send_cors_headers()

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    response
                ).encode("utf-8")
            )

            return


        # -------------------------
        # CREATE SUPPLY
        # POST /supplies
        # -------------------------

        if self.path == "/supplies":

            if self.require_authentication() is None:
                return


            supply = self.read_json_body()


            if not self.valid_supply(supply):

                self.send_json_response(
                    400,
                    {
                        "error":
                        "Invalid supply data."
                    }
                )

                return


            supply_id = (
                database.create_supply(
                    supply
                )
            )


            created_supply = (
                database.get_supply(
                    supply_id
                )
            )


            self.send_json_response(
                201,
                created_supply
            )

            return


        self.send_json_response(
            404,
            {
                "error":
                "Route not found."
            }
        )


    # -------------------------
    # PUT
    # -------------------------

    def do_PUT(self):

        supply_id = self.get_supply_id()


        if supply_id is None:

            self.send_json_response(
                404,
                {
                    "error":
                    "Route not found."
                }
            )

            return


        if self.require_authentication() is None:
            return


        existing_supply = (
            database.get_supply(
                supply_id
            )
        )


        if existing_supply is None:

            self.send_json_response(
                404,
                {
                    "error":
                    "Supply not found."
                }
            )

            return


        supply = self.read_json_body()


        if not self.valid_supply(supply):

            self.send_json_response(
                400,
                {
                    "error":
                    "Invalid supply data."
                }
            )

            return


        database.update_supply(
            supply_id,
            supply
        )


        updated_supply = (
            database.get_supply(
                supply_id
            )
        )


        self.send_json_response(
            200,
            updated_supply
        )


    # -------------------------
    # DELETE
    # -------------------------

    def do_DELETE(self):

        # -------------------------
        # LOGOUT
        # DELETE /sessions
        # -------------------------

        if self.path == "/sessions":

            session_id = self.get_session_id()

            if (
                session_id is not None
                and session_id in sessions
            ):
                del sessions[session_id]


            self.send_response(204)

            self.send_header(
                "Set-Cookie",
                "session_id=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/"
            )

            self.send_cors_headers()

            self.end_headers()

            return


        # -------------------------
        # DELETE SUPPLY
        # DELETE /supplies/{id}
        # -------------------------

        supply_id = self.get_supply_id()


        if supply_id is None:

            self.send_json_response(
                404,
                {
                    "error":
                    "Route not found."
                }
            )

            return


        if self.require_authentication() is None:
            return


        deleted = (
            database.delete_supply(
                supply_id
            )
        )


        if not deleted:

            self.send_json_response(
                404,
                {
                    "error":
                    "Supply not found."
                }
            )

            return


        self.send_response(204)

        self.send_cors_headers()

        self.end_headers()


# -------------------------
# START SERVER
# -------------------------

if __name__ == "__main__":

    server = HTTPServer(
        (HOST, PORT),
        AppHandler
    )

    print(
        "Rapture Authentication API "
        + "running at "
        + f"http://{HOST}:{PORT}"
    )

    server.serve_forever()