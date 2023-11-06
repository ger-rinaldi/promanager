const resources = get_resources();
const api_url = `/api/usuario/${resources["usuario"]}/proyecto/${resources["proyecto"]}`;

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

async function get_tasks_per_team() {
  const request = new Request(api_url + "/tareas_equipo");
  const response = await fetch(request).then((response) => response.json());

  return response;
}

async function get_members_per_team() {
  const request = new Request(api_url + "/miembros_equipo");
  const response = await fetch(request).then((response) => response.json());

  return response;
}

async function get_tasks_per_state() {
  const request = new Request(api_url + "/estado_tareas");
  const response = await fetch(request).then((response) => response.json());

  return response;
}

async function get_project_gral_stats() {
  const request = new Request(api_url + "/gral_stats");
  const response = await fetch(request).then((response) => response.json());

  return response;
}

async function get_user_stats_project() {
  const request = new Request(api_url + "/user_stats");
  const response = await fetch(request).then((response) => response.json());

  return response;
}

export {
  get_members_per_team,
  get_tasks_per_state,
  get_tasks_per_team,
  split_url,
  get_resources,
  get_project_gral_stats,
  get_user_stats_project,
};
