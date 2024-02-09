function get_api_url(url = window.location.toString(), remove_leaf = false) {
  let resource_url;

  if (remove_leaf) {
    resource_url = url.match(/\/\/[^/]+(\/.*)\/.*/)[1];
  } else {
    resource_url = url.match(/\/\/[^/]+(\/.*)/)[1];
  }

  const api_url = "/api" + resource_url;

  return api_url;
}

export { get_api_url };
