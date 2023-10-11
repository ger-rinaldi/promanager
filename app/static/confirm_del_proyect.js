async function delete_resource() {
  const resource_name_element = document.getElementById("nombre");
  const resource_id = document.getElementById("id_recurso").value;
  const resource_name = resource_name_element.value;

  const confirm_msg = `¿Segurx quieres borrar ${resource_name}?\nPresiona OK para continuar...`;
  const validate_msg = `Para eliminar ${resource_name} ingresa su nombre:`;

  if (confirm(confirm_msg)) {
    const confirmed_name = prompt(validate_msg);
    if (confirmed_name === resource_name) {
      await fetch(`/usuario/proyecto/${resource_id}/eliminar`, { method: "POST" });
      window.location.href = "/usuario/proyecto";
    } else {
      alert("Nombre ingresado erróneo. Vuelve a intentarlo.");
    }
  }
}