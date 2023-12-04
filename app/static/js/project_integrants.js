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

document.addEventListener("DOMContentLoaded", function () {
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
  });
});
