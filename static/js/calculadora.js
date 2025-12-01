/**
 * Función para alternar la visibilidad de los detalles del curso
 */
function toggleCourse(header) {
    const content = header.nextElementSibling;
    content.classList.toggle('open');
    const icon = header.querySelector('.fa-chevron-down, .fa-chevron-up');
    if (content.classList.contains('open')) {
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');
    } else {
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
    }
}

/**
 * Función principal para calcular el promedio y la nota necesaria
 * Se ejecuta cada vez que el usuario edita una nota
 */
function calculateAverage(element) {
    const courseCard = element.closest('.course-card');
    const rows = courseCard.querySelectorAll('.evaluacion-row');
    let totalWeightedScore = 0;
    let totalWeight = 0;
    let hasError = false;

    // Reset errors
    rows.forEach(row => {
        const gradeInput = row.querySelector('.grade-pill');
        if (gradeInput) {
            gradeInput.style.borderColor = 'transparent';
        }
    });

    rows.forEach(row => {
        const weight = parseFloat(row.dataset.ponderacion);
        const gradeInput = row.querySelector('.grade-pill');
        if (!gradeInput) return;

        let gradeValue = parseFloat(gradeInput.value);

        // Manejar valor vacío
        if (isNaN(gradeValue) || gradeInput.value === '') {
            gradeInput.classList.add('empty');
            return;
        } else {
            gradeInput.classList.remove('empty');
        }

        // Validar rango de nota (10 a 70)
        if (gradeValue > 70 || gradeValue < 10) {
            gradeInput.style.borderColor = 'var(--danger-color)';
            gradeInput.style.borderWidth = '2px';
            gradeInput.style.borderStyle = 'solid';
            hasError = true;
            return;
        }

        totalWeightedScore += gradeValue * (weight / 100);
        totalWeight += weight;
    });

    const averageDisplay = courseCard.querySelector('.promedio-actual');
    const repeteSection = courseCard.querySelector('.repete-ramo-section');
    const resultadoDiv = courseCard.querySelector('.resultado-ramo');

    // Obtener nota objetivo
    const targetGrade = parseFloat(courseCard.dataset.notaObjetivo) * 10; // Escala 10-70

    if (totalWeight > 0) {
        const average = totalWeightedScore / (totalWeight / 100);
        averageDisplay.innerText = average.toFixed(1);

        // Actualizar promedio en el header también
        const headerPromedio = courseCard.querySelector('.header-promedio');
        if (headerPromedio) {
            headerPromedio.textContent = average.toFixed(1);
        }

        let finalAverage = average;

        // Verificar si necesita repete (promedio < nota objetivo)
        if (average < targetGrade) {
            if (repeteSection) {
                repeteSection.style.display = 'block';
                // Actualizar mensaje del repete con la nota objetivo mostrada en pantalla
                const repeteMensaje = repeteSection.querySelector('.repete-mensaje');
                const notaObjetivoDisplay = courseCard.querySelector('.nota-objetivo-display');
                const notaObjetivoText = notaObjetivoDisplay ? notaObjetivoDisplay.textContent : targetGrade.toFixed(1);
                if (repeteMensaje) {
                    repeteMensaje.textContent = `Promedio bajo ${notaObjetivoText}. Deberás dar el Repete.`;
                }
            }

            const repeteGradeInput = courseCard.querySelector('.repete-grade-input');
            const repeteModeSelect = courseCard.querySelector('.repete-mode-select');
            const repeteGrade = repeteGradeInput ? parseFloat(repeteGradeInput.value) : NaN;
            const repeteMode = repeteModeSelect ? repeteModeSelect.value : 'lowest';

            if (!isNaN(repeteGrade) && repeteGrade >= 10 && repeteGrade <= 70) {
                // Calcular nuevo promedio con repete
                if (repeteMode === 'lowest') {
                    // Reemplazar la nota más baja
                    let lowestGrade = 70;
                    let lowestWeight = 0;

                    rows.forEach(row => {
                        const gradeInput = row.querySelector('.grade-pill');
                        if (!gradeInput) return;
                        const grade = parseFloat(gradeInput.value);
                        const weight = parseFloat(row.dataset.ponderacion);

                        if (!isNaN(grade) && !isNaN(weight) && grade < lowestGrade) {
                            lowestGrade = grade;
                            lowestWeight = weight;
                        }
                    });

                    if (lowestWeight > 0) {
                        totalWeightedScore = totalWeightedScore - (lowestGrade * (lowestWeight / 100)) + (repeteGrade * (lowestWeight / 100));
                        finalAverage = totalWeightedScore / (totalWeight / 100);
                    }
                } else if (repeteMode === 'highest_weight') {
                    // Reemplazar la evaluación con mayor ponderación
                    let highestWeight = 0;
                    let highestGrade = 0;

                    rows.forEach(row => {
                        const gradeInput = row.querySelector('.grade-pill');
                        if (!gradeInput) return;
                        const grade = parseFloat(gradeInput.value);
                        const weight = parseFloat(row.dataset.ponderacion);

                        if (!isNaN(weight) && weight > highestWeight) {
                            highestWeight = weight;
                            highestGrade = grade;
                        }
                    });

                    if (highestWeight > 0) {
                        totalWeightedScore = totalWeightedScore - (highestGrade * (highestWeight / 100)) + (repeteGrade * (highestWeight / 100));
                        finalAverage = totalWeightedScore / (totalWeight / 100);
                    }
                }

                // Actualizar promedio final
                const promedioFinalDisplay = courseCard.querySelector('.promedio-final');
                if (promedioFinalDisplay) {
                    promedioFinalDisplay.textContent = finalAverage.toFixed(1);
                }

                // Mostrar mensaje de resultado en sección de repete
                mostrarResultadoEnRepete(courseCard, finalAverage, targetGrade);
            } else {
                const promedioFinalDisplay = courseCard.querySelector('.promedio-final');
                if (promedioFinalDisplay) {
                    promedioFinalDisplay.textContent = average.toFixed(1);
                }
            }
        } else {
            if (repeteSection) repeteSection.style.display = 'none';
        }

        // Mostrar mensaje de resultado (solo si tiene suficiente progreso o con repete)
        if (totalWeight >= 100 || (repeteSection && repeteSection.style.display !== 'none' && courseCard.querySelector('.repete-grade-input') && !isNaN(parseFloat(courseCard.querySelector('.repete-grade-input').value)))) {
            mostrarResultadoRamo(courseCard, finalAverage, targetGrade);
        } else {
            // Ocultar mensaje de resultado si no cumple condiciones
            if (resultadoDiv) {
                resultadoDiv.style.display = 'none';
            }
        }
    } else {
        averageDisplay.innerText = '--';
        if (repeteSection) repeteSection.style.display = 'none';
        if (resultadoDiv) {
            resultadoDiv.style.display = 'none';
        }
    }
}

/**
 * Mostrar mensaje de resultado dentro de la sección de repete
 */
function mostrarResultadoEnRepete(courseCard, promedioFinal, notaObjetivo) {
    let resultadoDiv = courseCard.querySelector('.resultado-ramo-repete');

    if (!resultadoDiv) return;

    resultadoDiv.style.display = 'block';

    if (promedioFinal >= notaObjetivo) {
        resultadoDiv.style.backgroundColor = '#d4edda';
        resultadoDiv.style.color = '#155724';
        resultadoDiv.innerHTML = '<i class="fas fa-smile-beam" style="margin-right: 8px;"></i>¡Felicidades! Pasaste el ramo';
    } else {
        resultadoDiv.style.backgroundColor = '#f8d7da';
        resultadoDiv.style.color = '#721c24';
        resultadoDiv.innerHTML = '<i class="fas fa-sad-tear" style="margin-right: 8px;"></i>No alcanzaste la nota necesaria';
    }
}

/**
 * Agregar event listeners para los inputs de repete
 */
function setupRepeteListeners() {
    document.querySelectorAll('.repete-grade-input, .repete-mode-select').forEach(input => {
        input.addEventListener('input', function() {
            const courseCard = this.closest('.course-card');
            const firstGrade = courseCard.querySelector('.grade-pill');
            if (firstGrade) {
                calculateAverage(firstGrade);
            }
        });

        input.addEventListener('change', function() {
            const courseCard = this.closest('.course-card');
            const firstGrade = courseCard.querySelector('.grade-pill');
            if (firstGrade) {
                calculateAverage(firstGrade);
            }
        });
    });
}

/**
 * Mostrar mensaje de resultado para un ramo específico
 */
function mostrarResultadoRamo(courseCard, promedioFinal, notaObjetivo) {
    let resultadoDiv = courseCard.querySelector('.resultado-ramo');

    if (!resultadoDiv) {
        resultadoDiv = document.createElement('div');
        resultadoDiv.className = 'resultado-ramo';
        resultadoDiv.style.cssText = 'margin-top: 15px; padding: 12px; border-radius: var(--radius-sm); text-align: center; font-weight: 600;';

        const summarySection = courseCard.querySelector('.summary-section');
        if (summarySection) {
            summarySection.appendChild(resultadoDiv);
        }
    }

    // Ambos valores ya están en escala 10-70
    // promedioFinal: ya está en escala 10-70
    // notaObjetivo: ya está en escala 10-70 (viene de targetGrade)
    if (promedioFinal >= notaObjetivo) {
        resultadoDiv.style.backgroundColor = '#d4edda';
        resultadoDiv.style.color = '#155724';
        resultadoDiv.innerHTML = '<i class="fas fa-smile-beam" style="margin-right: 8px;"></i>¡Felicidades! Pasaste el ramo';
    } else {
        resultadoDiv.style.backgroundColor = '#f8d7da';
        resultadoDiv.style.color = '#721c24';
        resultadoDiv.innerHTML = '<i class="fas fa-sad-tear" style="margin-right: 8px;"></i>No alcanzaste la nota necesaria';
    }
}

/**
 * Actualizar la nota objetivo de un ramo
 */
function toggleNotaObjetivoRamo(selectElement) {
    const courseCard = selectElement.closest('.course-card');
    const customContainer = courseCard.querySelector('.nota-objetivo-custom-container');
    const tipo = selectElement.value;
    const ramoId = selectElement.getAttribute('data-ramo-id');

    if (tipo === 'custom') {
        customContainer.style.display = 'block';
    } else {
        // Hide and clear the custom input when switching back to "pasar"
        if (customContainer) {
            const input = customContainer.querySelector('.nota-objetivo-custom-input');
            if (input) {
                input.value = '';
            }
            customContainer.style.display = 'none';
        }
        // Si selecciona "pasar es pasar", guardar 39.5
        guardarNotaObjetivo(ramoId, 39.5, courseCard);
    }
}

function updateNotaObjetivoCustom(inputElement) {
    const courseCard = inputElement.closest('.course-card');
    // Clamp input to valid range immediately
    let customValue = parseFloat(inputElement.value);
    if (!isNaN(customValue)) {
        if (customValue > 70) { customValue = 70; inputElement.value = 70; }
        if (customValue < 10) { customValue = 10; inputElement.value = 10; }
    }
    const ramoId = inputElement.getAttribute('data-ramo-id');

    if (!isNaN(customValue) && customValue >= 10 && customValue <= 70) {
        guardarNotaObjetivo(ramoId, customValue, courseCard);
    } else {
        // invalid value => if it's numeric it's already clamped above, call guardar
        if (!isNaN(customValue)) {
            guardarNotaObjetivo(ramoId, customValue, courseCard);
        }
    }
}

function guardarNotaObjetivo(ramoId, notaObjetivo, courseCard) {
    console.log(`Guardando nota objetivo ${notaObjetivo} para ramo ${ramoId}`);

    fetch(`/save_nota_objetivo/${ramoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ nota_objetivo: notaObjetivo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Nota objetivo guardada:', data.nota_objetivo);

            // Actualizar el data attribute (en escala 1-7)
            courseCard.dataset.notaObjetivo = data.nota_objetivo;

            // Actualizar la visualización de la meta (en escala 10-70)
            const metaDisplay = courseCard.querySelector('.nota-objetivo-display');
            if (metaDisplay) {
                metaDisplay.textContent = notaObjetivo.toFixed(1);
            }

            // Recalcular con la nueva meta
            const firstGradeInput = courseCard.querySelector('.grade-pill');
            if (firstGradeInput) {
                calculateAverage(firstGradeInput);
            }
        } else {
            console.error('Error al guardar nota objetivo:', data.error);
        }
    })
    .catch(error => {
        console.error('Error de red:', error);
    });
}

/**
 * Calcular promedio para ramos históricos (sin repete)
 */
function calculateAverageHistorico(element) {
    const courseCard = element.closest('.course-card');
    const rows = courseCard.querySelectorAll('.evaluacion-row');
    let totalWeightedScore = 0;
    let totalWeight = 0;

    // Reset errors
    rows.forEach(row => {
        const gradeInput = row.querySelector('.grade-pill');
        if (gradeInput) {
            gradeInput.style.borderColor = 'transparent';
        }
    });

    rows.forEach(row => {
        const weight = parseFloat(row.dataset.ponderacion);
        const gradeInput = row.querySelector('.grade-pill');
        if (!gradeInput) return;

        let gradeValue = parseFloat(gradeInput.value);

        // Manejar valor vacío
        if (isNaN(gradeValue) || gradeInput.value === '') {
            gradeInput.classList.add('empty');
            return;
        } else {
            gradeInput.classList.remove('empty');
        }

        // Validar rango de nota (10 a 70)
        if (gradeValue > 70 || gradeValue < 10) {
            gradeInput.style.borderColor = 'var(--danger-color)';
            gradeInput.style.borderWidth = '2px';
            gradeInput.style.borderStyle = 'solid';
            return;
        }

        totalWeightedScore += gradeValue * (weight / 100);
        totalWeight += weight;
    });

    // Actualizar promedio
    if (totalWeight > 0) {
        const average = totalWeightedScore / (totalWeight / 100);

        // Actualizar promedio en el resumen
        const averageDisplay = courseCard.querySelector('.summary-value');
        if (averageDisplay) {
            averageDisplay.innerText = average.toFixed(1);
        }

        // Actualizar promedio en el header
        const headerPromedio = courseCard.querySelector('.header-promedio-historico');
        if (headerPromedio) {
            headerPromedio.textContent = average.toFixed(1);
        }
    }
}

// Cálculo inicial al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.course-card').forEach(card => {
        // Disparar cálculo para cada tarjeta para establecer estado inicial
        const firstGrade = card.querySelector('.grade-pill');
        if (firstGrade) calculateAverage(firstGrade);
    });

    // Configurar listeners para repete
    setupRepeteListeners();
    // Configurar clamps para inputs de nota objetivo (guest y por ramo)
    setupNotaObjetivoClamps();
    
    // Global input clamping and validation: grades (10-70), weights (0-100)
    document.body.addEventListener('input', function(e) {
        const tgt = e.target;
        if (!tgt) return;

        // grade inputs used across templates
        // Use explicit class `percent-input` for attendance/percentage fields
        const isPercentField = tgt.classList && tgt.classList.contains('percent-input');

        if (tgt.classList && (tgt.classList.contains('grade-pill') || (tgt.classList.contains('grade-input') && !isPercentField))) {
            let v = parseFloat(tgt.value);
            if (isNaN(v)) return;
            if (v > 70) tgt.value = 70;
            if (v < 10) {
                // allow typing small numbers, only enforce minimum when blurred
                // but keep a hard floor at 0 in case someone enters negative
                if (v < 0) tgt.value = 10;
            }
        }

        // Weight inputs (0-100). Also include `percent-input` fields (asistencia)
        if (tgt.classList && (tgt.classList.contains('weight-input') || isPercentField)) {
            let w = parseFloat(tgt.value);
            if (isNaN(w)) return;
            if (w > 100) tgt.value = 100;
            if (w < 0) tgt.value = 0;
        }
    }, { capture: true });
});

/**
 * Función para cambiar entre pestañas (Período actual / Históricas)
 */
function switchTab(tabName) {
    // Actualizar tabs activos
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
        if ((tabName === 'actual' && tab.textContent.includes('actual')) ||
            (tabName === 'historicas' && tab.textContent.includes('Históricas'))) {
            tab.classList.add('active');
        }
    });

    // Mostrar/ocultar contenedores
    const ramosActuales = document.getElementById('ramos-list');
    const ramosHistoricos = document.getElementById('ramos-historicos-list');

    if (tabName === 'actual') {
        if (ramosActuales) ramosActuales.style.display = 'block';
        if (ramosHistoricos) ramosHistoricos.style.display = 'none';
    } else if (tabName === 'historicas') {
        if (ramosActuales) ramosActuales.style.display = 'none';
        if (ramosHistoricos) ramosHistoricos.style.display = 'block';
    }
}

/**
 * Calculadora de Invitado - Funciones para la calculadora rápida
 */
function toggleNotaObjetivoInput() {
    const tipo = document.getElementById('nota-objetivo-tipo').value;
    const customContainer = document.getElementById('nota-objetivo-custom-container');

    if (tipo === 'custom') {
        customContainer.style.display = 'block';
    } else {
        // Hide and clear the custom input when switching to "pasar"
        const input = document.getElementById('nota-objetivo-custom');
        if (input) input.value = '';
        customContainer.style.display = 'none';
    }
    calculateGuest();
}

// Attach clamp listeners for guest and ramo custom inputs
function setupNotaObjetivoClamps() {
    // Guest calculator
    const guestInput = document.getElementById('nota-objetivo-custom');
    if (guestInput) {
        // Allow typing intermediate values; only clamp on blur/change
        guestInput.addEventListener('input', function() {
            // Just recalculate guest preview while typing, don't modify value
            calculateGuest();
        });
        guestInput.addEventListener('blur', function() {
            let v = parseFloat(this.value);
            if (isNaN(v)) return;
            if (v > 70) this.value = 70;
            if (v < 10) this.value = 10;
            calculateGuest();
        });
        guestInput.addEventListener('change', function() {
            let v = parseFloat(this.value);
            if (isNaN(v)) return;
            if (v > 70) this.value = 70;
            if (v < 10) this.value = 10;
            calculateGuest();
        });
    }

    // Ramo custom inputs (may be multiple)
    document.querySelectorAll('.nota-objetivo-custom-input').forEach(inp => {
        // Allow typing; clamp and save on change/blur
        inp.addEventListener('input', function() {
            // do nothing to value here to allow multi-digit entry
        });
        inp.addEventListener('blur', function() {
            let v = parseFloat(this.value);
            if (isNaN(v)) return;
            if (v > 70) this.value = 70;
            if (v < 10) this.value = 10;
            updateNotaObjetivoCustom(this);
        });
        inp.addEventListener('change', function() {
            let v = parseFloat(this.value);
            if (isNaN(v)) return;
            if (v > 70) this.value = 70;
            if (v < 10) this.value = 10;
            updateNotaObjetivoCustom(this);
        });
    });
}

function calculateGuest() {
    const rows = document.querySelectorAll('#grades-container .grade-row');
    let totalWeightedScore = 0;
    let totalWeight = 0;

    rows.forEach(row => {
        const gradeInput = row.querySelector('.grade-input');
        const weightInput = row.querySelector('.weight-input');

        const grade = parseFloat(gradeInput.value);
        const weight = parseFloat(weightInput.value);

        if (!isNaN(grade) && !isNaN(weight) && grade >= 10 && grade <= 70) {
            totalWeightedScore += grade * (weight / 100);
            totalWeight += weight;
        }
    });

    const averageDisplay = document.getElementById('guest-average');
    const finalAverageDisplay = document.getElementById('guest-final-average');
    const repeteSection = document.getElementById('repete-section');
    const resultadoMensaje = document.getElementById('resultado-mensaje');
    const resultadoIcono = document.getElementById('resultado-icono');
    const resultadoTexto = document.getElementById('resultado-texto');

    // Obtener nota objetivo
    const tipoNota = document.getElementById('nota-objetivo-tipo').value;
    let notaObjetivo = 39.5;

    if (tipoNota === 'custom') {
        const customInput = document.getElementById('nota-objetivo-custom');
        const customValue = parseFloat(customInput.value);
        if (!isNaN(customValue) && customValue >= 10 && customValue <= 70) {
            notaObjetivo = customValue;
        }
    }

    if (totalWeight > 0) {
        const average = totalWeightedScore / (totalWeight / 100);
        averageDisplay.textContent = average.toFixed(1);

        let finalAverage = average;

        // Verificar si necesita repete (promedio < nota objetivo)
        if (average < notaObjetivo) {
            if (repeteSection) {
                repeteSection.style.display = 'block';
                // Actualizar mensaje del repete con nota objetivo
                const alertSpan = repeteSection.querySelector('.alert-warning span');
                if (alertSpan) {
                    alertSpan.textContent = `Promedio bajo ${notaObjetivo}. Deberás dar el Repete.`;
                }
            }

            const repeteGrade = parseFloat(document.getElementById('repete-grade').value);
            const repeteMode = document.getElementById('repete-mode').value;

            if (!isNaN(repeteGrade) && repeteGrade >= 10 && repeteGrade <= 70) {
                // Calcular nuevo promedio con repete
                if (repeteMode === 'lowest') {
                    // Reemplazar la nota más baja
                    let lowestGrade = 70;
                    let lowestWeight = 0;

                    rows.forEach(row => {
                        const grade = parseFloat(row.querySelector('.grade-input').value);
                        const weight = parseFloat(row.querySelector('.weight-input').value);

                        if (!isNaN(grade) && !isNaN(weight) && grade < lowestGrade) {
                            lowestGrade = grade;
                            lowestWeight = weight;
                        }
                    });

                    if (lowestWeight > 0) {
                        totalWeightedScore = totalWeightedScore - (lowestGrade * (lowestWeight / 100)) + (repeteGrade * (lowestWeight / 100));
                        finalAverage = totalWeightedScore / (totalWeight / 100);
                    }
                } else if (repeteMode === 'highest_weight') {
                    // Reemplazar la evaluación con mayor ponderación
                    let highestWeight = 0;
                    let highestGrade = 0;

                    rows.forEach(row => {
                        const grade = parseFloat(row.querySelector('.grade-input').value);
                        const weight = parseFloat(row.querySelector('.weight-input').value);

                        if (!isNaN(weight) && weight > highestWeight) {
                            highestWeight = weight;
                            highestGrade = grade;
                        }
                    });

                    if (highestWeight > 0) {
                        totalWeightedScore = totalWeightedScore - (highestGrade * (highestWeight / 100)) + (repeteGrade * (highestWeight / 100));
                        finalAverage = totalWeightedScore / (totalWeight / 100);
                    }
                }

                finalAverageDisplay.textContent = finalAverage.toFixed(1);
            } else {
                finalAverageDisplay.textContent = average.toFixed(1);
            }
        } else {
            if (repeteSection) repeteSection.style.display = 'none';
            finalAverageDisplay.textContent = average.toFixed(1);
            finalAverage = average;
        }

        // Mostrar mensaje de resultado si el promedio final es válido
        if (totalWeight >= 100 || (repeteSection && repeteSection.style.display !== 'none' && !isNaN(parseFloat(document.getElementById('repete-grade').value)))) {
            if (finalAverage >= notaObjetivo) {
                // ¡Éxito!
                resultadoMensaje.style.display = 'block';
                resultadoMensaje.style.backgroundColor = '#d4edda';
                resultadoMensaje.style.color = '#155724';
                resultadoIcono.className = 'fas fa-smile-beam';
                resultadoTexto.textContent = '¡Felicidades! Pasaste el ramo';
            } else {
                // Fracaso
                resultadoMensaje.style.display = 'block';
                resultadoMensaje.style.backgroundColor = '#f8d7da';
                resultadoMensaje.style.color = '#721c24';
                resultadoIcono.className = 'fas fa-sad-tear';
                resultadoTexto.textContent = 'No alcanzaste la nota necesaria';
            }
        } else {
            resultadoMensaje.style.display = 'none';
        }
    } else {
        averageDisplay.textContent = '--';
        finalAverageDisplay.textContent = '--';
        if (repeteSection) repeteSection.style.display = 'none';
        resultadoMensaje.style.display = 'none';
    }
}

function addRow() {
    const container = document.getElementById('grades-container');
    const newRow = document.createElement('div');
    newRow.className = 'grade-row';
    newRow.innerHTML = `
        <div class="input-group">
            <label>Nota (10-70)</label>
            <input type="number" class="grade-input" placeholder="" min="10" max="70" oninput="calculateGuest()">
        </div>
        <div class="input-group">
            <label>Porcentaje (%)</label>
            <input type="number" class="weight-input" placeholder="" min="0" max="100" oninput="calculateGuest()">
        </div>
        <button class="btn-remove" onclick="removeRow(this)"><i class="fas fa-minus"></i></button>
    `;
    container.appendChild(newRow);
}

function removeRow(button) {
    const row = button.closest('.grade-row');
    row.remove();
    calculateGuest();
}

function clearCalculator() {
    const inputs = document.querySelectorAll('#grades-container input');
    inputs.forEach(input => input.value = '');
    document.getElementById('repete-grade').value = '';
    calculateGuest();
}

