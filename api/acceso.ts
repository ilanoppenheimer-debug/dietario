/* Dietario · valida el código profesional y deja una cookie de sesión por 180 días.
   No guarda nada más: no hay cuentas ni registro de quién entra. */
async function token(code: string): Promise<string> {
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("dietario-pro:" + code));
  return Array.from(new Uint8Array(h)).map((b) => b.toString(16).padStart(2, "0")).join("");
}
function seguro(n: string): string { return typeof n === "string" && n.startsWith("/") && !n.startsWith("//") && !n.includes("\\") ? n : "/clinica/index.html"; }

export async function POST(request: Request): Promise<Response> {
  const code = process.env.PRO_CODE;
  let form: FormData;
  try { form = await request.formData(); } catch (e) { form = new FormData(); }
  const dado = String(form.get("codigo") || "").trim().toUpperCase();
  const next = seguro(String(form.get("next") || ""));
  const base = new URL(request.url);
  if (!code || dado !== code.trim().toUpperCase()) {
    await new Promise((r) => setTimeout(r, 600));
    const back = new URL("/codigo.html", base); back.searchParams.set("error", "1"); back.searchParams.set("next", next);
    return new Response(null, { status: 303, headers: { Location: back.toString(), "Cache-Control": "no-store" } });
  }
  const t = await token(code);
  const dest = new URL("/index.html", base); dest.searchParams.set("acceso", "ok"); dest.searchParams.set("next", next);
  return new Response(null, { status: 303, headers: {
    Location: dest.toString(), "Cache-Control": "no-store",
    "Set-Cookie": `dietario_pro=${t}; Path=/; Max-Age=15552000; HttpOnly; Secure; SameSite=Lax`
  } });
}
export function GET() { return new Response("Método no permitido", { status: 405 }); }
