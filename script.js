const API_URL = "http://localhost:8080";


// -----------------------------
// DOM QUERYING
// -----------------------------

const loginSection =
    document.querySelector("#login-section");

const registerSection =
    document.querySelector("#register-section");

const appSection =
    document.querySelector("#app-section");


const loginForm =
    document.querySelector("#login-form");

const loginEmail =
    document.querySelector("#login-email");

const loginPassword =
    document.querySelector("#login-password");

const loginMessage =
    document.querySelector("#login-message");


const registerForm =
    document.querySelector("#register-form");

const firstName =
    document.querySelector("#first-name");

const lastName =
    document.querySelector("#last-name");

const registerEmail =
    document.querySelector("#register-email");

const registerPassword =
    document.querySelector("#register-password");

const registerMessage =
    document.querySelector("#register-message");


const showRegisterButton =
    document.querySelector("#show-register-button");

const backToLoginButton =
    document.querySelector("#back-to-login-button");

const logoutButton =
    document.querySelector("#logout-button");

const welcomeMessage =
    document.querySelector("#welcome-message");


const addSupplyButton =
    document.querySelector("#add-supply-button");

const supplyFormSection =
    document.querySelector("#supply-form-section");

const supplyFormTitle =
    document.querySelector("#supply-form-title");

const supplyForm =
    document.querySelector("#supply-form");

const cancelSupplyButton =
    document.querySelector("#cancel-supply-button");

const supplyList =
    document.querySelector("#supply-list");


const supplyName =
    document.querySelector("#supply-name");

const supplyCategory =
    document.querySelector("#supply-category");

const supplyLocation =
    document.querySelector("#supply-location");

const supplyQuantity =
    document.querySelector("#supply-quantity");

const supplyStatus =
    document.querySelector("#supply-status");


// null means creating a new supply.
// A number means editing an existing supply.

let editingSupplyId = null;


// -----------------------------
// UI STATE
// -----------------------------

function showLogin() {

    loginSection.classList.remove(
        "hidden"
    );

    registerSection.classList.add(
        "hidden"
    );

    appSection.classList.add(
        "hidden"
    );
}


function showRegister() {

    loginSection.classList.add(
        "hidden"
    );

    registerSection.classList.remove(
        "hidden"
    );

    appSection.classList.add(
        "hidden"
    );
}


function showApp(user) {

    loginSection.classList.add(
        "hidden"
    );

    registerSection.classList.add(
        "hidden"
    );

    appSection.classList.remove(
        "hidden"
    );


    if (user && user.first_name) {

        welcomeMessage.textContent =
            "Welcome, " + user.first_name;

    } else {

        welcomeMessage.textContent =
            "Authenticated User";
    }


    loadSupplies();
}


// -----------------------------
// CHECK SESSION
// -----------------------------

function checkSession() {

    fetch(
        API_URL + "/session",
        {
            credentials: "include"
        }
    )

        .then(function (response) {

            if (!response.ok) {

                showLogin();

                return null;
            }

            return response.json();

        })

        .then(function (data) {

            if (
                data !== null
                && data.authenticated
            ) {

                showApp(null);
            }

        })

        .catch(function (error) {

            console.log(error);

            showLogin();

        });
}


// -----------------------------
// REGISTRATION
// -----------------------------

registerForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        const user = {

            first_name:
                firstName.value.trim(),

            last_name:
                lastName.value.trim(),

            email:
                registerEmail.value.trim(),

            password:
                registerPassword.value
        };


        registerMessage.textContent =
            "Creating account...";


        fetch(
            API_URL + "/users",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                credentials: "include",

                body:
                    JSON.stringify(user)
            }
        )

            .then(function (response) {

                return response
                    .json()
                    .then(function (data) {

                        return {
                            response: response,
                            data: data
                        };

                    });

            })

            .then(function (result) {

                if (!result.response.ok) {

                    registerMessage.textContent =
                        result.data.error;

                    return;
                }


                registerMessage.textContent =
                    "Account created successfully.";


                registerForm.reset();


                loginEmail.value =
                    result.data.email;


                loginMessage.textContent =
                    "Registration successful. Please log in.";


                showLogin();

            })

            .catch(function (error) {

                console.log(error);

                registerMessage.textContent =
                    "Unable to create account.";

            });

    }
);


// -----------------------------
// LOGIN
// -----------------------------

loginForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        const credentials = {

            email:
                loginEmail.value.trim(),

            password:
                loginPassword.value
        };


        loginMessage.textContent =
            "Logging in...";


        fetch(
            API_URL + "/sessions",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                credentials: "include",

                body:
                    JSON.stringify(
                        credentials
                    )
            }
        )

            .then(function (response) {

                return response
                    .json()
                    .then(function (data) {

                        return {
                            response: response,
                            data: data
                        };

                    });

            })

            .then(function (result) {

                if (!result.response.ok) {

                    loginMessage.textContent =
                        result.data.error;

                    return;
                }


                loginMessage.textContent = "";

                loginForm.reset();


                showApp(
                    result.data
                );

            })

            .catch(function (error) {

                console.log(error);

                loginMessage.textContent =
                    "Unable to log in.";

            });

    }
);


// -----------------------------
// LOGOUT
// -----------------------------

logoutButton.addEventListener(
    "click",
    function () {

        fetch(
            API_URL + "/sessions",
            {
                method: "DELETE",

                credentials: "include"
            }
        )

            .then(function (response) {

                if (!response.ok) {

                    throw new Error(
                        "Unable to log out."
                    );
                }


                closeSupplyForm();

                supplyList.innerHTML = "";

                loginMessage.textContent =
                    "You have been logged out.";

                showLogin();

            })

            .catch(function (error) {

                console.log(error);

            });

    }
);


// -----------------------------
// LOAD SUPPLIES
// -----------------------------

function loadSupplies() {

    fetch(
        API_URL + "/supplies",
        {
            credentials: "include"
        }
    )

        .then(function (response) {

            if (response.status === 401) {

                showLogin();

                throw new Error(
                    "Authentication required."
                );
            }


            if (!response.ok) {

                throw new Error(
                    "Unable to load supplies."
                );
            }


            return response.json();

        })

        .then(function (supplies) {

            displaySupplies(
                supplies
            );

        })

        .catch(function (error) {

            console.log(error);

        });
}


// -----------------------------
// DISPLAY SUPPLIES
// -----------------------------

function displaySupplies(supplies) {

    supplyList.innerHTML = "";


    if (supplies.length === 0) {

        const message =
            document.createElement("p");

        message.textContent =
            "No supplies currently recorded.";

        supplyList.appendChild(
            message
        );

        return;
    }


    supplies.forEach(
        function (supply) {

            const card =
                document.createElement(
                    "div"
                );

            card.classList.add(
                "supply-card"
            );


            const title =
                document.createElement(
                    "h3"
                );

            title.textContent =
                supply.name;


            const category =
                document.createElement(
                    "p"
                );

            category.classList.add(
                "supply-info"
            );

            category.textContent =
                "Category: "
                + supply.category;


            const location =
                document.createElement(
                    "p"
                );

            location.classList.add(
                "supply-info"
            );

            location.textContent =
                "Location: "
                + supply.location;


            const quantity =
                document.createElement(
                    "p"
                );

            quantity.classList.add(
                "supply-info"
            );

            quantity.textContent =
                "Quantity: "
                + supply.quantity;


            const status =
                document.createElement(
                    "p"
                );

            status.classList.add(
                "supply-info"
            );

            status.textContent =
                "Status: "
                + supply.status;


            const actions =
                document.createElement(
                    "div"
                );

            actions.classList.add(
                "supply-actions"
            );


            // EDIT BUTTON

            const editButton =
                document.createElement(
                    "button"
                );

            editButton.textContent =
                "Edit";


            editButton.addEventListener(
                "click",
                function () {

                    openEditForm(
                        supply
                    );

                }
            );


            // DELETE BUTTON

            const deleteButton =
                document.createElement(
                    "button"
                );

            deleteButton.textContent =
                "Delete";

            deleteButton.classList.add(
                "delete-button"
            );


            deleteButton.addEventListener(
                "click",
                function () {

                    deleteSupply(
                        supply
                    );

                }
            );


            actions.appendChild(
                editButton
            );

            actions.appendChild(
                deleteButton
            );


            card.appendChild(
                title
            );

            card.appendChild(
                category
            );

            card.appendChild(
                location
            );

            card.appendChild(
                quantity
            );

            card.appendChild(
                status
            );

            card.appendChild(
                actions
            );


            supplyList.appendChild(
                card
            );

        }
    );
}


// -----------------------------
// CREATE FORM
// -----------------------------

function openCreateForm() {

    editingSupplyId = null;

    supplyFormTitle.textContent =
        "Add Supply";

    supplyForm.reset();

    supplyFormSection.classList.remove(
        "hidden"
    );
}


// -----------------------------
// EDIT FORM
// -----------------------------

function openEditForm(supply) {

    editingSupplyId =
        supply.id;


    supplyFormTitle.textContent =
        "Edit Supply";


    supplyName.value =
        supply.name;

    supplyCategory.value =
        supply.category;

    supplyLocation.value =
        supply.location;

    supplyQuantity.value =
        supply.quantity;

    supplyStatus.value =
        supply.status;


    supplyFormSection.classList.remove(
        "hidden"
    );
}


// -----------------------------
// CLOSE SUPPLY FORM
// -----------------------------

function closeSupplyForm() {

    editingSupplyId = null;

    supplyForm.reset();

    supplyFormSection.classList.add(
        "hidden"
    );
}


// -----------------------------
// CREATE SUPPLY
// -----------------------------

function createSupply(supply) {

    fetch(
        API_URL + "/supplies",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            credentials: "include",

            body:
                JSON.stringify(
                    supply
                )
        }
    )

        .then(function (response) {

            if (!response.ok) {

                throw new Error(
                    "Unable to create supply."
                );
            }


            closeSupplyForm();

            loadSupplies();

        })

        .catch(function (error) {

            console.log(error);

        });
}


// -----------------------------
// UPDATE SUPPLY
// -----------------------------

function updateSupply(
    supplyId,
    supply
) {

    fetch(
        API_URL
        + "/supplies/"
        + supplyId,
        {
            method: "PUT",

            headers: {
                "Content-Type":
                    "application/json"
            },

            credentials: "include",

            body:
                JSON.stringify(
                    supply
                )
        }
    )

        .then(function (response) {

            if (!response.ok) {

                throw new Error(
                    "Unable to update supply."
                );
            }


            closeSupplyForm();

            loadSupplies();

        })

        .catch(function (error) {

            console.log(error);

        });
}


// -----------------------------
// DELETE SUPPLY
// -----------------------------

function deleteSupply(supply) {

    const confirmed =
        confirm(
            "Are you sure you want to delete "
            + supply.name
            + "?"
        );


    if (!confirmed) {
        return;
    }


    fetch(
        API_URL
        + "/supplies/"
        + supply.id,
        {
            method: "DELETE",

            credentials: "include"
        }
    )

        .then(function (response) {

            if (!response.ok) {

                throw new Error(
                    "Unable to delete supply."
                );
            }


            loadSupplies();

        })

        .catch(function (error) {

            console.log(error);

        });
}


// -----------------------------
// SUPPLY FORM SUBMISSION
// -----------------------------

supplyForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();


        const supply = {

            name:
                supplyName.value.trim(),

            category:
                supplyCategory.value.trim(),

            location:
                supplyLocation.value.trim(),

            quantity:
                Number(
                    supplyQuantity.value
                ),

            status:
                supplyStatus.value.trim()
        };


        if (
            editingSupplyId === null
        ) {

            createSupply(
                supply
            );

        } else {

            updateSupply(
                editingSupplyId,
                supply
            );

        }

    }
);


// -----------------------------
// UI BUTTON EVENTS
// -----------------------------

showRegisterButton.addEventListener(
    "click",
    function () {

        registerMessage.textContent = "";

        showRegister();

    }
);


backToLoginButton.addEventListener(
    "click",
    function () {

        loginMessage.textContent = "";

        showLogin();

    }
);


addSupplyButton.addEventListener(
    "click",
    openCreateForm
);


cancelSupplyButton.addEventListener(
    "click",
    closeSupplyForm
);


// -----------------------------
// INITIAL PAGE LOAD
// -----------------------------

checkSession();