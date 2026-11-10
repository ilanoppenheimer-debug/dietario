/* Dietario · acceso profesional.
   Las páginas de /clinica/ solo se sirven con la cookie que entrega /api/acceso tras ingresar el código.
   El código vive en la variable de entorno PRO_CODE de Vercel (nunca en el repositorio).
   La cookie guarda un hash del código: si se cambia PRO_CODE, todas las sesiones previas quedan fuera. */
import { next } from "@vercel/functions";

export const config = { matcher: ["/clinica", "/clinica/:path*"] };

async function token(code: string): Promise<string> {
  const data = new TextEncoder().encode("dietario-pro:" + code);
  const h = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(h)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export default async function middleware(request: Request): Promise<Response> {
  const code = process.env.PRO_CODE;
  const cookie = request.headers.get("cookie") || "";
  const m = cookie.match(/(?:^|;\s*)dietario_pro=([a-f0-9]{64})/);
  if (code && m && m[1] === (await token(code))) return next();
  const url = new URL(request.url);
  const dest = new URL("/codigo.html", request.url);
  dest.searchParams.set("next", url.pathname + url.search);
  return Response.redirect(dest, 302);
}
