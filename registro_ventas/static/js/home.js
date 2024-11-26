
const getLocationBtn = document.getElementById('getLocationBtn');

getLocationBtn.addEventListener('click', (e) => {
    obtenerUbicacion()
})


// Botones de restar y aumentar cantidad de bebidas
const updateQuantityMinusBtn = document.getElementById('updateQuantityMinusBtn');
const updateQuantityPlusBtn = document.getElementById('updateQuantityPlusBtn');

updateQuantityMinusBtn.addEventListener('click', (e) => {
    actualizarCantidad(-1);
})

updateQuantityPlusBtn.addEventListener('click', (e) => {
    actualizarCantidad(1);
})

// Botones de restar y aumentar comida
const updateQuantityFoodMinusBtn = document.getElementById('updateQuantityFoodMinusBtn');
const updateQuantityFoodPlusBtn = document.getElementById('updateQuantityFoodPlusBtn');

updateQuantityFoodMinusBtn.addEventListener('click', (e) => {
    actualizarCantidad_alimentos(-1);
})

updateQuantityFoodPlusBtn.addEventListener('click', (e) => {
    actualizarCantidad_alimentos(1);
})

// Botones de restar y aumentar promociones
const updateQuantityPromoMinusBtn = document.getElementById('updateQuantityPromoMinusBtn');
const updateQuantityPromoPlusBtn = document.getElementById('updateQuantityPromoPlusBtn');

updateQuantityPromoMinusBtn.addEventListener('click', (e) => {
    actualizarCantidad_promociones(-1);
})

updateQuantityPromoPlusBtn.addEventListener('click', (e) => {
    actualizarCantidad_promociones(1);
})


function mostrarFormularios_bebidas() {
    let cantidadBebidas = document.getElementById('cantidad_bebidas').value;
    let contenedor = document.getElementById('formularios_bebidas');
    contenedor.innerHTML = '';

    const categoriaDefault = Object.keys(categoriasBebidas)[0]; // Primera categoría predeterminada
    const subcategoriaDefault = categoriasBebidas[categoriaDefault]?.[0]; // Primera subcategoría de la categoría predeterminada

    for (let i = 0; i < cantidadBebidas; i++) {
        contenedor.innerHTML += `
    <div class="card container-card" id="bebida_${i}">
        <h3>Bebida ${i + 1}</h3>
         <div class="container-form-group">
            <label for="categoria_bebida_${i}">Categoría:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="categoria_bebida_${i}" name="categoria_bebida_${i}" onchange="mostrarSubcategorias(${i})">
                <option value="">Selecciona una categoría</option>
                ${Object.keys(categoriasBebidas).map(cat => `
                    <option value="${cat}" ${cat === categoriaDefault ? 'selected' : ''}>
                        ${cat}
                    </option>`).join('')}
            </select>
        </div>

         <div class="container-form-group">
            <label for="subcategoria_bebida_${i}">Subcategoría:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="subcategoria_bebida_${i}" name="subcategoria_bebida_${i}" onchange="guardarSubcategoria(${i})">
                <option value="">Selecciona una subcategoría</option>
                ${categoriasBebidas[categoriaDefault].map(subcat => `
                    <option value="${subcat}" ${subcat === subcategoriaDefault ? 'selected' : ''}>
                        ${subcat}
                    </option>`).join('')}
            </select>
        </div>

        <div class="container-form-group">
            <label for="tipo_leche_${i}">Tipo de Leche:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="tipo_leche_${i}" name="tipo_leche_${i}">
                <option value="No Aplica">No Aplica</option>
                <option value="Light">Light</option>
                <option value="Deslactosada">Deslactosada</option>
                <option value="Entera">Entera</option>
            </select>
        </div>

        <div class="container-form-group">
            <label for="azucar_${i}">¿Azúcar?:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="azucar_${i}" name="azucar_${i}">
                <option value="Si">Sí</option>
                <option value="No">No</option>
            </select>
        </div>
        
        
        <div class="container-form-group">
            <label for="consideraciones_${i}">Consideraciones:</label>
            <input class="form-control" type="text" id="consideraciones_${i}" name="consideraciones_${i}"><br><br>
        </div>
        
    </div>
`;

        // Seleccionar por defecto categoría y subcategoría para todas las bebidas
        document.getElementById(`categoria_bebida_${i}`).value = categoriaDefault;
        mostrarSubcategorias(i); // Mostrar subcategorías predeterminadas
        document.getElementById(`subcategoria_bebida_${i}`).value = subcategoriaDefault;
    }
}

function mostrarSubcategorias(index) {
    let categoria = document.getElementById(`categoria_bebida_${index}`)?.value;
    let subcategoriaSelect = document.getElementById(`subcategoria_bebida_${index}`);
    subcategoriaSelect.innerHTML = '<option value="">Selecciona una subcategoría</option>';

    if (categoria && categoriasBebidas[categoria]) {
        categoriasBebidas[categoria].forEach(subcategoria => {
            subcategoriaSelect.innerHTML += `<option value="${subcategoria}">${subcategoria}</option>`;
        });

        // Actualizar automáticamente a la primera subcategoría si no está seleccionada
        subcategoriaSelect.value = categoriasBebidas[categoria][0];
    }
}

function guardarSubcategoria(index) {
    let subcategoria = document.getElementById(`subcategoria_bebida_${index}`).value;

    // En caso de que necesites hacer algo en particular cuando cambia, puedes agregar aquí la lógica
    console.log(`Subcategoría actualizada para bebida ${index + 1}: ${subcategoria}`);
}

function actualizarCantidad(incremento) {
    let cantidadBebidasInput = document.getElementById('cantidad_bebidas');
    let cantidadBebidas = parseInt(cantidadBebidasInput.value);

    if (isNaN(cantidadBebidas)) cantidadBebidas = 1;

    if (incremento === 1 || (incremento === -1 && cantidadBebidas >= 0)) {
        cantidadBebidas += incremento;
        cantidadBebidasInput.value = cantidadBebidas;
    }

    mostrarFormularios_bebidas();
}


//---------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------

function mostrarFormularios_alimentos() {
    let cantidadAlimentos = document.getElementById('cantidad_alimentos').value;
    let contenedor = document.getElementById('formularios_alimentos');
    contenedor.innerHTML = '';

    const categoriaDefault = Object.keys(categoriasAlimentos)[0]; // Primera categoría predeterminada
    const subcategoriaDefault = categoriasAlimentos[categoriaDefault]?.[0]; // Primera subcategoría de la categoría predeterminada

    for (let i = 0; i < cantidadAlimentos; i++) {
        contenedor.innerHTML += `
   <div class="card container-card" id="alimento_${i}">
        <h3>Alimento ${i + 1}</h3>
         <div class="container-form-group">
            <label for="categoria_alimento_${i}">Categoría:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="categoria_alimento_${i}" name="categoria_alimento_${i}" onchange="mostrarSubcategorias_alimentos(${i})">
                <option value="">Selecciona una categoría</option>
                ${Object.keys(categoriasAlimentos).map(cat => `
                    <option value="${cat}" ${cat === categoriaDefault ? 'selected' : ''}>
                        ${cat}
                    </option>`).join('')}
            </select>
        </div>
        <div class="container-form-group">
            <label for="subcategoria_alimento_${i}">Subcategoría:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="subcategoria_alimento_${i}" name="subcategoria_alimento_${i}">
                <option value="">Selecciona una subcategoría</option>
                ${categoriasAlimentos[categoriaDefault].map(subcat => `
                    <option value="${subcat}" ${subcat === subcategoriaDefault ? 'selected' : ''}>
                        ${subcat}
                    </option>`).join('')}
            </select>
        </div>
        
        <div class="container-form-group">
            <label for="consideraciones_alimentos_${i}">Consideraciones:</label>
            <input type="text" id="consideraciones_alimentos_${i}" name="consideraciones_alimentos_${i}">
        </div>
    </div>
`;

        // Seleccionar por defecto categoría y subcategoría para todas las bebidas
        document.getElementById(`categoria_alimento_${i}`).value = categoriaDefault;
        mostrarSubcategorias(i); // Mostrar subcategorías predeterminadas
        document.getElementById(`subcategoria_alimento_${i}`).value = subcategoriaDefault;
    }
}

function mostrarSubcategorias_alimentos(index) {
    let categoria = document.getElementById(`categoria_alimento_${index}`).value;
    let subcategoriaSelect = document.getElementById(`subcategoria_alimento_${index}`);
    subcategoriaSelect.innerHTML = '<option value="">Selecciona una subcategoría</option>';

    if (categoria && categoriasAlimentos[categoria]) {
        categoriasAlimentos[categoria].forEach(subcategoria => {
            subcategoriaSelect.innerHTML += `<option value="${subcategoria}">${subcategoria}</option>`;
        });
    }
}

function actualizarCantidad_alimentos(incremento) {
    let cantidadAlimentosInput = document.getElementById('cantidad_alimentos');
    let cantidadAlimentos = parseInt(cantidadAlimentosInput.value);

    if (isNaN(cantidadAlimentos)) cantidadAlimentos = 1;

    if (incremento === 1 || (incremento === -1 && cantidadAlimentos >= 0)) {
        cantidadAlimentos += incremento;
        cantidadAlimentosInput.value = cantidadAlimentos;
    }

    mostrarFormularios_alimentos();
}


function mostrarFormularios_promociones() {
    let cantidadPromociones = document.getElementById('cantidad_promociones').value;
    let contenedor = document.getElementById('formularios_promociones');
    contenedor.innerHTML = '';

    const categoriaDefault = Object.keys(categoriasPromociones)[0]; // Primera categoría predeterminada
    const subcategoriaDefault = categoriasPromociones[categoriaDefault]?.[0]; // Primera subcategoría de la categoría predeterminada

    for (let i = 0; i < cantidadPromociones; i++) {
        contenedor.innerHTML += `
    <div class="card container-card" id="promocion_${i}">
        <h3>Promocion ${i + 1}</h3>
         <div class="container-form-group">
            <label for="categoria_promocion_${i}">Categoría:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="categoria_promocion_${i}" name="categoria_promocion_${i}" onchange="mostrarSubcategorias_promociones(${i})">
                <option value="">Selecciona una categoría</option>
                ${Object.keys(categoriasPromociones).map(cat => `
                    <option value="${cat}" ${cat === categoriaDefault ? 'selected' : ''}>
                        ${cat}
                    </option>`).join('')}
            </select>
        </div>
        
        <div class="container-form-group">
            <label for="subcategoria_promocion_${i}">Subcategoría:</label>
            <select class="btn btn-outline-secondary dropdown-toggle" id="subcategoria_promocion_${i}" name="subcategoria_promocion_${i}">
                <option value="">Selecciona una subcategoría</option>
                ${categoriasPromociones[categoriaDefault].map(subcat => `
                    <option value="${subcat}" ${subcat === subcategoriaDefault ? 'selected' : ''}>
                        ${subcat}
                    </option>`).join('')}
            </select>
        </div>
          <div class="container-form-group">
            <label for="consideraciones_promociones_${i}">Consideraciones:</label>
            <input type="text" id="consideraciones_promociones_${i}" name="consideraciones_promociones_${i}"><br><br>
          </div>
        
    </div>
`;

        // Seleccionar por defecto categoría y subcategoría para todas las bebidas
        document.getElementById(`categoria_promocion_${i}`).value = categoriaDefault;
        mostrarSubcategorias(i); // Mostrar subcategorías predeterminadas
        document.getElementById(`subcategoria_promocion_${i}`).value = subcategoriaDefault;
    }
}

function mostrarSubcategorias_promociones(index) {
    let categoria = document.getElementById(`categoria_promocion_${index}`).value;
    let subcategoriaSelect = document.getElementById(`subcategoria_promocion_${index}`);
    subcategoriaSelect.innerHTML = '<option value="">Selecciona una subcategoría</option>';

    if (categoria && categoriasPromociones[categoria]) {
        categoriasPromociones[categoria].forEach(subcategoria => {
            subcategoriaSelect.innerHTML += `<option value="${subcategoria}">${subcategoria}</option>`;
        });
    }
}

function actualizarCantidad_promociones(incremento) {
    let cantidadPromocionesInput = document.getElementById('cantidad_promociones');
    let cantidadPromociones = parseInt(cantidadPromocionesInput.value);

    if (isNaN(cantidadPromociones)) cantidadPromociones = 1;

    if (incremento === 1 || (incremento === -1 && cantidadPromociones >= 0)) {
        cantidadPromociones += incremento;
        cantidadPromocionesInput.value = cantidadPromociones;
    }

    mostrarFormularios_promociones();
}


function obtenerUbicacion() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const latitud = position.coords.latitude;
                const longitud = position.coords.longitude;

                fetch("/guardar_ubicacion", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ latitud, longitud })
                })
                    .then(response => response.json())
                    .then(data => {
                        alert("Ubicación enviada correctamente: " + data.message);
                    })
                    .catch(error => {
                        console.error("Error al enviar la ubicación:", error);
                    });
            },
            function (error) {
                console.error("Error obteniendo la ubicación:", error);
            }
        );
    } else {
        alert("La geolocalización no está soportada por este navegador.");
    }
}