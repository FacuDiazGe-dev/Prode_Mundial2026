const FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4";
const ESTADOS_AUTOMATICOS = new Set(["Pendiente", "En Vivo", "Entretiempo"]);

const MESES_ES: Record<string, number> = {
  ene: 1,
  feb: 2,
  mar: 3,
  abr: 4,
  may: 5,
  jun: 6,
  jul: 7,
  ago: 8,
  sep: 9,
  oct: 10,
  nov: 11,
  dic: 12,
};

const EQUIPO_ALIASES: Record<string, string[]> = {
  "alemania": ["germany"],
  "arabia saudita": ["saudi arabia"],
  "argentina": ["argentina"],
  "australia": ["australia"],
  "belgica": ["belgium"],
  "bosnia y herzegovina": ["bosnia and herzegovina", "bosnia-herzegovina", "bosnia herzegovina"],
  "brasil": ["brazil"],
  "canada": ["canada"],
  "cabo verde": ["cape verde", "cape verde islands"],
  "corea del sur": ["korea republic", "south korea"],
  "costa rica": ["costa rica"],
  "croacia": ["croatia"],
  "dinamarca": ["denmark"],
  "egipto": ["egypt"],
  "ecuador": ["ecuador"],
  "espana": ["spain"],
  "estados unidos": ["united states", "usa", "united states of america"],
  "francia": ["france"],
  "haiti": ["haiti"],
  "inglaterra": ["england"],
  "irak": ["iraq"],
  "iran": ["iran"],
  "italia": ["italy"],
  "japon": ["japan"],
  "marruecos": ["morocco"],
  "mexico": ["mexico"],
  "noruega": ["norway"],
  "nueva zelanda": ["new zealand"],
  "nigeria": ["nigeria"],
  "paises bajos": ["netherlands", "holland"],
  "paraguay": ["paraguay"],
  "polonia": ["poland"],
  "portugal": ["portugal"],
  "qatar": ["qatar"],
  "catar": ["qatar"],
  "republica checa": ["czechia", "czech republic"],
  "republica democratica del congo": ["congo dr", "dr congo", "congo democratic republic"],
  "senegal": ["senegal"],
  "serbia": ["serbia"],
  "sudafrica": ["south africa"],
  "suecia": ["sweden"],
  "suiza": ["switzerland"],
  "tunez": ["tunisia"],
  "uruguay": ["uruguay"],
  "uzbekistan": ["uzbekistan"],
  "costa de marfil": ["ivory coast", "cote d ivoire"],
  "curazao": ["curacao"],
  "argelia": ["algeria"],
};

type ResultadoRow = {
  n_partido: number;
  equipo_1: string;
  equipo_2: string;
  dia: string;
  hora: string;
  viz: boolean | string | number | null;
  live?: boolean | string | number | null;
  live_r1?: number | null;
  live_r2?: number | null;
  estado_partido?: string | null;
};

type MatchApi = {
  status?: string;
  utcDate?: string;
  homeTeam?: { name?: string; shortName?: string; tla?: string };
  awayTeam?: { name?: string; shortName?: string; tla?: string };
  score?: Record<string, { home?: number | null; away?: number | null }>;
};

function requiredEnv(name: string): string {
  const value = (Deno.env.get(name) || "").trim();
  if (!value) throw new Error(`Falta variable requerida: ${name}`);
  return value;
}

function normalizarTexto(value: unknown): string {
  return String(value || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function parseFechaPartido(dia: unknown): string | null {
  const match = String(dia || "").trim().toLowerCase().match(/(\d{1,2})\s*[-/ ]\s*([a-zA-Z]{3})/);
  if (!match) return null;

  const diaNum = Number(match[1]);
  const mesNum = MESES_ES[normalizarTexto(match[2]).slice(0, 3)];
  if (!diaNum || !mesNum) return null;

  return `2026-${String(mesNum).padStart(2, "0")}-${String(diaNum).padStart(2, "0")}`;
}

function fechasPosiblesPartido(partido: ResultadoRow): string[] {
  const fechaApi = parseFechaPartido(partido.dia);
  if (!fechaApi) return [];

  const fechas = [fechaApi];
  const hora = Number(String(partido.hora || "").split(":", 1)[0]);
  if (!Number.isNaN(hora) && hora >= 21) {
    const fecha = new Date(`${fechaApi}T00:00:00Z`);
    fecha.setUTCDate(fecha.getUTCDate() + 1);
    fechas.push(fecha.toISOString().slice(0, 10));
  }

  return fechas;
}

function nombresEquipo(nombre: unknown): string[] {
  const normalizado = normalizarTexto(nombre);
  return [normalizado, ...(EQUIPO_ALIASES[normalizado] || [])];
}

function coincideEquipo(nombreProde: unknown, equipoApi: MatchApi["homeTeam"]): boolean {
  const candidatosProde = nombresEquipo(nombreProde);
  const candidatosApi = [equipoApi?.name, equipoApi?.shortName, equipoApi?.tla]
    .map(normalizarTexto)
    .filter(Boolean);

  return candidatosProde.some((prode) =>
    candidatosApi.some((api) => prode === api || prode.includes(api) || api.includes(prode))
  );
}

function scoreActual(score: MatchApi["score"]): [number | null, number | null] {
  for (const key of ["fullTime", "regularTime", "halfTime"]) {
    const parcial = score?.[key] || {};
    if (parcial.home !== null && parcial.home !== undefined && parcial.away !== null && parcial.away !== undefined) {
      return [Number(parcial.home), Number(parcial.away)];
    }
  }
  return [null, null];
}

function estadoDesdeApi(status: unknown): string {
  const value = String(status || "").trim().toUpperCase();
  if (value === "FINISHED") return "Finalizado";
  if (["IN_PLAY", "LIVE"].includes(value)) return "En Vivo";
  if (value === "PAUSED") return "Entretiempo";
  return "Pendiente";
}

function esVisible(value: unknown): boolean {
  return ["TRUE", "1", "1.0", "VERDADERO", "T", "SI", "SÍ"].includes(String(value || "").trim().toUpperCase());
}

async function consultarMatchesApi(): Promise<MatchApi[]> {
  const token = requiredEnv("FOOTBALL_DATA_API_TOKEN");
  const competitionCode = (Deno.env.get("FOOTBALL_DATA_COMPETITION_CODE") || "WC").trim();
  const url = new URL(
    competitionCode === "WC"
      ? `${FOOTBALL_DATA_BASE_URL}/competitions/WC/matches`
      : `${FOOTBALL_DATA_BASE_URL}/matches`,
  );

  if (competitionCode === "WC") {
    url.searchParams.set("season", "2026");
  } else {
    url.searchParams.set("competitions", competitionCode);
  }

  const response = await fetch(url, { headers: { "X-Auth-Token": token } });
  if (!response.ok) {
    throw new Error(`football-data.org respondio ${response.status}: ${await response.text()}`);
  }

  const payload = await response.json();
  return payload.matches || [];
}

async function leerPartidosVisibles(): Promise<ResultadoRow[]> {
  const supabaseUrl = requiredEnv("SUPABASE_URL");
  const serviceRoleKey = requiredEnv("SUPABASE_SERVICE_ROLE_KEY");
  const url = new URL(`${supabaseUrl}/rest/v1/resultados`);
  url.searchParams.set("select", "n_partido,equipo_1,equipo_2,dia,hora,viz,live,live_r1,live_r2,estado_partido");
  url.searchParams.set("or", "(estado_partido.is.null,estado_partido.neq.Finalizado)");
  url.searchParams.set("order", "n_partido.asc");

  const response = await fetch(url, {
    headers: {
      apikey: serviceRoleKey,
      Authorization: `Bearer ${serviceRoleKey}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Supabase select respondio ${response.status}: ${await response.text()}`);
  }

  const rows = await response.json();
  return rows.filter((row: ResultadoRow) => esVisible(row.viz));
}

function sugerirPartido(partido: ResultadoRow, matches: MatchApi[]) {
  const fechasApi = fechasPosiblesPartido(partido);
  const equipo1 = partido.equipo_1;
  const equipo2 = partido.equipo_2;

  for (const filtrarFecha of [true, false]) {
    for (const match of matches) {
      if (filtrarFecha && !fechasApi.includes(String(match.utcDate || "").split("T", 1)[0])) continue;

      const homeTeam = match.homeTeam || {};
      const awayTeam = match.awayTeam || {};
      const normal = coincideEquipo(equipo1, homeTeam) && coincideEquipo(equipo2, awayTeam);
      const invertido = coincideEquipo(equipo1, awayTeam) && coincideEquipo(equipo2, homeTeam);
      if (!normal && !invertido) continue;

      const [homeScore, awayScore] = scoreActual(match.score);
      const estado = estadoDesdeApi(match.status);
      return {
        ok: true,
        n_partido: partido.n_partido,
        status_api: match.status || null,
        estado,
        r1: invertido ? awayScore : homeScore,
        r2: invertido ? homeScore : awayScore,
        home: homeTeam.name || null,
        away: awayTeam.name || null,
        utc_date: match.utcDate || null,
        mensaje: filtrarFecha ? "Match por fecha/equipos." : "Match por equipos; revisar fecha/hora.",
      };
    }
  }

  return {
    ok: false,
    n_partido: partido.n_partido,
    mensaje: "No se encontro partido equivalente en football-data.org.",
  };
}

async function actualizarEstadoVisual(sugerencia: ReturnType<typeof sugerirPartido>) {
  if (!sugerencia.ok) return null;

  const supabaseUrl = requiredEnv("SUPABASE_URL");
  const serviceRoleKey = requiredEnv("SUPABASE_SERVICE_ROLE_KEY");
  const statusApi = String(sugerencia.status_api || "").toUpperCase();
  const update: Record<string, unknown> = {
    live_r1: sugerencia.r1,
    live_r2: sugerencia.r2,
  };

  if (statusApi !== "FINISHED" && ESTADOS_AUTOMATICOS.has(sugerencia.estado)) {
    update.estado_partido = sugerencia.estado;
    update.live = ["En Vivo", "Entretiempo"].includes(sugerencia.estado);
  }

  const url = new URL(`${supabaseUrl}/rest/v1/resultados`);
  url.searchParams.set("n_partido", `eq.${sugerencia.n_partido}`);

  const response = await fetch(url, {
    method: "PATCH",
    headers: {
      apikey: serviceRoleKey,
      Authorization: `Bearer ${serviceRoleKey}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(update),
  });

  if (!response.ok) {
    throw new Error(`Supabase update partido #${sugerencia.n_partido} respondio ${response.status}: ${await response.text()}`);
  }

  return update;
}

function validarSyncSecret(request: Request) {
  const expected = (Deno.env.get("SYNC_LIVE_SECRET") || "").trim();
  if (!expected) {
    throw new Error("Falta SYNC_LIVE_SECRET en los secrets de la Edge Function.");
  }

  const received = (request.headers.get("x-sync-secret") || "").trim();
  if (received !== expected) {
    return false;
  }

  return true;
}

Deno.serve(async (request) => {
  try {
    if (!validarSyncSecret(request)) {
      return Response.json({ ok: false, error: "No autorizado." }, { status: 401 });
    }

    const partidos = await leerPartidosVisibles();
    const matches = await consultarMatchesApi();
    const detalles = [];
    let actualizados = 0;
    let finalizadosDetectados = 0;
    let noEncontrados = 0;

    for (const partido of partidos) {
      const sugerencia = sugerirPartido(partido, matches);
      if (!sugerencia.ok) {
        noEncontrados += 1;
        detalles.push(sugerencia);
        continue;
      }

      if (String(sugerencia.status_api || "").toUpperCase() === "FINISHED") {
        finalizadosDetectados += 1;
      }

      const update = await actualizarEstadoVisual(sugerencia);
      actualizados += 1;
      detalles.push({ ...sugerencia, update });
    }

    return Response.json({
      ok: true,
      partidos_consultados: partidos.length,
      actualizados,
      finalizados_detectados: finalizadosDetectados,
      no_encontrados: noEncontrados,
      detalles,
    });
  } catch (error) {
    return Response.json({ ok: false, error: error instanceof Error ? error.message : String(error) }, { status: 500 });
  }
});
