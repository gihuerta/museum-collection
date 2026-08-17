import axios from "axios";

const client = axios.create({ baseURL: "/api" });

export const getItems = (params) => client.get("/items", { params });
export const getItem = (id) => client.get(`/items/${id}`);
export const createItem = (data) => client.post("/items", data);
export const updateItem = (id, data) => client.put(`/items/${id}`, data);
export const deleteItem = (id) => client.delete(`/items/${id}`);
export const importCSV = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return client.post("/items/import", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
export const uploadItemImage = (id, file) => {
  const formData = new FormData();
  formData.append("image", file);
  return client.post(`/items/${id}/image`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
export const deleteItemImage = (id) => client.delete(`/items/${id}/image`);
export const validateCatalog = () => client.get("/items/validate");
export const exportCSVUrl = "/api/items/export";

export default client;
