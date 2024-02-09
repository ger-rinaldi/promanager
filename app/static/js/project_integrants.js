import { get_api_url } from "./api_utils.js";

const api_url = get_api_url();

function getAlertElement(message, status) {
  const dismissBtn = () => {
    const btn = document.createElement("button");
    btn.classList.add("close");
    btn.setAttribute("type", "button");
    btn.setAttribute("data-bs-dismiss", "alert");
    btn.setAttribute("aria-label", "Close");
    btn.innerHTML = "&times;";

    return btn;
  };
  const alertElement = document.createElement("div");

  if (status !== 200) {
    alertElement.classList.add("alert-danger");
  } else {
    alertElement.classList.add("alert-success");
  }

  alertElement.classList.add("show", "fade", "alert-dismissible", "alert");
  alertElement.setAttribute("role", "alert");
  alertElement.textContent = message;
  alertElement.appendChild(dismissBtn());
  return alertElement;
}

function clearMessages() {
  const msgDisplay = document.getElementById("message-display");

  while (msgDisplay.firstChild) {
    msgDisplay.removeChild(msgDisplay.lastChild);
  }
}

function displayResponseMessages(responseStatus, responseMessages) {
  const msgDisplay = document.getElementById("message-display");
  clearMessages();

  if (Array.isArray(responseMessages)) {
    for (const message of responseMessages) {
      const alertElement = getAlertElement(message, responseStatus);
      msgDisplay.appendChild(alertElement);
    }
  } else {
    const alertElement = getAlertElement(responseMessages, responseStatus);
    msgDisplay.appendChild(alertElement);
  }
}

async function getProyectRoles() {
  const rolesResponse = await fetch("/api/proyecto/roles");
  const roles = await rolesResponse.json();
  return roles;
}

function makeSelectCell(defaultOption, values) {
  const selectElement = document.createElement("select");
  selectElement.setAttribute("class", "rol-cell");
  selectElement.classList.add("text-center");
  values.forEach((r) => {
    const optionElement = document.createElement("option");
    optionElement.value = r.id;
    optionElement.textContent = r.nombre;

    if (defaultOption === r.nombre) {
      optionElement.setAttribute("selected", "");
    }

    selectElement.appendChild(optionElement);
  });

  return selectElement;
}

function makeCell(keyName) {
  // class="text-center {{key}}-cell"
  const rowCell = document.createElement("td");
  rowCell.classList.add("text-center", `${keyName}-cell`);
  return rowCell;
}

function switchHiddenActions(element) {
  const buttonsCell = element.parentElement;

  for (const child of buttonsCell.children) {
    if ("hidden" in child.attributes) {
      child.removeAttribute("hidden");
    } else {
      child.setAttribute("hidden", "");
    }
  }
}

// ! ALERT: SIMPLIFY LOGIC THIS IS A BUNCH OF SHIIIIT
document.addEventListener("DOMContentLoaded", function () {
  const msgDisplay = document.getElementById("message-display");
  const createButton = document.getElementById("create-button");
  const table = document.getElementById("table-body");

  createButton.addEventListener("click", async function () {
    const createParticipantURL = api_url + "/agregar";
    const createForm = new FormData();
    const newParticipant = document.getElementById("participant_identif").value;
    const roleOfParcipant = document.getElementById("role").value;

    document.getElementById("participant_identif").value = "";
    document.getElementById("role").value = "";

    createForm.append("participant_identif", newParticipant);
    createForm.append("role", roleOfParcipant);

    // request new participant information to append to table without refreshing

    const request = {
      method: "POST",
      body: createForm,
    };

    const registerResponse = await fetch(createParticipantURL, request);
    const responsePromise = await registerResponse.json();
    displayResponseMessages(registerResponse.status, responsePromise.message);
  });

  // eliminar y actualizar participante
  const editButtons = document.querySelectorAll(".edit-button");

  editButtons.forEach((currentEditButton) => {
    currentEditButton.addEventListener("click", async function () {
      // get the row
      const row = this.parentNode.parentNode;
      //get the roles
      const roles = await getProyectRoles();
      // get its children
      const roleCell = row.querySelector(".rol-cell");
      // add them to the select element
      const selectElement = makeSelectCell(roleCell.textContent, roles);
      // make the Role one a dropdown selector, like the one above

      roleCell.replaceWith(selectElement);
      switchHiddenActions(this);
    });
  });

  const deleteButtons = document.querySelectorAll(".delete-button");

  deleteButtons.forEach((e) => {
    e.addEventListener("click", async function () {
      const row = e.parentNode.parentNode;

      const deleteParticipantURL = api_url + "/remover";
      const deleteForm = new FormData();
      const participantUsername =
        row.querySelector(".username-cell").textContent;

      deleteForm.append("participant_identif", participantUsername);
      const request = {
        method: "POST",
        body: deleteForm,
      };
      const deleteRequest = await fetch(deleteParticipantURL, request);
      const responsePromise = await deleteRequest.json();
      displayResponseMessages(deleteRequest.status, responsePromise.message);
      table.removeChild(row);
    });
  });

  const saveButtons = document.querySelectorAll(".save-button");

  saveButtons.forEach((saveButton) => {
    saveButton.addEventListener("click", async function () {
      // send save to api
      const row = this.parentNode.parentNode;
      const updateParticipantURL = api_url + "/modificar";
      const updateForm = new FormData();

      updateForm.append(
        "participant_identif",
        row.querySelector(".username-cell").textContent
      );

      updateForm.append("role", row.querySelector(".rol-cell").value);

      const request = {
        method: "POST",
        body: updateForm,
      };

      const updateRequest = await fetch(updateParticipantURL, request);
      const updateResponse = await updateRequest.json();

      displayResponseMessages(updateRequest.status, updateResponse.message);

      if (updateRequest.status === 200) {
        // restore role cell with new role
        const roleCell = makeCell("rol");
        // row.querySelector(".rol-cell").options[row.querySelector(".rol-cell").selectedIndex].textContent
        roleCell.textContent =
          row.querySelector(".rol-cell").options[
            row.querySelector(".rol-cell").selectedIndex
          ].textContent;

        row.querySelector(".rol-cell").replaceWith(roleCell);
      }

      switchHiddenActions(this);
    });
  });

  const cancelButtons = document.querySelectorAll(".cancel-button");

  cancelButtons.forEach((cancelButton) => {
    cancelButton.addEventListener("click", async function () {
      // restore role cell with previous role
      const row = this.parentNode.parentNode;

      const getPreviousRole = () => {
        for (const option of row.querySelector(".rol-cell")) {
          if ("selected" in option.attributes) {
            return option.textContent;
          }
        }
      };

      const roleCell = makeCell("rol");
      roleCell.textContent = getPreviousRole();

      row.querySelector(".rol-cell").replaceWith(roleCell);

      switchHiddenActions(this);
    });
  });
});
