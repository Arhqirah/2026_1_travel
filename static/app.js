// Escaper tekst, sa den sikkert kan vises som HTML.
function appEscapeHtml(value) {
	const text = value == null ? "" : String(value)
	return text
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#39;")
}

// Viser en brugerdefineret bekraeftelses-dialog og returnerer et Promise med svaret.
function appConfirm(message) {
	return new Promise((resolve) => {
		const existing = document.getElementById("app-confirm-overlay")
		if (existing) {
			existing.remove()
		}

		const overlay = document.createElement("div")
		overlay.id = "app-confirm-overlay"
		overlay.className = "app-confirm-overlay"
		overlay.innerHTML = `
			<div class="app-confirm-modal" role="alertdialog" aria-modal="true" aria-label="Confirm action">
				<div class="app-confirm-title">Please confirm</div>
				<p class="app-confirm-message">${appEscapeHtml(message || "Are you sure?")}</p>
				<div class="app-confirm-actions">
					<button type="button" class="app-confirm-btn app-confirm-btn-cancel">Cancel</button>
					<button type="button" class="app-confirm-btn app-confirm-btn-ok">Confirm</button>
				</div>
			</div>
		`

		const cancelBtn = overlay.querySelector(".app-confirm-btn-cancel")
		const okBtn = overlay.querySelector(".app-confirm-btn-ok")

		const onKeyDown = (event) => {
			if (event.key === "Escape") {
				close(false)
			}
		}

		const close = (answer) => {
			document.removeEventListener("keydown", onKeyDown)
			overlay.remove()
			resolve(answer)
		}

		cancelBtn.addEventListener("click", () => close(false))
		okBtn.addEventListener("click", () => close(true))
		overlay.addEventListener("click", (event) => {
			if (event.target === overlay) {
				close(false)
			}
		})
		document.addEventListener("keydown", onKeyDown)

		document.body.appendChild(overlay)
		okBtn.focus()
	})
}

// Koerer en MixHTML-handling uden browserens native confirm.
function appRunMixActionWithoutNativeConfirm(targetElement, trigger) {
	const message = targetElement.getAttribute("mix-confirm")
	targetElement.removeAttribute("mix-confirm")

	try {
		trigger()
	} finally {
		setTimeout(() => {
			if (!targetElement.hasAttribute("mix-confirm") && message) {
				targetElement.setAttribute("mix-confirm", message)
			}
		}, 0)
	}
}

// Opfanger elementer med mix-confirm og viser vores egen dialog foer handlingen fortsaetter.
function appHandleMixConfirm(event) {
	const eventTarget = event.target
	if (!(eventTarget instanceof Element)) {
		return
	}

	const mixConfirmElement = eventTarget.closest("[mix-confirm]")
	if (!mixConfirmElement) {
		return
	}

	event.preventDefault()
	event.stopPropagation()

	const message = mixConfirmElement.getAttribute("mix-confirm")
	appConfirm(message).then((confirmed) => {
		if (!confirmed) {
			return
		}

		if (mixConfirmElement.tagName === "FORM") {
			appRunMixActionWithoutNativeConfirm(mixConfirmElement, () => {
				mixConfirmElement.requestSubmit()
			})
			return
		}

		appRunMixActionWithoutNativeConfirm(mixConfirmElement, () => {
			mixConfirmElement.click()
		})
	})
}

document.addEventListener("click", appHandleMixConfirm, true)
document.addEventListener("submit", appHandleMixConfirm, true)

// Synkroniserer datoregler i et formular-saet: ingen datoer i fortiden og slutdato efter startdato.
function appSyncDestinationDateConstraints(formElement) {
	const startInput = formElement.querySelector('input[name="destination_start_date"]')
	const endInput = formElement.querySelector('input[name="destination_end_date"]')
	if (!startInput || !endInput) {
		return
	}

	const today = new Date()
	const todayIso = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`
	startInput.min = todayIso

	const startValue = startInput.value || ""
	if (startValue) {
		endInput.min = startValue < todayIso ? todayIso : startValue
		if (endInput.value && endInput.value < startValue) {
			endInput.value = ""
		}
		return
	}

	endInput.min = todayIso
}

// Initialiserer datoregler for alle destination-formularer og opdaterer regler ved input-aendringer.
function appSetupDestinationDateConstraints() {
	const forms = document.querySelectorAll(".destination-form")
	forms.forEach((formElement) => {
		appSyncDestinationDateConstraints(formElement)

		const startInput = formElement.querySelector('input[name="destination_start_date"]')
		const endInput = formElement.querySelector('input[name="destination_end_date"]')
		if (!startInput || !endInput) {
			return
		}

		startInput.addEventListener("change", () => appSyncDestinationDateConstraints(formElement))
		startInput.addEventListener("input", () => appSyncDestinationDateConstraints(formElement))
	})
}

// Saetter datoregler op, naar siden er indlaest.
document.addEventListener("DOMContentLoaded", appSetupDestinationDateConstraints)
