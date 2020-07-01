/**
 * JavaScript file for the Home page
 */

/* jshint esversion: 8 */

/**
 * This is the model class which provides access to the server REST API
 * @type {{}}
 */
class Model {
    async read() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json"
            }
        };
        // call the REST endpoint and wait for data
        let response = await fetch("/api/ads", options);
        let data = await response.json();
        return data;
    }
}


/**
 * This is the view class which provides access to the DOM
 */
class View {
    constructor() {
        this.table = document.querySelector(".ads table");
        this.error = document.querySelector(".error");
    }

    buildTable(ads) {
        let tbody = this.table.createTBody();
        let html = "";

        // Iterate over the ads and build the table
        ads.forEach((ad) => {
            html += `
            <tr data-person_id="${ad.user.user_id}" data-note_id="${ad.ad_id}">
                <td class="timestamp">${ad.ad_date}</td>
                <td class="name">${ad.user.user_phone}</td>
                <td class="content">${ad.ad_text}</td>
            </tr>`;
        });
        // Replace the tbody with our new content
        tbody.innerHTML = html;
    }

    errorMessage(message) {
        this.error.innerHTML = message;
        this.error.classList.remove("hidden");
        this.error.classList.add("visible");
        setTimeout(() => {
            this.error.classList.remove("visible");
            this.error.classList.add("hidden");
        }, 2000);
    }
}


/**
 * This is the controller class for the user interaction
 */
class Controller {
    constructor(model, view) {
        this.model = model;
        this.view = view;

        this.initialize();
    }
    async initialize() {
        try {
            let notes = await this.model.read();
            this.view.buildTable(notes);
        } catch(err) {
            this.view.errorMessage(err);
        }

        // handle application events
        document.querySelector("table tbody").addEventListener("dblclick", (evt) => {
            let target = evt.target,
                parent = target.parentElement;

            // is this the name td?
            if (target.classList.contains("name")) {
                let person_id = parent.getAttribute("data-person_id");

                window.location = `/user/${user_id}`;

            // is this the content td
            } else if (target.classList.contains("content")) {
                let person_id = parent.getAttribute("data-person_id"),
                    note_id = parent.getAttribute("data-note_id");

                window.location = `user/${person_id}/ads/${note_id}`;
            }
        });
    }
}

// Create the MVC components
const model = new Model();
const view = new View();
const controller = new Controller(model, view);

// export the MVC components as the default
export default {
    model,
    view,
    controller
};


