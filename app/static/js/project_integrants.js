function split_url() {
  const str_url = window.location.toString();
  const split_url = str_url.split("/");

  return split_url;
}

function get_resources() {
  let available_resources = ["usuario", "proyecto", "equipo", "tarea"];
  let queried_resources = {};

  const path = split_url();

  for (const resource of available_resources) {
    if (path.indexOf(resource) >= 0) {
      queried_resources[resource] = path[path.indexOf(resource) + 1];
    }
  }

  return queried_resources;
}

const resources = get_resources();
const api_url = `/api/usuario/${resources["usuario"]}/proyecto/${resources["proyecto"]}/integrante`;

function getAlertElement(message, status) {
  const dismissBtn = () => {
    const btn = document.createElement("button");
    btn.classList.add("btn-close");
    btn.setAttribute("type", "button");
    btn.setAttribute("data-bs-dismiss", "alert");
    btn.setAttribute("aria-label", "Close");

    return btn;
  };
  const alertElement = document.createElement("div");

  if (status !== 200) {
    alertElement.classList.add("alert-danger");
  } else {
    alertElement.classList.add("alert-success");
  }

  alertElement.classList.add("alert-fixed");
  alertElement.classList.add("show");
  alertElement.classList.add("fade");
  alertElement.classList.add("alert-dismissible");
  alertElement.classList.add("alert");
  alertElement.role = "alert";
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
  clearMessages();

  if (Array.isArray(responseMessages)) {
    for (const message of responseMessages) {
      const alertElement = getAlertElement(message, responseStatus);
      document.body.appendChild(alertElement);
    }
  } else {
    const alertElement = getAlertElement(responseMessages, responseStatus);
    document.body.appendChild(alertElement);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const msgDisplay = document.getElementById("message-display");
  const createButton = document.getElementById("create-button");

  createButton.addEventListener("click", async function () {
    const createParticipantURL = api_url + "/agregar";
    const createForm = new FormData();
    const newParticipant = document.getElementById("participant_identif").value;
    const roleOfParcipant = document.getElementById("role").value;

    document.getElementById("participant_identif").value = "";
    document.getElementById("role").value = "";

    createForm.append("participant_identif", newParticipant);
    createForm.append("role", roleOfParcipant);

    const request = {
      method: "POST",
      body: createForm,
    };

    const registerResponse = await fetch(createParticipantURL, request);
    const responsePromise = await registerResponse.json();
    displayResponseMessages(registerResponse.status, responsePromise.message);
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
});
