"use strict";

const state = {
  current: "estudiantes",
  data: {
    carreras: [],
    cursos: [],
    estudiantes: [],
    inscripciones: [],
  },
  dialog: {
    entity: null,
    item: null,
    fields: [],
  },
};

const PUEDE_ESCRIBIR = document.body.dataset.role === "admin";

const ENTITIES = {
  estudiantes: {
    singular: "estudiante",
    title: "Estudiantes",
    subtitle: "Registra y actualiza los datos de los estudiantes.",
    endpoint: "/estudiantes",
    columns: [
      { label: "ID", value: (item) => item.id },
      { label: "Nombre", value: (item) => `${item.nombre} ${item.apellido}` },
      { label: "Email", value: (item) => item.email },
      { label: "Carrera", value: (item) => item.carrera },
    ],
    fields: () => [
      {
        name: "nombre",
        label: "Nombre",
        type: "text",
        required: true,
        placeholder: "Ana",
      },
      {
        name: "apellido",
        label: "Apellido",
        type: "text",
        required: true,
        placeholder: "Pérez",
      },
      {
        name: "email",
        label: "Email",
        type: "email",
        required: true,
        placeholder: "ana@example.com",
      },
      {
        name: "carrera_id",
        label: "Carrera",
        type: "select",
        required: true,
        options: () =>
          state.data.carreras.map((carrera) => ({
            value: carrera.id,
            label: carrera.nombre,
          })),
      },
    ],
  },

  carreras: {
    singular: "carrera",
    title: "Carreras",
    subtitle: "Administra las carreras y sus facultades.",
    endpoint: "/carreras",
    columns: [
      { label: "ID", value: (item) => item.id },
      { label: "Nombre", value: (item) => item.nombre },
      { label: "Facultad", value: (item) => item.facultad },
      { label: "Estudiantes", value: (item) => item.total_estudiantes },
    ],
    fields: [
      {
        name: "nombre",
        label: "Nombre",
        type: "text",
        required: true,
        placeholder: "Ingeniería de Software",
      },
      {
        name: "facultad",
        label: "Facultad",
        type: "text",
        required: true,
        placeholder: "Ingeniería",
      },
    ],
  },

  cursos: {
    singular: "curso",
    title: "Cursos",
    subtitle: "Gestiona la oferta académica y sus responsables.",
    endpoint: "/cursos",
    columns: [
      { label: "ID", value: (item) => item.id },
      { label: "Código", value: (item) => item.codigo },
      { label: "Nombre", value: (item) => item.nombre },
      { label: "Créditos", value: (item) => item.creditos },
      { label: "Profesor", value: (item) => item.profesor },
    ],
    fields: [
      {
        name: "codigo",
        label: "Código",
        type: "text",
        required: true,
        placeholder: "DEVOPS-01",
      },
      {
        name: "nombre",
        label: "Nombre",
        type: "text",
        required: true,
        placeholder: "Fundamentos de DevOps",
      },
      {
        name: "creditos",
        label: "Créditos",
        type: "number",
        required: true,
        min: 1,
        step: 1,
        placeholder: "4",
      },
      {
        name: "profesor",
        label: "Profesor",
        type: "text",
        required: true,
        placeholder: "Iván Guerra",
      },
    ],
  },

  inscripciones: {
    singular: "inscripción",
    title: "Inscripciones",
    subtitle: "Asocia estudiantes a cursos y registra sus notas.",
    endpoint: "/inscripciones",
    columns: [
      { label: "ID", value: (item) => item.id },
      {
        label: "Estudiante",
        value: (item) => nombreEstudiante(item.estudiante_id),
      },
      { label: "Curso", value: (item) => nombreCurso(item.curso_id) },
      { label: "Periodo", value: (item) => item.periodo },
      {
        label: "Nota",
        value: (item) => (item.nota === null ? "Sin nota" : item.nota),
      },
    ],
    fields: (item) => [
      {
        name: "estudiante_id",
        label: "Estudiante",
        type: "select",
        required: true,
        disabled: Boolean(item),
        options: () =>
          state.data.estudiantes.map((estudiante) => ({
            value: estudiante.id,
            label: `${estudiante.nombre} ${estudiante.apellido}`,
          })),
      },
      {
        name: "curso_id",
        label: "Curso",
        type: "select",
        required: true,
        disabled: Boolean(item),
        options: () =>
          state.data.cursos.map((curso) => ({
            value: curso.id,
            label: `${curso.codigo} · ${curso.nombre}`,
          })),
      },
      {
        name: "periodo",
        label: "Periodo",
        type: "text",
        required: true,
        placeholder: "2026-II",
      },
      {
        name: "nota",
        label: "Nota (0 - 20)",
        type: "number",
        required: false,
        min: 0,
        max: 20,
        step: 0.01,
        placeholder: "Opcional",
      },
    ],
  },
};

const $ = (selector) => document.querySelector(selector);

function capitalizar(texto) {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function nombreEstudiante(id) {
  const estudiante = state.data.estudiantes.find((item) => item.id === id);
  return estudiante ? `${estudiante.nombre} ${estudiante.apellido}` : `#${id}`;
}

function nombreCurso(id) {
  const curso = state.data.cursos.find((item) => item.id === id);
  return curso ? `${curso.codigo} · ${curso.nombre}` : `#${id}`;
}

function describir(entity, item) {
  if (entity === "estudiantes") {
    return `${item.nombre} ${item.apellido}`;
  }
  if (entity === "carreras" || entity === "cursos") {
    return item.nombre;
  }
  return `#${item.id}`;
}

async function api(path, { method = "GET", body } = {}) {
  const response = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body,
  });

  if (response.status === 204) {
    return null;
  }

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Sesión expirada. Vuelve a iniciar sesión.");
  }

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.error || `Error HTTP ${response.status}`);
  }

  return payload;
}

async function refreshAll() {
  const [carreras, cursos, estudiantes, inscripciones] = await Promise.all([
    api("/carreras"),
    api("/cursos"),
    api("/estudiantes"),
    api("/inscripciones"),
  ]);

  state.data = { carreras, cursos, estudiantes, inscripciones };
  render();
}

function render() {
  document.querySelectorAll(".tab").forEach((tab) => {
    const entity = tab.dataset.entity;
    const activa = entity === state.current;
    tab.classList.toggle("is-active", activa);
    tab.setAttribute("aria-selected", activa ? "true" : "false");
    tab.querySelector(".count").textContent = state.data[entity].length;
  });

  const total = Object.values(state.data).reduce(
    (suma, coleccion) => suma + coleccion.length,
    0
  );
  $("#total-registros").textContent = total;

  renderTabla();
}

function renderTabla() {
  const config = ENTITIES[state.current];
  const items = state.data[state.current];

  $("#panel-title").textContent = config.title;
  $("#panel-subtitle").textContent = config.subtitle;
  $("#create-btn").hidden = !PUEDE_ESCRIBIR;
  $("#create-btn").textContent = `+ Nuevo ${config.singular}`;

  const head = $("#table-head");
  const body = $("#table-body");
  head.replaceChildren();
  body.replaceChildren();

  const filaCabecera = document.createElement("tr");
  config.columns.forEach((column) => {
    const th = document.createElement("th");
    th.textContent = column.label;
    filaCabecera.appendChild(th);
  });
  if (PUEDE_ESCRIBIR) {
    const thAcciones = document.createElement("th");
    thAcciones.textContent = "Acciones";
    thAcciones.className = "actions-col";
    filaCabecera.appendChild(thAcciones);
  }
  head.appendChild(filaCabecera);

  $("#empty-state").hidden = items.length > 0;
  $("#empty-create-btn").hidden = !PUEDE_ESCRIBIR;

  items.forEach((item) => {
    const fila = document.createElement("tr");

    config.columns.forEach((column) => {
      const td = document.createElement("td");
      const valor = column.value(item);
      td.textContent =
        valor === null || valor === undefined || valor === "" ? "—" : valor;
      fila.appendChild(td);
    });

    if (PUEDE_ESCRIBIR) {
      const tdAcciones = document.createElement("td");
      tdAcciones.className = "actions";

      const botonEditar = document.createElement("button");
      botonEditar.type = "button";
      botonEditar.className = "btn btn-small btn-ghost";
      botonEditar.textContent = "Editar";
      botonEditar.addEventListener("click", () =>
        abrirDialogo(state.current, item)
      );

      const botonEliminar = document.createElement("button");
      botonEliminar.type = "button";
      botonEliminar.className = "btn btn-small btn-danger-ghost";
      botonEliminar.textContent = "Eliminar";
      botonEliminar.addEventListener("click", () =>
        eliminarRegistro(state.current, item)
      );

      tdAcciones.append(botonEditar, botonEliminar);
      fila.appendChild(tdAcciones);
    }

    body.appendChild(fila);
  });
}

function abrirDialogo(entity, item = null) {
  const config = ENTITIES[entity];
  const fields = typeof config.fields === "function"
    ? config.fields(item)
    : config.fields;

  state.dialog = { entity, item, fields };

  $("#modal-title").textContent = item
    ? `Editar ${config.singular}`
    : `Nuevo ${config.singular}`;

  const contenedor = $("#form-fields");
  contenedor.replaceChildren();

  fields.forEach((field) => {
    const wrapper = document.createElement("label");
    wrapper.className = "field";

    const etiqueta = document.createElement("span");
    etiqueta.textContent = field.label + (field.required ? " *" : "");
    wrapper.appendChild(etiqueta);

    let input;
    if (field.type === "select") {
      input = document.createElement("select");
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Selecciona una opción";
      input.appendChild(placeholder);

      field.options().forEach((option) => {
        const elemento = document.createElement("option");
        elemento.value = option.value;
        elemento.textContent = option.label;
        input.appendChild(elemento);
      });
    } else {
      input = document.createElement("input");
      input.type = field.type;
      if (field.placeholder) input.placeholder = field.placeholder;
      if (field.min !== undefined) input.min = field.min;
      if (field.max !== undefined) input.max = field.max;
      if (field.step !== undefined) input.step = field.step;
    }

    input.id = `field-${field.name}`;
    input.name = field.name;
    input.required = Boolean(field.required);
    input.disabled = Boolean(field.disabled);

    if (item && item[field.name] !== null && item[field.name] !== undefined) {
      input.value = item[field.name];
    }

    wrapper.appendChild(input);
    contenedor.appendChild(wrapper);
  });

  const dialogo = $("#entity-dialog");
  if (!dialogo.open) {
    dialogo.showModal();
  }

  const primero = contenedor.querySelector(
    "input:not([disabled]), select:not([disabled])"
  );
  if (primero) primero.focus();
}

function cerrarDialogo() {
  const dialogo = $("#entity-dialog");
  if (dialogo.open) dialogo.close();
}

async function guardar(event) {
  event.preventDefault();

  const { entity, item, fields } = state.dialog;
  const config = ENTITIES[entity];
  const payload = {};

  for (const field of fields) {
    if (field.disabled) continue;

    const input = document.getElementById(`field-${field.name}`);
    let valor = input.value;

    if (field.type === "number" || field.name.endsWith("_id")) {
      valor = valor === "" ? null : Number(valor);
    } else if (typeof valor === "string") {
      valor = valor.trim();
    }

    payload[field.name] = valor;
  }

  try {
    if (item) {
      await api(`${config.endpoint}/${item.id}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      mostrarToast(`${capitalizar(config.singular)} actualizado correctamente.`);
    } else {
      await api(config.endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      mostrarToast(`${capitalizar(config.singular)} creado correctamente.`);
    }

    cerrarDialogo();
    await refreshAll();
  } catch (error) {
    mostrarToast(error.message, "error");
  }
}

async function eliminarRegistro(entity, item) {
  const config = ENTITIES[entity];
  const etiqueta = describir(entity, item);

  if (!window.confirm(`¿Eliminar ${config.singular} "${etiqueta}"?`)) {
    return;
  }

  try {
    await api(`${config.endpoint}/${item.id}`, { method: "DELETE" });
    mostrarToast(`${capitalizar(config.singular)} eliminado correctamente.`);
    await refreshAll();
  } catch (error) {
    mostrarToast(error.message, "error");
  }
}

async function verificarSalud() {
  const badge = $("#health-badge");
  try {
    await api("/health");
    badge.className = "badge badge-ok";
    badge.innerHTML = '<span class="dot"></span> API y BD en línea';
  } catch {
    badge.className = "badge badge-error";
    badge.innerHTML = '<span class="dot"></span> Sin conexión';
  }
}

let toastTimer;

function mostrarToast(mensaje, tipo = "success") {
  const toast = $("#toast");
  toast.textContent = mensaje;
  toast.className = `toast toast-${tipo}`;
  toast.hidden = false;

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.hidden = true;
  }, 4000);
}

function enlazarEventos() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      state.current = tab.dataset.entity;
      render();
    });
  });

  $("#create-btn").addEventListener("click", () =>
    abrirDialogo(state.current)
  );
  $("#empty-create-btn").addEventListener("click", () =>
    abrirDialogo(state.current)
  );

  $("#entity-form").addEventListener("submit", guardar);
  $("#cancel-btn").addEventListener("click", cerrarDialogo);
  $("#close-modal").addEventListener("click", cerrarDialogo);

  $("#refresh-btn").addEventListener("click", async () => {
    try {
      await Promise.all([refreshAll(), verificarSalud()]);
      mostrarToast("Datos actualizados.");
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  enlazarEventos();
  render();

  try {
    await refreshAll();
  } catch (error) {
    mostrarToast(error.message, "error");
  }

  await verificarSalud();
});
