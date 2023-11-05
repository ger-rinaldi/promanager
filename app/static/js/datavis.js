import {
  get_tasks_per_team,
  get_tasks_per_state,
  get_members_per_team,
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
}

document.addEventListener("DOMContentLoaded", async function () {
  mpt.addEventListener("click", members_x_team_chart);
  tpt.addEventListener("click", task_x_team_chart);
  tps.addEventListener("click", task_x_state_chart);
});
