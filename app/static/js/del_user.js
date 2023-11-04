const username = document.getElementById("username").value;

const pass_1_input = document.getElementById("contrasena_1");
const pass_2_input = document.getElementById("contrasena_2");

const pass_1_div = document.getElementById("div_pass_1");
const pass_2_div = document.getElementById("div_pass_2");

document.addEventListener("DOMContentLoaded", function () {
  pass_1_input.addEventListener("keyup", async (e) => {
    console.log(
      "pass_1 ",
      pass_1_input.value,
      "pass_2 in ONE ",
      pass_2_input.value
    );
    same_pass_feedback();
  });
  pass_2_input.addEventListener("keyup", async (e) => {
    console.log("pass_2 ", pass_2_input.value);
    same_pass_feedback();
  });
});

function same_pass_feedback() {
  if (pass_1_div.querySelector("#diff-pass") !== null) {
    pass_1_div.removeChild(pass_1_div.querySelector("#diff-pass"));
    pass_2_div.removeChild(pass_2_div.querySelector("#diff-pass"));
  }

  if (!same_pass()) {
    pass_1_div.appendChild(diff_pass_message());
    pass_2_div.appendChild(diff_pass_message());
  }
}

function diff_pass_message() {
  const divergent_passwords = document.createElement("div");
  divergent_passwords.setAttribute("class", "feedback ");
  divergent_passwords.setAttribute("id", "diff-pass");
  divergent_passwords.textContent = "Las contraseñas ingresadas son distintas.";

  return divergent_passwords;
}

function same_pass() {
  return pass_1_input.value === pass_2_input.value;
}

async function alert_wrong_passwords() {
  let del_resp;

  if (!same_pass()) {
    alert("¡Las contraseñas ingresadas difieren entre sí!");
    return;
  }

  let formData = new FormData();
  formData.append(
    "contrasena_1",
    pass_1_div.querySelector("#contrasena_1").value
  );
  formData.append(
    "contrasena_2",
    pass_2_div.querySelector("#contrasena_2").value
  );

  del_resp = await fetch(`/api/usuario/${username}/eliminar`, {
    body: formData,
    method: "POST",
  });

  if (del_resp.status == 200) {
    alert("Tu cuenta ha sido eliminada con exito");
    window.location.href = `/`;
  }
}
