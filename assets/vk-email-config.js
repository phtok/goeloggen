// Optional runtime config for the visitenkarten email export gateway.
// Set this to your deployed worker URL, e.g.:
// window.VK_EMAIL_EXPORT_ENDPOINT = "https://vk-mail.your-domain.workers.dev/export";
window.VK_EMAIL_EXPORT_ENDPOINT =
  window.VK_EMAIL_EXPORT_ENDPOINT || "https://goetheanum-visitenkarten-email.goetheanum-grafik-philipptok.workers.dev";

// Optional attachment cap in bytes (default in app: 14 MB).
// window.VK_EMAIL_MAX_ATTACHMENT_BYTES = 12 * 1024 * 1024;
