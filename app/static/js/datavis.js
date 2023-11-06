import {
  get_tasks_per_team,
  get_tasks_per_state,
  get_members_per_team,
  get_project_gral_stats,
  get_user_stats_project,
} from "./api_consult.mjs";

const mpt = document.getElementById("mpt-btn");
const tpt = document.getElementById("tpt-btn");
const tps = document.getElementById("tps-btn");
const textdata = document.getElementById("textdata");

async function task_x_team_chart() {
  const data = await get_tasks_per_team();
  let label = "Total de tareas por equipo";

  make_chart(label, data);
}

async function members_x_team_chart() {
  const data = await get_members_per_team();
  let label = "Total de miembros por equipo";

  make_chart(label, data);
}

async function task_x_state_chart() {
  const data = await get_tasks_per_state();
  let label = "Total de tareas por estado";

  make_chart(label, data);
}

function make_chart(label, data) {
  const chart_container = document.getElementById("chart-cointainer");
  const canvas = document.createElement("canvas");
  canvas.setAttribute("id", "barchart");

  chart_container.removeChild(chart_container.querySelector("#barchart"));
  chart_container.appendChild(canvas);

  new Chart(document.getElementById("barchart"), {
    type: "bar",
    data: {
      labels: data.map((group) => group.nombre),
      datasets: [
        {
          label: label,
          data: data.map((group) => group.total),
          borderWidth: 3,
        },
      ],
    },
    options: {
      scales: {
        y: {
          ticks: {
            callback: function (value) {
              if (value % 1 === 0) {
                return value;
              }
            },
          },
          max:
            Math.ceil(
              data.map((group) => group.total).sort((a, b) => a - b)[
                data.length - 1
              ] / 5
            ) * 5,
          beginAtZero: true,
        },
      },
    },
  });
  canvas.scrollIntoView({ behavior: "smooth" });
}

async function show_project_gral_stats() {
  const data = await get_project_gral_stats();
  const task_per_state = await get_tasks_per_state();

  const gral_stats_elem = document.getElementById("gral_stats");

  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      let capitalized_key = key[0].toUpperCase() + key.slice(1) + ": ";
      let pContent = capitalized_key.split("_").join(" ") + data[key];

      const pElement = document.createElement("p");
      pElement.setAttribute("class", "col");
      pElement.textContent = pContent;
      gral_stats_elem.append(pElement);
    }
  }

  const data_averages = process_gral_stats(data, task_per_state);
  const avg_stats_elem = document.getElementById("gral_stats_averages");

  for (const key in data_averages) {
    if (data_averages.hasOwnProperty(key)) {
      let capitalized_key = key[0].toUpperCase() + key.slice(1) + ": ";
      let pContent = capitalized_key.split("_").join(" ") + data_averages[key];

      const pElement = document.createElement("p");
      pElement.setAttribute("class", "col");
      pElement.textContent = pContent;
      avg_stats_elem.append(pElement);
    }
  }
}

async function show_user_stats() {
  const data = await get_user_stats_project();
  const task_states = data["por_estado"];
  delete data["por_estado"];

  let completed_tasks = 0;
  task_states.forEach((state) => {
    if (state.nombre == "Completada") {
      completed_tasks = state.total;
    }
  });

  console.log(data.total_tareas);
  console.log(completed_tasks);

  data["porcentaje_tareas_completadas"] =
    checkForNaN((completed_tasks / data.total_tareas) * 100) + "%";

  const user_stats_elem = document.getElementById("user_stats");

  for (const key in data) {
    let capitalized_key = key[0].toUpperCase() + key.slice(1) + ": ";
    let pContent = capitalized_key.split("_").join(" ") + data[key];
    console.log(pContent);

    const pElement = document.createElement("p");
    pElement.setAttribute("class", "col");
    pElement.textContent = pContent;
    user_stats_elem.append(pElement);
  }

  const user_tasks_elem = document.getElementById("user_task_stats");

  for (const state of task_states) {
    let capitalized_name =
      state.nombre[0].toUpperCase() + state.nombre.slice(1) + ": ";
    let pContent = capitalized_name.split("_").join(" ") + state.total;

    const pElement = document.createElement("p");
    pElement.setAttribute("class", "col");
    pElement.textContent = pContent;
    user_tasks_elem.append(pElement);
  }
}

function process_gral_stats(gral_stats, tasks_per_state) {
  let processed_data = {};

  processed_data["promedio_tareas_equipo"] = checkForNaN(
    gral_stats.total_tareas / gral_stats.total_equipos
  );

  let total_task_completed = 0;
  let total_task_late = 0;

  tasks_per_state.forEach((e) => {
    if (e.nombre === "Completada") {
      total_task_completed = e.total;
    } else if (e.nombre === "Atrasada") {
      total_task_late = e.total;
    }
  });

  processed_data["porcentaje_tareas_completadas"] =
    checkForNaN((total_task_completed / gral_stats.total_tareas) * 100) + "%";

  processed_data["porcentaje_tareas_atrasadas"] =
    checkForNaN((total_task_late / gral_stats.total_tareas) * 100) + "%";

  return processed_data;
}

function checkForNaN(result) {
  if (isNaN(result)) {
    return "0";
  } else {
    return result;
  }
}

document.addEventListener("DOMContentLoaded", async function () {
  mpt.addEventListener("click", members_x_team_chart);
  tpt.addEventListener("click", task_x_team_chart);
  tps.addEventListener("click", task_x_state_chart);
  show_project_gral_stats();
  show_user_stats();
});
