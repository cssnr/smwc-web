const emails = {
    abuse: 'bWFpbHRvOmFidXNlQHNtd2N3b3JsZC5jb20/c3ViamVjdD1BYnVzZSBSZXBvcnQgZm9yOiBzbXdjd29ybGQuY29t',
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-email]').forEach((el) => {
        const url = new URL(atob(emails[el.dataset.email]))
        el.textContent = url.pathname
        el.href = url.href
    })
})
