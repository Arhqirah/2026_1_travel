// Escapes text so it can safely be rendered as HTML.
function appEscapeHtml(value) {
	return (value == null ? "" : String(value))
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#39;")
}

// Shows a custom confirmation dialog and returns a Promise with the answer.
function appConfirm(message) {
	return new Promise((resolve) => {
		document.getElementById("app-confirm-overlay")?.remove()

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
		let resolved = false

		const close = (answer) => {
			if (resolved) {
				return
			}
			resolved = true
			document.removeEventListener("keydown", onKeyDown)
			overlay.remove()
			resolve(answer)
		}

		const onKeyDown = (event) => {
			if (event.key === "Escape") {
				close(false)
			}
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

// Runs a MixHTML action without the browser's native confirm dialog.
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

// Catches elements with mix-confirm and shows our custom dialog before continuing.
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

		const trigger = mixConfirmElement.tagName === "FORM"
			? () => mixConfirmElement.requestSubmit()
			: () => mixConfirmElement.click()

		appRunMixActionWithoutNativeConfirm(mixConfirmElement, trigger)
	})
}

document.addEventListener("click", appHandleMixConfirm, true)
document.addEventListener("submit", appHandleMixConfirm, true)
