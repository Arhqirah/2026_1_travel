// Returns true if a form is signup or login form handled by auth APIs.
function appIsAuthForm(formElement) {
	if (!(formElement instanceof HTMLFormElement)) {
		return false
	}

	const endpoint = formElement.getAttribute("mix-post") || ""
	return ["/api-create-user", "/api-login"].includes(endpoint)
}

// Applies visual state to one auth field.
function appSetAuthFieldState(fieldElement, isValid) {
	fieldElement.classList.remove("destination-field-ok", "destination-field-error")
	if (isValid) {
		fieldElement.classList.add("destination-field-ok")
		return
	}
	fieldElement.classList.add("destination-field-error")
}

// Clears visual state from one auth field.
function appClearAuthFieldState(fieldElement) {
	fieldElement.classList.remove("destination-field-ok", "destination-field-error")
}

// Validates one auth field based on backend-equivalent constraints.
function appValidateAuthField(fieldElement, options = {}) {
	const force = options.force === true
	const touched = fieldElement.getAttribute("data-auth-touched") === "yes"
	const fieldName = fieldElement.getAttribute("name") || ""
	const value = (fieldElement.value || "").trim()
	let isValid = true

	if (fieldName === "user_first_name" || fieldName === "user_last_name") {
		isValid = value.length >= 2 && value.length <= 20
	}

	if (fieldName === "user_email") {
		isValid = value !== "" && fieldElement.checkValidity()
	}

	if (fieldName === "user_password") {
		isValid = value.length >= 8 && value.length <= 50
	}

	if (!force && !touched) {
		appClearAuthFieldState(fieldElement)
		return isValid
	}

	appSetAuthFieldState(fieldElement, isValid)
	return isValid
}

// Validates all auth fields in one form.
function appValidateAuthForm(formElement, options = {}) {
	let isFormValid = true
	formElement.querySelectorAll("input[name='user_first_name'], input[name='user_last_name'], input[name='user_email'], input[name='user_password']").forEach((fieldElement) => {
		if (!appValidateAuthField(fieldElement, options)) {
			isFormValid = false
		}
	})
	return isFormValid
}

// Handles touched-only validation on auth field input/change.
function appHandleAuthFieldEvents(event) {
	const eventTarget = event.target
	if (!(eventTarget instanceof Element)) {
		return
	}

	const fieldElement = eventTarget.closest("form input[name='user_first_name'], form input[name='user_last_name'], form input[name='user_email'], form input[name='user_password']")
	if (!fieldElement) {
		return
	}

	const formElement = fieldElement.closest("form")
	if (!appIsAuthForm(formElement)) {
		return
	}

	fieldElement.setAttribute("data-auth-touched", "yes")
	appValidateAuthField(fieldElement)
}

// Prevents submit when auth form has invalid fields and reveals states.
function appHandleAuthFormSubmit(event) {
	const eventTarget = event.target
	if (!(eventTarget instanceof Element)) {
		return
	}

	const formElement = eventTarget.closest("form")
	if (!appIsAuthForm(formElement)) {
		return
	}

	formElement.querySelectorAll("input[name='user_first_name'], input[name='user_last_name'], input[name='user_email'], input[name='user_password']").forEach((fieldElement) => {
		fieldElement.setAttribute("data-auth-touched", "yes")
	})

	if (!appValidateAuthForm(formElement, { force: true })) {
		event.preventDefault()
		event.stopPropagation()
	}
}

document.addEventListener("input", appHandleAuthFieldEvents, true)
document.addEventListener("change", appHandleAuthFieldEvents, true)
document.addEventListener("submit", appHandleAuthFormSubmit, true)
