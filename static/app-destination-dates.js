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

// Initializes date rules for all destination forms and updates them on input changes.
function appSetupDestinationDateConstraints() {
	document.querySelectorAll(".destination-form").forEach((formElement) => {
		appSyncDestinationDateConstraints(formElement)

		const startInput = formElement.querySelector('input[name="destination_start_date"]')
		if (!startInput) {
			return
		}

		startInput.addEventListener("change", () => appSyncDestinationDateConstraints(formElement))
		startInput.addEventListener("input", () => appSyncDestinationDateConstraints(formElement))
	})
}

// Sets up date rules when the page is loaded.
document.addEventListener("DOMContentLoaded", appSetupDestinationDateConstraints)
