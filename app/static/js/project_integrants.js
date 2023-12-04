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

function getErrorDisplay(errorMsg) {
  const errorElement = document.createElement("div");
  errorElement.classList.add("alert-danger");
  errorElement.classList.add("alert");
  errorElement.textContent = errorMsg;
  return errorElement;
}

function getSuccessDisplay(successMsg) {
  const successElement = document.createElement("div");
  successElement.classList.add("alert-success");
  successElement.classList.add("alert");
  successElement.textContent = successMsg;
  return successElement;
}

function clearMessages() {
  const msgDisplay = document.getElementById("message-display");

  while (msgDisplay.firstChild) {
    msgDisplay.removeChild(msgDisplay.lastChild);
  }
}

function displayResponseMessages(responseStatus, responseMessages) {
  clearMessages();
  const msgDisplay = document.getElementById("message-display");

  displayByStatus = (message) => {
    if (responseStatus === 200) {
      msgDisplay.appendChild(getSuccessDisplay(message));
    } else {
      msgDisplay.appendChild(getErrorDisplay(message));
    }
  };

  if (Array.isArray(responseMessages)) {
    for (const message of responseMessages) {
      displayByStatus(message);
    }
  } else {
    displayByStatus(responseMessages);
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
});
