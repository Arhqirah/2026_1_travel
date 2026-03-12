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

// Handles delete forms that should always use the custom popup.
function appHandleDeleteConfirm(event) {
	const eventTarget = event.target
	if (!(eventTarget instanceof Element)) {
		return
	}

	const deleteForm = eventTarget.closest("form[data-delete-confirm]")
	if (!deleteForm) {
		return
	}

	if (deleteForm.getAttribute("data-delete-confirm-bypass") === "yes") {
		return
	}

	event.preventDefault()
	event.stopPropagation()

	const message = deleteForm.getAttribute("data-delete-confirm") || "Are you sure you want to delete this destination?"
	appConfirm(message).then((confirmed) => {
		if (!confirmed) {
			return
		}

		deleteForm.setAttribute("data-delete-confirm-bypass", "yes")
		try {
			deleteForm.requestSubmit()
		} finally {
			setTimeout(() => {
				deleteForm.removeAttribute("data-delete-confirm-bypass")
			}, 0)
		}
	})
}

document.addEventListener("click", appHandleDeleteConfirm, true)
document.addEventListener("submit", appHandleDeleteConfirm, true)
