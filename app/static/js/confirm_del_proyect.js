async function delete_resource() {
  const str_url = window.location.toString();
  const split_url = str_url.split("/");

  username = split_url[split_url.indexOf("usuario") + 1];

  const resource_name_element = document.getElementById("nombre");
  const resource_id = document.getElementById("id_recurso").value;
  const resource_name = resource_name_element.value;

  const confirm_msg = `¿Segurx quieres borrar ${resource_name}?\nPresiona OK para continuar...`;
  const validate_msg = `Para eliminar ${resource_name} ingresa su nombre:`;

  if (!confirm(confirm_msg)) {
    return;
  }

  const confirmed_name = prompt(validate_msg);

  if (confirmed_name !== resource_name) {
    alert("Nombre ingresado erróneo. Vuelve a intentarlo.");
    return;
  }

  const delete_resp = await fetch(
    `/api/usuario/${username}/proyecto/${resource_id}/eliminar`,
    { method: "POST" }
  );

  if (delete_resp.status == 200) {
    alert(`El proyecto '${resource_name}' ha sido eliminado exitosamente.`);
  } else {
    alert(
      "Hubo un problema inesperado, si el proyecto no fue eliminado vuelve a intentar en un momento."
    );
  }
  window.location.href = `/usuario/${username}/proyecto`;
}
