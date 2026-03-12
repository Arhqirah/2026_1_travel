// Syncs date rules in a form set: no past dates and end date after start date.
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

// Marks fields as valid/invalid for quick visual feedback while typing.
function appSetDestinationFieldState(fieldElement, isValid) {
	fieldElement.classList.remove("destination-field-ok", "destination-field-error")
	if (isValid) {
		fieldElement.classList.add("destination-field-ok")
		return
	}
	fieldElement.classList.add("destination-field-error")
}

// Clears visual validation state from a field.
function appClearDestinationFieldState(fieldElement) {
	fieldElement.classList.remove("destination-field-ok", "destination-field-error")
}

// Validates one destination field based on required and mix-validate attributes.
function appValidateDestinationField(fieldElement, options = {}) {
	const force = options.force === true
	const touched = fieldElement.getAttribute("data-destination-touched") === "yes"

	const tagName = fieldElement.tagName
	if (!["INPUT", "SELECT", "TEXTAREA"].includes(tagName)) {
		return true
	}

	if (fieldElement.disabled) {
		return true
	}

	const value = (fieldElement.value || "").trim()
	let isValid = true

	if (fieldElement.required && value === "") {
		isValid = false
	}

	if (isValid && fieldElement.hasAttribute("mix-validate")) {
		const regexPattern = fieldElement.getAttribute("mix-validate") || ""
		if (regexPattern) {
			const regex = new RegExp(regexPattern)
			isValid = regex.test(fieldElement.value || "")
		}
	}

	if (!force && !touched) {
		appClearDestinationFieldState(fieldElement)
		return isValid
	}

	appSetDestinationFieldState(fieldElement, isValid)
	return isValid
}

// Validates all fields in one destination form and returns overall validity.
function appValidateDestinationForm(formElement, options = {}) {
	let isFormValid = true
	formElement.querySelectorAll("input, select, textarea").forEach((fieldElement) => {
		if (!appValidateDestinationField(fieldElement, options)) {
			isFormValid = false
		}
	})
	return isFormValid
}

// Initializes date rules for all destination forms and updates them on input changes.
function appSetupDestinationDateConstraints() {
	document.querySelectorAll(".destination-form").forEach((formElement) => {
		appSyncDestinationDateConstraints(formElement)
	})
}

// Handles delegated field validation and date sync for dynamically injected forms.
function appHandleDestinationFieldEvents(event) {
	const eventTarget = event.target
	if (!(eventTarget instanceof Element)) {
		return
	}

	const fieldElement = eventTarget.closest(".destination-form input, .destination-form select, .destination-form textarea")
	if (!fieldElement) {
		return
	}

	fieldElement.setAttribute("data-destination-touched", "yes")
	appValidateDestinationField(fieldElement)

	if (["destination_start_date", "destination_end_date"].includes(fieldElement.getAttribute("name") || "")) {
		const formElement = fieldElement.closest(".destination-form")
		if (formElement) {
			appSyncDestinationDateConstraints(formElement)
		}
	}
}

// Ensures submit is blocked if required destination fields fail validation.
function appHandleDestinationFormSubmit(event) {
	const eventTarget = event.target
	if (!(eventTarget instanceof Element)) {
		return
	}

	const formElement = eventTarget.closest(".destination-form")
	if (!formElement) {
		return
	}

	formElement.querySelectorAll("input, select, textarea").forEach((fieldElement) => {
		fieldElement.setAttribute("data-destination-touched", "yes")
	})

	if (!appValidateDestinationForm(formElement, { force: true })) {
		event.preventDefault()
		event.stopPropagation()
	}
}

// Sets up date rules when the page is loaded.
document.addEventListener("DOMContentLoaded", appSetupDestinationDateConstraints)
document.addEventListener("input", appHandleDestinationFieldEvents, true)
document.addEventListener("change", appHandleDestinationFieldEvents, true)
document.addEventListener("submit", appHandleDestinationFormSubmit, true)
