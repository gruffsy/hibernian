const PREFERENCE_KEY = "hibernian.ui.preference";
const CLASSIC_URL = "./legacy/frontend-static/index.htm";
const R2_BASE_URL = "https://pub-a1dbb638fdc8455c914f9f6c5f5b4564.r2.dev/latest";
const LOCAL_PUBLISH_BASE_URL = "./legacy/frontend-static/data/publish";
const DAY_DATA_URL = {
  local: `${LOCAL_PUBLISH_BASE_URL}/salg_fra_22_pr_dag_med_total.json`,
  remote: `${R2_BASE_URL}/salg_fra_22_pr_dag_med_total.json`,
};
const MONTH_COMPARE_URL = `${LOCAL_PUBLISH_BASE_URL}/salg_fra_22_pr_mnd_med_total_og_sammenligning.json`;
const SELLER_DAY_DATA_URL = {
  local: `${LOCAL_PUBLISH_BASE_URL}/salg_pr_selger_fra_22_pr_dag.json`,
  remote: `${R2_BASE_URL}/salg_pr_selger_fra_22_pr_dag.json`,
};
const STOCK_DATA_URL = {
  local: `${LOCAL_PUBLISH_BASE_URL}/merged_stock_orders.json`,
  remote: `${R2_BASE_URL}/merged_stock_orders.json`,
};
const META_URL = {
  local: `${LOCAL_PUBLISH_BASE_URL}/tid.json`,
  remote: `${R2_BASE_URL}/tid.json`,
};
const app = document.getElementById("app");
const activeVisuals = [];
let resizeVisualsBound = false;

function getDataMode() {
  const params = new URLSearchParams(window.location.search);
  return params.get("data") === "local" ? "local" : "auto";
}

function getCandidateUrls(target) {
  if (typeof target === "string") {
    return [target];
  }

  if (getDataMode() === "local") {
    return [target.local];
  }

  return [target.remote, target.local];
}

async function fetchJson(url) {
  const separator = url.includes("?") ? "&" : "?";
  const response = await fetch(`${url}${separator}_ts=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  return response.json();
}

async function fetchJsonWithFallback(target) {
  const errors = [];
  for (const url of getCandidateUrls(target)) {
    try {
      return await fetchJson(url);
    } catch (error) {
      errors.push(error instanceof Error ? error.message : String(error));
    }
  }

  throw new Error(errors.join(" | "));
}

function setPreference(value) {
  localStorage.setItem(PREFERENCE_KEY, value);
}

function getPreference() {
  return localStorage.getItem(PREFERENCE_KEY) || "classic";
}

function goClassic() {
  setPreference("classic");
  window.location.href = CLASSIC_URL;
}

function normalizeDisplayText(value) {
  return String(value ?? "").trim();
}

function parseCurrency(value) {
  return Number(String(value).replace(/[^\d-]/g, ""));
}

function parseInteger(value) {
  return Number(String(value).replace(/[^\d-]/g, ""));
}

function parsePercent(value) {
  return Number(String(value).replace("%", "").replace(",", "."));
}

function formatCurrency(value) {
  return `${Math.round(value).toLocaleString("nb-NO")} kr`;
}

function formatInteger(value) {
  return Math.round(value).toLocaleString("nb-NO");
}

function formatPercent(value) {
  return `${value.toFixed(1)}%`;
}

function formatSignedCurrency(value) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatCurrency(value)}`;
}

function formatSignedInteger(value) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatInteger(value)}`;
}

function formatSignedPercentPoints(value) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(1)} pp`;
}

function formatAxisMillions(value) {
  const millions = Number(value) / 1000000;
  const formatted = millions
    .toFixed(millions >= 10 ? 0 : 1)
    .replace(".", ",")
    .replace(/,0$/, "");
  return `${formatted}m`;
}

function getYearFromLabel(label) {
  const match = String(label).match(/(19|20)\d{2}/);
  return match ? Number(match[0]) : Number.POSITIVE_INFINITY;
}

function sortDatasetsByYear(datasets) {
  return [...datasets].sort((left, right) => {
    const yearDelta = getYearFromLabel(left.label) - getYearFromLabel(right.label);
    if (yearDelta !== 0) {
      return yearDelta;
    }
    return String(left.label).localeCompare(String(right.label), "nb-NO");
  });
}

function formatDateLabel(dateKey) {
  const raw = String(dateKey);
  const year = Number(raw.slice(0, 4));
  const month = Number(raw.slice(4, 6)) - 1;
  const day = Number(raw.slice(6, 8));
  const date = new Date(year, month, day);

  return new Intl.DateTimeFormat("nb-NO", {
    weekday: "long",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

function formatDayHeading(dateKey) {
  return formatDateLabel(dateKey).replace(",", "");
}

function formatInputDate(dateKey) {
  const raw = String(dateKey);
  return `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`;
}

function parseDateKey(dateKey) {
  const raw = String(dateKey);
  return {
    year: Number(raw.slice(0, 4)),
    month: Number(raw.slice(4, 6)),
    day: Number(raw.slice(6, 8)),
  };
}

function buildDateKey(year, month, day) {
  return `${year}${String(month).padStart(2, "0")}${String(day).padStart(2, "0")}`;
}

function getDaysInMonth(year, month) {
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function toUtcDate(dateKey) {
  const { year, month, day } = parseDateKey(dateKey);
  return new Date(Date.UTC(year, month - 1, day));
}

function formatMonthDayKey(dateKey) {
  const raw = String(dateKey);
  return `${raw.slice(4, 6)}-${raw.slice(6, 8)}`;
}

function formatMonthDayLabel(monthDay) {
  const [month, day] = monthDay.split("-").map(Number);
  const date = new Date(2026, month - 1, day);
  return new Intl.DateTimeFormat("nb-NO", {
    day: "numeric",
    month: "long",
  }).format(date);
}

function monthKey(year, month) {
  return `${year}-${String(month).padStart(2, "0")}`;
}

function monthLabelFromKey(key) {
  const [year, month] = key.split("-").map(Number);
  return new Intl.DateTimeFormat("nb-NO", {
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, 1));
}

function getIsoWeekInfo(dateKey) {
  const date = toUtcDate(dateKey);
  const day = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - day);
  const isoYear = date.getUTCFullYear();
  const yearStart = new Date(Date.UTC(isoYear, 0, 1));
  const weekNumber = Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
  const isoDay = toUtcDate(dateKey).getUTCDay() || 7;

  return {
    isoYear,
    weekNumber,
    isoDay,
    weekKey: `${isoYear}-W${String(weekNumber).padStart(2, "0")}`,
  };
}

function getIsoWeekStart(isoYear, weekNumber) {
  const simple = new Date(Date.UTC(isoYear, 0, 1 + (weekNumber - 1) * 7));
  const day = simple.getUTCDay() || 7;
  if (day <= 4) {
    simple.setUTCDate(simple.getUTCDate() - day + 1);
  } else {
    simple.setUTCDate(simple.getUTCDate() + 8 - day);
  }
  return simple;
}

function formatWeekLabel(weekKey) {
  const [yearText, weekText] = weekKey.split("-W");
  const isoYear = Number(yearText);
  const weekNumber = Number(weekText);
  const start = getIsoWeekStart(isoYear, weekNumber);
  const end = new Date(start);
  end.setUTCDate(start.getUTCDate() + 6);
  const startLabel = new Intl.DateTimeFormat("nb-NO", {
    day: "2-digit",
    month: "2-digit",
  }).format(start);
  const endLabel = new Intl.DateTimeFormat("nb-NO", {
    day: "2-digit",
    month: "2-digit",
  }).format(end);
  return `Uke ${weekNumber}, ${isoYear} (${startLabel}-${endLabel})`;
}

function formatMonthHeading(key, cutoffDay = null) {
  return cutoffDay ? `${monthLabelFromKey(key)} - hittil dag ${cutoffDay}` : monthLabelFromKey(key);
}

function formatYearHeading(year, cutoffMonthDay = null) {
  return cutoffMonthDay ? `${year} - hittil ${formatMonthDayLabel(cutoffMonthDay)}` : String(year);
}

function formatWeekHeading(weekKey, cutoffIsoDay = null) {
  const weekdayLabels = ["", "mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"];
  return cutoffIsoDay ? `${formatWeekLabel(weekKey)} - hittil ${weekdayLabels[cutoffIsoDay]}` : formatWeekLabel(weekKey);
}

function formatShortMonth(month) {
  return new Intl.DateTimeFormat("nb-NO", { month: "short" })
    .format(new Date(2026, month - 1, 1))
    .replace(".", "");
}

function normalizeText(value) {
  return normalizeDisplayText(value)
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[^a-z0-9]/g, "");
}

function rowClass(row) {
  return row.butikk === "Totalt" ? "store-row total-row" : "store-row";
}

function enrichRow(row) {
  const gross = parseCurrency(row.mmoms);
  const net = parseCurrency(row.umoms);
  const dbAmount = parseCurrency(row.db);
  const customers = parseInteger(row.antord);
  const perCustomer = parseCurrency(row.prord);
  const dgPercent = parsePercent(row.dg);
  const client = Number(row.Klient ?? 0);

  return {
    ...row,
    butikk: normalizeDisplayText(row.butikk),
    gross,
    net,
    dbAmount,
    customers,
    perCustomer,
    dgPercent,
    client,
    mmoms: formatCurrency(gross),
    umoms: formatCurrency(net),
    db: formatCurrency(dbAmount),
    antord: formatInteger(customers),
    prord: formatCurrency(perCustomer),
    dg: formatPercent(dgPercent),
  };
}

function sortRows(rows) {
  return [...rows].sort((left, right) => left.client - right.client);
}

function getTotals(rows) {
  return rows.find((row) => row.butikk === "Totalt") || rows[rows.length - 1] || null;
}

function getStoreRows(rows) {
  return rows.filter((row) => row.butikk !== "Totalt");
}

async function loadUpdatedAt() {
  try {
    const data = await fetchJsonWithFallback(META_URL);
    return Array.isArray(data) && data[0] ? data[0].oppdatert : null;
  } catch {
    return null;
  }
}

async function loadDayData() {
  const rows = (await fetchJsonWithFallback(DAY_DATA_URL)).map(enrichRow);
  const grouped = new Map();
  const monthDates = new Map();
  const weekDates = new Map();

  for (const row of rows) {
    const dateKey = String(row.fakturadato);
    const key = monthKey(Number(dateKey.slice(0, 4)), Number(dateKey.slice(4, 6)));

    if (!grouped.has(dateKey)) {
      grouped.set(dateKey, []);
    }
    grouped.get(dateKey).push(row);

    if (!monthDates.has(key)) {
      monthDates.set(key, []);
    }
    monthDates.get(key).push(dateKey);

    const weekInfo = getIsoWeekInfo(dateKey);
    if (!weekDates.has(weekInfo.weekKey)) {
      weekDates.set(weekInfo.weekKey, []);
    }
    weekDates.get(weekInfo.weekKey).push(dateKey);
  }

  for (const [dateKey, dateRows] of grouped.entries()) {
    grouped.set(dateKey, sortRows(dateRows));
  }

  const dates = Array.from(grouped.keys()).sort((left, right) => Number(right) - Number(left));

  for (const [key, dateKeys] of monthDates.entries()) {
    monthDates.set(
      key,
      Array.from(new Set(dateKeys)).sort((left, right) => Number(left) - Number(right))
    );
  }

  for (const [key, dateKeys] of weekDates.entries()) {
    weekDates.set(
      key,
      Array.from(new Set(dateKeys)).sort((left, right) => Number(left) - Number(right))
    );
  }

  return { grouped, dates, monthDates, weekDates };
}

async function loadMonthData() {
  const compareResponse = await fetch(MONTH_COMPARE_URL);

  if (!compareResponse.ok) {
    throw new Error("Kunne ikke lese månedsdata.");
  }

  const compareRows = (await compareResponse.json()).map((row) => ({
    ...enrichRow(row),
    thisYear: row.this_year,
    lastYear: row.last_year,
    incomplete: row.incomplete,
  }));

  return { compareRows };
}

function enrichSellerDayRow(row) {
  return {
    navn: normalizeDisplayText(row.navn),
    butikk: normalizeDisplayText(row.butikk || "Ukjent butikk"),
    umomsValue: parseCurrency(row.umoms),
    dbValue: parseCurrency(row.db),
    umoms: formatCurrency(parseCurrency(row.umoms)),
    db: formatCurrency(parseCurrency(row.db)),
    fakturadato: Number(row.fakturadato),
    ukedag: normalizeDisplayText(row.ukedag),
  };
}

async function loadSellerData() {
  const dayRows = (await fetchJsonWithFallback(SELLER_DAY_DATA_URL)).map(enrichSellerDayRow);
  const latestDay = Math.max(...dayRows.map((row) => row.fakturadato));
  const latestMonthKey = monthKey(
    Number(String(latestDay).slice(0, 4)),
    Number(String(latestDay).slice(4, 6))
  );
  const latestYear = Number(String(latestDay).slice(0, 4));

  return {
    rawRows: dayRows,
    dayRows: aggregateSellerRows(dayRows.filter((row) => row.fakturadato === latestDay)),
    monthRows: aggregateSellerRows(
      dayRows.filter(
        (row) =>
          monthKey(Number(String(row.fakturadato).slice(0, 4)), Number(String(row.fakturadato).slice(4, 6))) ===
          latestMonthKey
      )
    ),
    yearRows: aggregateSellerRows(
      dayRows.filter((row) => Number(String(row.fakturadato).slice(0, 4)) === latestYear)
    ),
    latestDay,
    latestMonthKey,
    latestYear,
  };
}

function readStockValue(row, keys, fallback = 0) {
  for (const key of keys) {
    if (Object.hasOwn(row, key)) {
      return row[key];
    }
  }

  const entries = Object.entries(row);
  for (const key of keys) {
    const match = entries.find(([candidate]) => normalizeDisplayText(candidate) === normalizeDisplayText(key));
    if (match) {
      return match[1];
    }
  }

  return fallback;
}

function enrichStockRow(row) {
  const incomingOrders = readStockValue(row, ["Bestilling på vei"], []);
  const orders = Array.isArray(incomingOrders)
    ? incomingOrders.map((order) => ({
        week: normalizeDisplayText(order.Ukenr || "Ukjent uke"),
        amount: Number(order.Antall || 0),
        amountLabel: formatInteger(Number(order.Antall || 0)),
      }))
    : [];
  const stockAmount = Number(readStockValue(row, ["antall på lager"], 0));
  const unitsPerPallet = Number(readStockValue(row, ["antall pr pall"], 0));
  const palletsInStock = Number(readStockValue(row, ["Paller på lager"], 0));
  const palletsIncoming = Number(readStockValue(row, ["Paller på vei"], 0));

  return {
    prodno: String(readStockValue(row, ["Prodno"], "")).trim(),
    description: normalizeDisplayText(readStockValue(row, ["Beskrivelse"], "")),
    stockAmount,
    unitsPerPallet,
    palletsInStock,
    palletsIncoming,
    orders,
    stockAmountLabel: formatInteger(stockAmount),
    unitsPerPalletLabel: unitsPerPallet ? formatInteger(unitsPerPallet) : "0",
    palletsInStockLabel: formatInteger(palletsInStock),
    palletsIncomingLabel: formatInteger(palletsIncoming),
    searchText: normalizeText(`${readStockValue(row, ["Prodno"], "")} ${readStockValue(row, ["Beskrivelse"], "")}`),
  };
}

async function loadStockData() {
  const rows = (await fetchJsonWithFallback(STOCK_DATA_URL)).map(enrichStockRow);
  return rows.sort((left, right) => {
    if (right.palletsIncoming !== left.palletsIncoming) {
      return right.palletsIncoming - left.palletsIncoming;
    }
    if (right.palletsInStock !== left.palletsInStock) {
      return right.palletsInStock - left.palletsInStock;
    }
    return left.description.localeCompare(right.description, "nb-NO");
  });
}

function aggregateSellerRows(rows) {
  const grouped = new Map();

  for (const row of rows) {
    const key = `${normalizeText(row.navn)}__${normalizeText(row.butikk)}`;
    if (!grouped.has(key)) {
      grouped.set(key, {
        navn: row.navn,
        butikk: row.butikk,
        umomsValue: 0,
        dbValue: 0,
      });
    }

    const current = grouped.get(key);
    current.umomsValue += row.umomsValue;
    current.dbValue += row.dbValue;
  }

  return Array.from(grouped.values()).map((row) => ({
    ...row,
    umoms: formatCurrency(row.umomsValue),
    db: formatCurrency(row.dbValue),
  }));
}

function buildRowsForDateKeys(dayGrouped, dateKeys) {
  const rows = dateKeys.flatMap((dateKey) => dayGrouped.get(dateKey) || []);
  return buildAggregatedRows(rows);
}

function buildCanonicalMonths(dayData) {
  const monthOptions = Array.from(dayData.monthDates.keys()).sort((left, right) => (left < right ? 1 : -1));
  const canonicalMonths = new Map();

  for (const key of monthOptions) {
    canonicalMonths.set(key, buildRowsForDateKeys(dayData.grouped, dayData.monthDates.get(key) || []));
  }

  return { canonicalMonths, monthOptions };
}

function buildCanonicalYears(dayData) {
  const yearOptions = Array.from(
    new Set(dayData.dates.map((dateKey) => Number(String(dateKey).slice(0, 4))))
  ).sort((left, right) => right - left);
  const canonicalYears = new Map();

  for (const year of yearOptions) {
    const yearDates = dayData.dates.filter((dateKey) => Number(String(dateKey).slice(0, 4)) === year);
    canonicalYears.set(year, buildRowsForDateKeys(dayData.grouped, yearDates));
  }

  return { canonicalYears, yearOptions };
}

function buildAggregatedRows(rows) {
  const stores = new Map();

  for (const row of rows) {
    if (row.butikk === "Totalt") {
      continue;
    }

    if (!stores.has(row.butikk)) {
      stores.set(row.butikk, {
        butikk: row.butikk,
        client: row.client,
        gross: 0,
        net: 0,
        dbAmount: 0,
        customers: 0,
      });
    }

    const current = stores.get(row.butikk);
    current.gross += row.gross;
    current.net += row.net;
    current.dbAmount += row.dbAmount;
    current.customers += row.customers;
  }

  const items = Array.from(stores.values()).sort((left, right) => left.client - right.client);
  const totals = items.reduce(
    (accumulator, row) => {
      accumulator.gross += row.gross;
      accumulator.net += row.net;
      accumulator.dbAmount += row.dbAmount;
      accumulator.customers += row.customers;
      return accumulator;
    },
    { gross: 0, net: 0, dbAmount: 0, customers: 0 }
  );

  return [...items, { butikk: "Totalt", client: 99, ...totals }].map((row) => {
    const perCustomer = row.customers === 0 ? 0 : row.gross / row.customers;
    const dgPercent = row.net === 0 ? 0 : (row.dbAmount / row.net) * 100;

    return {
      butikk: row.butikk,
      client: row.client,
      gross: row.gross,
      net: row.net,
      dbAmount: row.dbAmount,
      customers: row.customers,
      perCustomer,
      dgPercent,
      mmoms: formatCurrency(row.gross),
      umoms: formatCurrency(row.net),
      db: formatCurrency(row.dbAmount),
      antord: formatInteger(row.customers),
      prord: formatCurrency(perCustomer),
      dg: formatPercent(dgPercent),
    };
  });
}

function buildMonthToDateRows(state, key, cutoffDay) {
  const dateKeys = state.dayMonthDates.get(key) || [];
  const filtered = dateKeys.filter((dateKey) => Number(String(dateKey).slice(6, 8)) <= cutoffDay);
  const rows = filtered.flatMap((dateKey) => state.dayGrouped.get(dateKey) || []);
  return buildAggregatedRows(rows);
}

function buildWeekRows(state, weekKey, cutoffIsoDay = null) {
  const dateKeys = state.dayWeekDates.get(weekKey) || [];
  const filtered = dateKeys.filter((dateKey) => (cutoffIsoDay ? getIsoWeekInfo(dateKey).isoDay <= cutoffIsoDay : true));
  const rows = filtered.flatMap((dateKey) => state.dayGrouped.get(dateKey) || []);
  return buildAggregatedRows(rows);
}

function buildYearToDateRows(state, year, cutoffMonthDay) {
  const rows = [];

  for (const [dateKey, dateRows] of state.dayGrouped.entries()) {
    const raw = String(dateKey);
    if (Number(raw.slice(0, 4)) !== year) {
      continue;
    }
    if (formatMonthDayKey(raw) <= cutoffMonthDay) {
      rows.push(...dateRows);
    }
  }

  return buildAggregatedRows(rows);
}

function buildDiffRows(selectedRows, compareRows) {
  const compareMap = new Map(compareRows.map((row) => [row.butikk, row]));

  return selectedRows.map((row) => {
    const other = compareMap.get(row.butikk) || {
      gross: 0,
      dbAmount: 0,
      customers: 0,
      dgPercent: 0,
    };

    return {
      butikk: row.butikk,
      client: row.client,
      gross: row.gross - other.gross,
      dbAmount: row.dbAmount - other.dbAmount,
      customers: row.customers - other.customers,
      dgPercent: row.dgPercent - other.dgPercent,
    };
  });
}

function getDefaultCompareKey(targetKey, options) {
  const [year, month] = targetKey.split("-").map(Number);
  const sameMonthLastYear = monthKey(year - 1, month);
  if (options.includes(sameMonthLastYear)) {
    return sameMonthLastYear;
  }

  const fallback = options.find((key) => key !== targetKey);
  return fallback || targetKey;
}

function resolveMonthRows(state, key) {
  if (state.monthMode === "full") {
    return state.monthCanonical.get(key) || [];
  }

  return buildMonthToDateRows(state, key, state.monthCutoffDay);
}

function resolveWeekRows(state, key) {
  if (state.weekMode === "full") {
    return buildWeekRows(state, key, null);
  }

  return buildWeekRows(state, key, state.weekCutoffIsoDay);
}

function resolveYearRows(state, year) {
  if (state.yearMode === "full") {
    return state.yearCanonical.get(year) || [];
  }

  return buildYearToDateRows(state, year, state.yearCutoffMonthDay);
}

function getYearCutoffOptions(state, year) {
  return Array.from(
    new Set(
      state.dayDates
        .filter((dateKey) => String(dateKey).startsWith(String(year)))
        .map((dateKey) => formatMonthDayKey(dateKey))
    )
  ).sort();
}

function getWeekCutoffOptions(state, weekKey) {
  const weekdayLabels = ["", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"];
  return Array.from(
    new Set((state.dayWeekDates.get(weekKey) || []).map((dateKey) => getIsoWeekInfo(dateKey).isoDay))
  )
    .sort((left, right) => left - right)
    .map((isoDay) => ({ isoDay, label: weekdayLabels[isoDay] }));
}

function getDefaultCompareWeekKey(targetWeekKey, options) {
  const [yearText, weekText] = targetWeekKey.split("-W");
  const sameWeekLastYear = `${Number(yearText) - 1}-W${weekText}`;
  if (options.includes(sameWeekLastYear)) {
    return sameWeekLastYear;
  }
  return options.find((key) => key !== targetWeekKey) || targetWeekKey;
}

function registerVisual(kind, instance) {
  activeVisuals.push({ kind, instance });
  if (!resizeVisualsBound) {
    window.addEventListener("resize", () => {
      activeVisuals.forEach((visual) => {
        if (visual.kind === "chartjs") {
          visual.instance.resize();
        }
      });
    });
    resizeVisualsBound = true;
  }
}

function clearVisuals() {
  while (activeVisuals.length > 0) {
    const visual = activeVisuals.pop();
    if (visual.kind === "chartjs") {
      visual.instance.destroy();
    }
  }
}

function buildMonthSeries(state, key, cutoffDay = null) {
  const rows = [];
  const labels = [];
  let runningGross = 0;
  const dateKeys = (state.dayMonthDates.get(key) || []).filter((dateKey) =>
    cutoffDay ? Number(String(dateKey).slice(6, 8)) <= cutoffDay : true
  );

  for (const dateKey of dateKeys) {
    const totals = getTotals(state.dayGrouped.get(dateKey) || []);
    const gross = totals ? totals.gross : 0;
    runningGross += gross;
    labels.push(String(Number(String(dateKey).slice(6, 8))));
    rows.push({ gross, cumulative: runningGross });
  }

  return {
    labels,
    gross: rows.map((row) => row.gross),
    cumulative: rows.map((row) => row.cumulative),
  };
}

function buildYearMonthSeries(state, year) {
  const cutoffMonth = state.yearMode === "ytd" ? Number(state.yearCutoffMonthDay.slice(0, 2)) : 12;
  const labels = [];
  const monthly = [];
  const cumulative = [];
  let runningGross = 0;

  for (let month = 1; month <= cutoffMonth; month += 1) {
    const dateKeys = (state.dayMonthDates.get(monthKey(year, month)) || []).filter((dateKey) =>
      state.yearMode === "ytd" ? formatMonthDayKey(dateKey) <= state.yearCutoffMonthDay : true
    );
    const totals = getTotals(buildRowsForDateKeys(state.dayGrouped, dateKeys));
    const gross = totals ? totals.gross : 0;

    runningGross += gross;
    labels.push(formatShortMonth(month));
    monthly.push(gross);
    cumulative.push(runningGross);
  }

  return { labels, monthly, cumulative };
}

function buildWeekSeries(state, weekKey, cutoffIsoDay = null) {
  const weekdayLabels = ["", "Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"];
  const rows = [];
  let runningGross = 0;
  const dateKeys = (state.dayWeekDates.get(weekKey) || []).filter((dateKey) =>
    cutoffIsoDay ? getIsoWeekInfo(dateKey).isoDay <= cutoffIsoDay : true
  );

  for (const dateKey of dateKeys) {
    const totals = getTotals(state.dayGrouped.get(dateKey) || []);
    const gross = totals ? totals.gross : 0;
    runningGross += gross;
    rows.push({
      isoDay: getIsoWeekInfo(dateKey).isoDay,
      label: weekdayLabels[getIsoWeekInfo(dateKey).isoDay],
      gross,
      cumulative: runningGross,
    });
  }

  return {
    labels: rows.map((row) => row.label),
    gross: rows.map((row) => row.gross),
    cumulative: rows.map((row) => row.cumulative),
  };
}

function formatComparisonDayLabel(dateKey) {
  if (!dateKey) {
    return "";
  }

  const raw = String(dateKey);
  const date = toUtcDate(dateKey);
  const weekday = new Intl.DateTimeFormat("nb-NO", { weekday: "short", timeZone: "UTC" })
    .format(date)
    .replace(/\./g, "")
    .slice(0, 3)
    .toLowerCase();
  const day = raw.slice(6, 8);
  return `${weekday} ${day}`;
}

function getPreviousYearMonthKey(state, selectedMonthKey) {
  const [year, month] = selectedMonthKey.split("-").map(Number);
  const preferred = monthKey(year - 1, month);
  if (state.dayMonthDates.has(preferred)) {
    return preferred;
  }

  const fallback = state.monthOptions.find((key) => {
    const [candidateYear, candidateMonth] = key.split("-").map(Number);
    return candidateMonth === month && candidateYear < year;
  });

  return fallback || null;
}

function buildDayMonthComparison(state, selectedDate, metric = "gross") {
  const { year, month } = parseDateKey(selectedDate);
  const selectedCutoffDay = Number(String(selectedDate).slice(6, 8));
  const selectedMonthKey = monthKey(year, month);
  const compareMonthKey = getPreviousYearMonthKey(state, selectedMonthKey);

  if (!compareMonthKey) {
    return null;
  }

  const compareYear = Number(compareMonthKey.slice(0, 4));
  const compareMonth = Number(compareMonthKey.slice(5, 7));
  const selectedSalesDates = [...(state.dayMonthDates.get(selectedMonthKey) || [])].sort();
  const compareSalesDates = [...(state.dayMonthDates.get(compareMonthKey) || [])].sort();

  if (!selectedSalesDates.length || !compareSalesDates.length) {
    return null;
  }

  const rowCount = Math.max(selectedSalesDates.length, compareSalesDates.length);
  const rows = [];
  let runningDiff = 0;
  let selectedTotal = 0;
  let compareTotal = 0;
  let currentDiff = 0;
  let currentDiffRow = null;
  let selectedCount = 0;
  let compareCount = 0;

  for (let day = 0; day < rowCount; day += 1) {
    const selectedMonthDate = day < selectedSalesDates.length ? selectedSalesDates[day] : null;
    const compareDate = day < compareSalesDates.length ? compareSalesDates[day] : null;
    const compareTotals = compareDate ? getTotals(state.dayGrouped.get(compareDate) || []) : null;
    const selectedTotals = selectedMonthDate ? getTotals(state.dayGrouped.get(selectedMonthDate) || []) : null;
    const compareHasSales = Boolean(compareTotals && compareTotals.butikk !== undefined);
    const selectedHasSales = Boolean(selectedTotals && selectedTotals.butikk !== undefined);
    const compareValue = metric === "db" ? compareTotals?.dbAmount || 0 : compareTotals?.net || 0;
    const selectedValue = metric === "db" ? selectedTotals?.dbAmount || 0 : selectedTotals?.net || 0;

    compareTotal += compareValue;
    selectedTotal += selectedValue;
    runningDiff += selectedValue - compareValue;

    rows.push({
      compareDate,
      selectedDate: selectedMonthDate,
      compareLabel: formatComparisonDayLabel(compareDate),
      selectedLabel: formatComparisonDayLabel(selectedMonthDate),
      compareValue,
      selectedValue,
      runningDiff,
    });

    if (compareHasSales) {
      compareCount += 1;
    }

    if (selectedHasSales) {
      selectedCount += 1;
    }

    if (selectedMonthDate && Number(String(selectedMonthDate).slice(6, 8)) <= selectedCutoffDay) {
      currentDiff = runningDiff;
      currentDiffRow = rows[rows.length - 1];
    }
  }

  return {
    metric,
    metricLabel: metric === "db" ? "DB dag for dag" : "Omsetning u/mva dag for dag",
    diffTitle: "Akk. diff hittil",
    heading: `${monthLabelFromKey(selectedMonthKey)} mot ${monthLabelFromKey(compareMonthKey)}`,
    rowLabelHeader: "Dag",
    metricHeader: "Beløp",
    selectedMonthKey,
    compareMonthKey,
    selectedYear: year,
    compareYear,
    rows,
    selectedTotal,
    compareTotal,
    selectedCount,
    compareCount,
    selectedAverage: selectedCount ? selectedTotal / selectedCount : 0,
    compareAverage: compareCount ? compareTotal / compareCount : 0,
    finalDiff: selectedTotal - compareTotal,
    finalPercentChange: compareTotal ? ((selectedTotal - compareTotal) / compareTotal) * 100 : 0,
    currentDiff,
    currentDiffLabel: currentDiffRow?.selectedLabel || formatComparisonDayLabel(selectedDate) || "",
  };
}

function buildWeekComparison(state, metric = "gross") {
  const selectedYear = Number(state.selectedWeekKey.slice(0, 4));
  const compareYear = Number(state.compareWeekKey.slice(0, 4));
  const selectedWeekNumber = Number(state.selectedWeekKey.slice(6, 8));
  const rows = [];
  let runningDiff = 0;
  let selectedTotal = 0;
  let compareTotal = 0;
  let currentDiff = 0;
  let currentDiffLabel = "";

  for (let week = 1; week <= 52; week += 1) {
    const weekLabel = `Uke ${String(week).padStart(2, "0")}`;
    const selectedTotals = getTotals(buildWeekRows(state, `${selectedYear}-W${String(week).padStart(2, "0")}`, null));
    const compareTotals = getTotals(buildWeekRows(state, `${compareYear}-W${String(week).padStart(2, "0")}`, null));
    const selectedValue = metric === "db" ? selectedTotals?.dbAmount || 0 : selectedTotals?.net || 0;
    const compareValue = metric === "db" ? compareTotals?.dbAmount || 0 : compareTotals?.net || 0;

    compareTotal += compareValue;
    selectedTotal += selectedValue;
    runningDiff += selectedValue - compareValue;

    rows.push({
      compareDate: week,
      selectedDate: week,
      compareLabel: weekLabel,
      selectedLabel: weekLabel,
      compareValue,
      selectedValue,
      runningDiff,
    });

    if (week === selectedWeekNumber) {
      currentDiff = runningDiff;
      currentDiffLabel = weekLabel;
    }
  }

  return {
    metric,
    metricLabel: metric === "db" ? "DB uke for uke" : "Omsetning u/mva uke for uke",
    diffTitle: currentDiffLabel ? `Akk. diff hittil ${currentDiffLabel.toLowerCase()}` : "Akk. diff hittil",
    heading: `${selectedYear} mot ${compareYear}`,
    rowLabelHeader: "Uke",
    metricHeader: metric === "db" ? "DB" : "U/mva",
    selectedYear,
    compareYear,
    rows,
    selectedTotal,
    compareTotal,
    selectedCount: 52,
    compareCount: 52,
    selectedAverage: selectedTotal / 52,
    compareAverage: compareTotal / 52,
    finalDiff: selectedTotal - compareTotal,
    finalPercentChange: compareTotal ? ((selectedTotal - compareTotal) / compareTotal) * 100 : 0,
    currentDiff,
    currentDiffLabel,
  };
}

function buildMonthComparison(state, metric = "gross") {
  const selectedYear = Number(state.selectedMonthKey.slice(0, 4));
  const compareYear = Number(state.compareMonthKey.slice(0, 4));
  const selectedMonthNumber = Number(state.selectedMonthKey.slice(5, 7));
  const rows = [];
  let runningDiff = 0;
  let selectedTotal = 0;
  let compareTotal = 0;
  let currentDiff = 0;
  let currentDiffLabel = "";

  for (let month = 1; month <= 12; month += 1) {
    const monthLabel = formatShortMonth(month);
    const selectedTotals = getTotals(state.monthCanonical.get(monthKey(selectedYear, month)) || []);
    const compareTotals = getTotals(state.monthCanonical.get(monthKey(compareYear, month)) || []);
    const selectedValue = metric === "db" ? selectedTotals?.dbAmount || 0 : selectedTotals?.net || 0;
    const compareValue = metric === "db" ? compareTotals?.dbAmount || 0 : compareTotals?.net || 0;

    compareTotal += compareValue;
    selectedTotal += selectedValue;
    runningDiff += selectedValue - compareValue;

    rows.push({
      compareDate: month,
      selectedDate: month,
      compareLabel: monthLabel,
      selectedLabel: monthLabel,
      compareValue,
      selectedValue,
      runningDiff,
    });

    if (month === selectedMonthNumber) {
      currentDiff = runningDiff;
      currentDiffLabel = monthLabel;
    }
  }

  return {
    metric,
    metricLabel: metric === "db" ? "DB måned for måned" : "Omsetning u/mva måned for måned",
    diffTitle: currentDiffLabel ? `Akk. diff hittil ${currentDiffLabel}` : "Akk. diff hittil",
    heading: `${selectedYear} mot ${compareYear}`,
    rowLabelHeader: "Måned",
    metricHeader: metric === "db" ? "DB" : "U/mva",
    selectedYear,
    compareYear,
    rows,
    selectedTotal,
    compareTotal,
    selectedCount: 12,
    compareCount: 12,
    selectedAverage: selectedTotal / 12,
    compareAverage: compareTotal / 12,
    finalDiff: selectedTotal - compareTotal,
    finalPercentChange: compareTotal ? ((selectedTotal - compareTotal) / compareTotal) * 100 : 0,
    currentDiff,
    currentDiffLabel,
  };
}

function renderDayMonthComparisonCardLegacy(comparison) {
  if (!comparison) {
    return "";
  }

  const triggerDiffClass = (Number.isFinite(comparison.currentDiff) ? comparison.currentDiff : comparison.finalDiff) >= 0 ? "is-positive" : "is-negative";
  const tableDiffClass = comparison.finalDiff >= 0 ? "is-positive" : "is-negative";

  return `
    <article class="day-comparison-card">
      <div class="day-comparison-head">
        <div>
          <p class="summary-label">${comparison.metricLabel}</p>
          <h2>${monthLabelFromKey(comparison.selectedMonthKey)} mot ${monthLabelFromKey(comparison.compareMonthKey)}</h2>
        </div>
        <div class="day-comparison-kpi ${triggerDiffClass}">
          <span>Akk. diff</span>
          <strong>${formatSignedInteger(comparison.finalDiff)}</strong>
        </div>
      </div>

      <div class="day-comparison-table-shell">
        <table class="day-comparison-table compact-report-table">
          <colgroup>
            <col class="day-comparison-col-day" />
            <col class="day-comparison-col-amount" />
            <col class="day-comparison-col-amount" />
            <col class="day-comparison-col-day" />
            <col class="day-comparison-col-diff" />
          </colgroup>
          <thead>
            <tr>
              <th colspan="2">${comparison.compareYear}</th>
              <th colspan="2">${comparison.selectedYear}</th>
              <th rowspan="2">Akk. diff</th>
            </tr>
            <tr>
              <th>Dag</th>
              <th>Beløp</th>
              <th>Beløp</th>
              <th>Dag</th>
            </tr>
          </thead>
          <tbody>
            ${comparison.rows
              .map(
                (row) => `
                <tr>
                    <td class="day-label-cell">${row.compareLabel || ""}</td>
                    <td>${row.compareDate ? formatInteger(row.compareValue) : ""}</td>
                    <td>${row.selectedDate ? formatInteger(row.selectedValue) : ""}</td>
                    <td class="day-label-cell">${row.selectedLabel || ""}</td>
                    <td class="${row.runningDiff >= 0 ? "is-positive" : "is-negative"}">${formatSignedInteger(row.runningDiff)}</td>
                  </tr>
                `
              )
              .join("")}
          </tbody>
          <tfoot>
            <tr>
              <th>Totalt</th>
              <th>${formatInteger(comparison.compareTotal)}</th>
              <th>${formatInteger(comparison.selectedTotal)}</th>
              <th></th>
              <th class="${tableDiffClass}">${formatSignedInteger(comparison.finalDiff)}</th>
            </tr>
            <tr>
              <th>Snitt</th>
              <th>${formatInteger(comparison.compareAverage)}</th>
              <th>${formatInteger(comparison.selectedAverage)}</th>
              <th></th>
              <th class="${tableDiffClass}">${comparison.finalPercentChange.toFixed(2).replace(".", ",")} %</th>
            </tr>
            <tr>
              <th>Dager</th>
              <th>${formatInteger(comparison.compareCount)}</th>
              <th>${formatInteger(comparison.selectedCount)}</th>
              <th></th>
              <th></th>
            </tr>
          </tfoot>
        </table>
      </div>
    </article>
  `;
}

function renderDayMonthComparisonCard(comparison, expanded = false) {
  if (!comparison) {
    return "";
  }

  const diffValue = Number.isFinite(comparison.currentDiff) ? comparison.currentDiff : comparison.finalDiff;
  const triggerDiffClass = diffValue >= 0 ? "is-positive" : "is-negative";
  const tableDiffClass = comparison.finalDiff >= 0 ? "is-positive" : "is-negative";
  const diffTitle = comparison.diffTitle || "Akk. diff hittil";
  const heading = comparison.heading || `${monthLabelFromKey(comparison.selectedMonthKey)} mot ${monthLabelFromKey(comparison.compareMonthKey)}`;
  const rowLabelHeader = comparison.rowLabelHeader || "Dag";
  const metricHeader = comparison.metricHeader || "Beløp";
  const rowTotalsLabel = comparison.rowTotalsLabel || "Dager";
  const leftYear = comparison.compareYear;
  const rightYear = comparison.selectedYear;

  return `
    <article class="day-comparison-card ${expanded ? "is-expanded" : "is-collapsed"}">
      <button
        class="day-comparison-trigger"
        type="button"
        data-day-comparison-toggle="${comparison.metric}"
        aria-expanded="${expanded ? "true" : "false"}"
      >
        <p class="summary-label">${comparison.metricLabel}</p>
        <div class="day-comparison-kpi ${triggerDiffClass}">
          <span>${diffTitle}</span>
          <strong>${formatSignedInteger(diffValue)}</strong>
        </div>
      </button>

      ${expanded
        ? `
          <div class="day-comparison-body">
            <div class="day-comparison-head">
              <div>
                <h2>${monthLabelFromKey(comparison.selectedMonthKey)} mot ${monthLabelFromKey(comparison.compareMonthKey)}</h2>
              </div>
            </div>

            <div class="day-comparison-table-shell">
              <table class="day-comparison-table compact-report-table">
                <colgroup>
                  <col class="day-comparison-col-day" />
                  <col class="day-comparison-col-amount" />
                  <col class="day-comparison-col-amount" />
                  <col class="day-comparison-col-day" />
                  <col class="day-comparison-col-diff" />
                </colgroup>
                <thead>
                  <tr>
                    <th colspan="2">${comparison.compareYear}</th>
                    <th colspan="2">${comparison.selectedYear}</th>
                    <th rowspan="2">Akk. diff</th>
                  </tr>
                  <tr>
                    <th>Dag</th>
                    <th>Beløp</th>
                    <th>Beløp</th>
                    <th>Dag</th>
                  </tr>
                </thead>
                <tbody>
                  ${comparison.rows
                    .map(
                      (row) => `
                      <tr>
                          <td class="day-label-cell">${row.compareLabel || ""}</td>
                          <td>${row.compareDate ? formatInteger(row.compareValue) : ""}</td>
                          <td>${row.selectedDate ? formatInteger(row.selectedValue) : ""}</td>
                          <td class="day-label-cell">${row.selectedLabel || ""}</td>
                          <td class="${row.runningDiff >= 0 ? "is-positive" : "is-negative"}">${formatSignedInteger(row.runningDiff)}</td>
                        </tr>
                      `
                    )
                    .join("")}
                </tbody>
                <tfoot>
                  <tr>
                    <th>Totalt</th>
                    <th>${formatInteger(comparison.compareTotal)}</th>
                    <th>${formatInteger(comparison.selectedTotal)}</th>
                    <th></th>
                    <th class="${tableDiffClass}">${formatSignedInteger(comparison.finalDiff)}</th>
                  </tr>
                  <tr>
                    <th>Snitt</th>
                    <th>${formatInteger(comparison.compareAverage)}</th>
                    <th>${formatInteger(comparison.selectedAverage)}</th>
                    <th></th>
                    <th class="${tableDiffClass}">${comparison.finalPercentChange.toFixed(2).replace(".", ",")} %</th>
                  </tr>
                  <tr>
                    <th>Dager</th>
                    <th>${formatInteger(comparison.compareCount)}</th>
                    <th>${formatInteger(comparison.selectedCount)}</th>
                    <th></th>
                    <th></th>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        `
        : ""}
    </article>
  `;
}

function renderPeriodComparisonCard(comparison, expanded = false) {
  if (!comparison) {
    return "";
  }

  const diffValue = Number.isFinite(comparison.currentDiff) ? comparison.currentDiff : comparison.finalDiff;
  const triggerDiffClass = diffValue >= 0 ? "is-positive" : "is-negative";
  const tableDiffClass = comparison.finalDiff >= 0 ? "is-positive" : "is-negative";
  const diffTitle = comparison.diffTitle || "Akk. diff hittil";
  const heading = comparison.heading || "";
  const rowLabelHeader = comparison.rowLabelHeader || "Periode";
  const metricHeader = comparison.metricHeader || "Beløp";
  const rowTotalsLabel = comparison.rowTotalsLabel || "Punkter";
  const leftYear = comparison.compareYear;
  const rightYear = comparison.selectedYear;

  return `
    <article class="day-comparison-card ${expanded ? "is-expanded" : "is-collapsed"}">
      <button
        class="day-comparison-trigger"
        type="button"
        data-period-comparison-toggle="${comparison.metric}"
        aria-expanded="${expanded ? "true" : "false"}"
      >
        <p class="summary-label">${comparison.metricLabel}</p>
        <div class="day-comparison-kpi ${triggerDiffClass}">
          <span>${diffTitle}</span>
          <strong>${formatSignedInteger(diffValue)}</strong>
        </div>
      </button>

      ${expanded
        ? `
          <div class="day-comparison-body">
            <div class="day-comparison-head">
              <div>
                <h2>${heading}</h2>
              </div>
            </div>

            <div class="day-comparison-table-shell">
              <table class="day-comparison-table compact-report-table">
                <colgroup>
                  <col class="day-comparison-col-day" />
                  <col class="day-comparison-col-amount" />
                  <col class="day-comparison-col-amount" />
                  <col class="day-comparison-col-day" />
                  <col class="day-comparison-col-diff" />
                </colgroup>
                <thead>
                  <tr>
                    <th colspan="2">${leftYear}</th>
                    <th colspan="2">${rightYear}</th>
                    <th rowspan="2">Akk. diff</th>
                  </tr>
                  <tr>
                    <th>${rowLabelHeader}</th>
                    <th>${metricHeader}</th>
                    <th>${metricHeader}</th>
                    <th>${rowLabelHeader}</th>
                  </tr>
                </thead>
                <tbody>
                  ${comparison.rows
                    .map(
                      (row) => `
                      <tr>
                          <td class="day-label-cell">${row.compareLabel || ""}</td>
                          <td>${formatInteger(row.compareValue)}</td>
                          <td>${formatInteger(row.selectedValue)}</td>
                          <td class="day-label-cell">${row.selectedLabel || ""}</td>
                          <td class="${row.runningDiff >= 0 ? "is-positive" : "is-negative"}">${formatSignedInteger(row.runningDiff)}</td>
                        </tr>
                      `
                    )
                    .join("")}
                </tbody>
                <tfoot>
                  <tr>
                    <th>Totalt</th>
                    <th>${formatInteger(comparison.compareTotal)}</th>
                    <th>${formatInteger(comparison.selectedTotal)}</th>
                    <th></th>
                    <th class="${tableDiffClass}">${formatSignedInteger(comparison.finalDiff)}</th>
                  </tr>
                  <tr>
                    <th>Snitt</th>
                    <th>${formatInteger(comparison.compareAverage)}</th>
                    <th>${formatInteger(comparison.selectedAverage)}</th>
                    <th></th>
                    <th class="${tableDiffClass}">${comparison.finalPercentChange.toFixed(2).replace(".", ",")} %</th>
                  </tr>
                  <tr>
                    <th>${rowTotalsLabel}</th>
                    <th>${formatInteger(comparison.compareCount)}</th>
                    <th>${formatInteger(comparison.selectedCount)}</th>
                    <th></th>
                    <th></th>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        `
        : ""}
    </article>
  `;
}

function sellerMatchesQuery(name, query) {
  const normalizedName = normalizeText(name);
  const normalizedQuery = normalizeText(query);
  if (!normalizedQuery) {
    return true;
  }
  return normalizedName.includes(normalizedQuery);
}

function buildSellerRanking(rows, metric) {
  return [...rows]
    .sort((left, right) => {
      const delta = right[metric] - left[metric];
      if (delta !== 0) {
        return delta;
      }
      return left.navn.localeCompare(right.navn, "nb-NO");
    })
    .map((row, index) => ({ ...row, rank: index + 1 }));
}

function parseSellerDateKey(dateKey) {
  const raw = String(dateKey || "");
  return /^\d{8}$/.test(raw) ? raw : null;
}

function getSellerSelectedDate(state) {
  const candidate = parseSellerDateKey(state.sellerSelectedDate) || parseSellerDateKey(state.sellerLatestDay);
  if (!candidate) {
    return null;
  }
  return state.dayGrouped?.has(candidate) ? candidate : String(state.sellerLatestDay);
}

function buildSellerPeriodData(state) {
  const selectedDate = getSellerSelectedDate(state);
  const rawRows = Array.isArray(state.sellerRawRows) ? state.sellerRawRows : [];
  if (!selectedDate) {
    return {
      selectedDate: null,
      selectedMonthKey: null,
      selectedYear: null,
      dayRows: [],
      monthRows: [],
      yearRows: [],
    };
  }

  const selectedYear = Number(String(selectedDate).slice(0, 4));
  const selectedMonth = Number(String(selectedDate).slice(4, 6));
  const selectedMonthKey = monthKey(selectedYear, selectedMonth);

  const dayRows = rawRows.filter((row) => row.fakturadato === Number(selectedDate));
  const monthRows = rawRows.filter(
    (row) =>
      Number(String(row.fakturadato).slice(0, 4)) === selectedYear &&
      Number(String(row.fakturadato).slice(4, 6)) === selectedMonth
  );
  const yearRows = rawRows.filter((row) => Number(String(row.fakturadato).slice(0, 4)) === selectedYear);

  return {
    selectedDate,
    selectedMonthKey,
    selectedYear,
    dayRows: aggregateSellerRows(dayRows),
    monthRows: aggregateSellerRows(monthRows),
    yearRows: aggregateSellerRows(yearRows),
  };
}

function renderNav(page) {
  const pages = [
    ["day", "Dag"],
    ["week", "Uke"],
    ["month", "Måned"],
    ["year", "År"],
    ["people", "Selgere"],
    ["stock", "Stock"],
  ];

  return `
    <nav class="beta-nav" aria-label="Hovednavigasjon">
      ${pages
        .map(([key, label]) => {
          if (key === "day" || key === "week" || key === "month" || key === "year" || key === "people" || key === "stock") {
            const className = page === key ? "nav-pill is-active" : "nav-pill";
            return `<button class="${className}" type="button" data-page="${key}">${label}</button>`;
          }
          return `<button class="nav-pill" type="button" disabled>${label}</button>`;
        })
        .join("")}
    </nav>
  `;
}

function getPageLabel(page) {
  const labels = {
    day: "DAG",
    week: "UKE",
    month: "MÅNED",
    year: "ÅR",
    people: "SELGERE",
    stock: "STOCK",
  };

  return labels[page] || "DAG";
}

function renderChrome(state, controlsHtml = "") {
  return `
    <section class="chrome-shell is-expanded">
      <div class="chrome-panel is-expanded">
        ${renderNav(state.page)}
        ${controlsHtml}
      </div>
    </section>
  `;
}

function renderSummaryCard(title, totals, modifier = "") {
  if (!totals) {
    return "";
  }

  return `
    <article class="summary-card ${modifier}">
      <p class="summary-label">${title}</p>
      <h3>${totals.mmoms}</h3>
      <div class="summary-grid">
        <div><span>DB</span><strong>${totals.db}</strong></div>
        <div><span>DG</span><strong>${totals.dg}</strong></div>
        <div><span>Kunder</span><strong>${totals.antord}</strong></div>
        <div><span>Per kunde</span><strong>${totals.prord}</strong></div>
      </div>
    </article>
  `;
}

function renderDeltaCard(selectedTotals, compareTotals) {
  if (!selectedTotals || !compareTotals) {
    return "";
  }

  const grossDelta = selectedTotals.gross - compareTotals.gross;
  const dbDelta = selectedTotals.dbAmount - compareTotals.dbAmount;
  const customerDelta = selectedTotals.customers - compareTotals.customers;
  const dgDelta = selectedTotals.dgPercent - compareTotals.dgPercent;

  return `
    <article class="summary-card">
      <p class="summary-label">Differanse</p>
      <h3>${formatSignedCurrency(grossDelta)}</h3>
      <div class="summary-grid">
        <div><span>DB</span><strong>${formatSignedCurrency(dbDelta)}</strong></div>
        <div><span>DG</span><strong>${formatSignedPercentPoints(dgDelta)}</strong></div>
        <div><span>Kunder</span><strong>${formatSignedInteger(customerDelta)}</strong></div>
        <div><span>Retning</span><strong>${grossDelta >= 0 ? "Over" : "Under"}</strong></div>
      </div>
    </article>
  `;
}

function renderWeekExpandableSummaryCard(
  title,
  totals,
  detailContent,
  expanded = false,
  modifier = "",
  toggleAttr = "data-week-panels-toggle",
  secondaryLabel = "",
  secondaryValue = "",
  secondaryItems = [],
  gridItems = null,
  summaryGridHtml = ""
) {
  if (!totals) {
    return "";
  }

  const sideEntries = [];
  if (secondaryLabel && secondaryValue) {
    sideEntries.push({ label: secondaryLabel, value: secondaryValue });
  }
  if (Array.isArray(secondaryItems) && secondaryItems.length) {
    sideEntries.push(...secondaryItems);
  }

  const sideBlock = sideEntries.length
    ? `
        <div class="summary-side ${sideEntries.length > 1 ? "summary-side-stack" : ""}">
          ${sideEntries
            .map(
              (entry) => `
                <div class="summary-side-item">
                  <span>${entry.label}</span>
                  <strong>${entry.value}</strong>
                </div>
              `
            )
            .join("")}
        </div>
      `
    : "";

  const defaultGridItems = [
    { label: "DB", value: totals.db },
    { label: "DG", value: totals.dg },
    { label: "Kunder", value: totals.antord },
    { label: "Per kunde", value: totals.prord },
  ];
  const summaryGridItems = Array.isArray(gridItems) && gridItems.length ? gridItems : defaultGridItems;
  const gridMarkup = summaryGridHtml
    ? summaryGridHtml
    : `
        <div class="summary-grid">
          ${summaryGridItems
            .map(
              (entry) => `
                <div><span>${entry.label}</span><strong>${entry.value}</strong></div>
              `
            )
            .join("")}
        </div>
      `;

  return `
    <article class="summary-card week-summary-card ${modifier} ${expanded ? "is-expanded" : ""}">
      <button
        class="week-summary-trigger"
        type="button"
        ${toggleAttr}
        aria-expanded="${expanded ? "true" : "false"}"
      >
        <p class="summary-label">${title}</p>
        <div class="summary-topline">
          <div class="summary-topline-main">
            <h3>${totals.mmoms}</h3>
          </div>
          ${sideBlock}
        </div>
        ${gridMarkup}
      </button>
      ${expanded ? `<div class="week-summary-detail">${detailContent}</div>` : ""}
    </article>
  `;
}

function buildSummaryMetricsHtml(totals) {
  return `
    <div class="day-summary-metrics">
      <div class="day-summary-metric-column">
        <div><span>DB</span><strong>${totals.db}</strong></div>
        <div><span>DG</span><strong>${totals.dg}</strong></div>
      </div>
      <div class="day-summary-metric-column">
        <div><span>Kunder</span><strong>${totals.antord}</strong></div>
        <div><span>Pr. k.</span><strong>${totals.prord}</strong></div>
      </div>
    </div>
  `;
}

function renderWeekExpandableDeltaCard(
  selectedTotals,
  compareTotals,
  detailContent,
  expanded = false,
  toggleAttr = "data-week-panels-toggle"
) {
  if (!selectedTotals || !compareTotals) {
    return "";
  }

  const grossDelta = selectedTotals.gross - compareTotals.gross;
  const dbDelta = selectedTotals.dbAmount - compareTotals.dbAmount;
  const customerDelta = selectedTotals.customers - compareTotals.customers;
  const dgDelta = selectedTotals.dgPercent - compareTotals.dgPercent;

  return `
    <article class="summary-card week-summary-card ${expanded ? "is-expanded" : ""}">
      <button
        class="week-summary-trigger"
        type="button"
        ${toggleAttr}
        aria-expanded="${expanded ? "true" : "false"}"
      >
        <p class="summary-label">Differanse</p>
        <h3>${formatSignedCurrency(grossDelta)}</h3>
        <div class="summary-grid">
          <div><span>DB</span><strong>${formatSignedCurrency(dbDelta)}</strong></div>
          <div><span>DG</span><strong>${formatSignedPercentPoints(dgDelta)}</strong></div>
          <div><span>Kunder</span><strong>${formatSignedInteger(customerDelta)}</strong></div>
          <div><span>Retning</span><strong>${grossDelta >= 0 ? "Over" : "Under"}</strong></div>
        </div>
      </button>
      ${expanded ? `<div class="week-summary-detail">${detailContent}</div>` : ""}
    </article>
  `;
}

function renderProjectionCard(state, key) {
  const [year, month] = key.split("-").map(Number);
  const forecast = state.monthCompareData.find(
    (row) => row.butikk === "Totalt" && row.thisYear === year && row.month === month && row.incomplete === null
  );

  if (!forecast) {
    return "";
  }

  return `
    <article class="summary-card summary-projection">
      <p class="summary-label">Prognose denne måneden</p>
      <h3>${forecast.mmoms}</h3>
      <div class="summary-grid">
        <div><span>DB</span><strong>${forecast.db}</strong></div>
        <div><span>DG</span><strong>${forecast.dg}</strong></div>
        <div><span>Kunder</span><strong>${forecast.antord}</strong></div>
        <div><span>Per kunde</span><strong>${forecast.prord}</strong></div>
      </div>
    </article>
  `;
}

function renderDesktopTable(rows) {
  return `
    <div class="table-shell desktop-only">
      <table class="store-table">
        <thead>
          <tr>
            <th>Butikk</th>
            <th>Beløp m/moms</th>
            <th>Beløp u/moms</th>
            <th>DB</th>
            <th>DG</th>
            <th>Antall kunder</th>
            <th>Per kunde</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr class="${rowClass(row)}">
                  <td>${row.butikk}</td>
                  <td>${row.mmoms}</td>
                  <td>${row.umoms}</td>
                  <td>${row.db}</td>
                  <td>${row.dg}</td>
                  <td>${row.antord}</td>
                  <td>${row.prord}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderMobileCards(rows) {
  return `
    <div class="mobile-only mobile-store-list">
      ${rows
        .map((row) => {
          const totalClass = row.butikk === "Totalt" ? "mobile-store-card total-card" : "mobile-store-card";
          return `
            <article class="${totalClass}">
              <div class="mobile-store-head">
                <h3>${row.butikk}</h3>
                <strong>${row.mmoms}</strong>
              </div>
              <div class="mobile-store-meta">
                <div><span>DB</span><strong>${row.db}</strong></div>
                <div><span>DG</span><strong>${row.dg}</strong></div>
                <div><span>Kunder</span><strong>${row.antord}</strong></div>
                <div><span>Per kunde</span><strong>${row.prord}</strong></div>
              </div>
              <p class="mobile-store-foot">Beløp u/moms: ${row.umoms}</p>
            </article>
          `;
        })
        .join("")}
    </div>
  `;
}

function compactMoneyText(value) {
  return String(value || "").replace(/\s*kr$/u, "");
}

function renderDayMobileTable(rows) {
  return `
    <div class="mobile-only day-mobile-table-shell">
      <table class="store-table day-mobile-table">
        <colgroup>
          <col class="day-mobile-col-store" />
          <col class="day-mobile-col-amount" />
          <col class="day-mobile-col-diff" />
          <col class="day-mobile-col-diff" />
          <col class="day-mobile-col-customers" />
          <col class="day-mobile-col-customers" />
        </colgroup>
        <thead>
          <tr>
            <th>Butikk</th>
            <th>u/mva</th>
            <th>DB</th>
            <th>DG</th>
            <th>Kunder</th>
            <th>pr. k.</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr class="${row.butikk === "Totalt" ? "total-row" : ""}">
                  <td class="day-mobile-store-cell">${row.butikk}</td>
                  <td>${compactMoneyText(row.umoms)}</td>
                  <td>${compactMoneyText(row.db)}</td>
                  <td>${row.dg}</td>
                  <td>${row.antord}</td>
                  <td>${compactMoneyText(row.prord)}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderDiffTable(rows) {
  return `
    <div class="desktop-only table-shell period-diff-table-shell">
      <table class="store-table">
        <thead>
          <tr>
            <th>Butikk</th>
            <th>Omsetning diff</th>
            <th>DB diff</th>
            <th>DG diff</th>
            <th>Kunder diff</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr class="${row.butikk === "Totalt" ? "store-row total-row" : "store-row"}">
                  <td>${row.butikk}</td>
                  <td>${formatSignedCurrency(row.gross)}</td>
                  <td>${formatSignedCurrency(row.dbAmount)}</td>
                  <td>${formatSignedPercentPoints(row.dgPercent)}</td>
                  <td>${formatSignedInteger(row.customers)}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
    <div class="mobile-only day-mobile-table-shell">
      <table class="store-table day-mobile-table period-diff-mobile-table">
        <colgroup>
          <col class="period-diff-col-store" />
          <col class="period-diff-col-amount" />
          <col class="period-diff-col-diff" />
          <col class="period-diff-col-diff" />
          <col class="period-diff-col-customers" />
        </colgroup>
        <thead>
          <tr>
            <th>Butikk</th>
            <th>Omsetning diff</th>
            <th>DB diff</th>
            <th>DG diff</th>
            <th>Kunder diff</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr class="${row.butikk === "Totalt" ? "total-row" : ""}">
                  <td class="day-mobile-store-cell">${row.butikk}</td>
                  <td>${compactMoneyText(formatSignedCurrency(row.gross))}</td>
                  <td>${compactMoneyText(formatSignedCurrency(row.dbAmount))}</td>
                  <td>${formatSignedPercentPoints(row.dgPercent)}</td>
                  <td>${formatSignedInteger(row.customers)}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderMonthChartsBlock() {
  return renderMonthChartsStandaloneClean();
  return `
    <section class="month-block">
      <div class="history-head">
        <p class="section-label">Visualisering</p>
        <h2>Måned i bevegelse</h2>
      </div>
      <div class="chart-grid">
        <article class="chart-card">
          <h3>Kumulativ utvikling dag for dag</h3>
          <canvas id="month-cumulative-chart"></canvas>
          <p class="chart-caption">Her ser vi hvordan valgt måned og sammenligningsmåned bygger seg opp gjennom perioden.</p>
        </article>
        <article class="chart-card">
          <h3>Butikkvis omsetning</h3>
          <canvas id="month-store-chart"></canvas>
          <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som drar opp eller ned forskjellen mellom periodene.</p>
        </article>
      </div>
    </section>
  `;
}

function renderMonthChartsStandaloneClean() {
  return `
    <div class="chart-grid chart-grid-standalone">
      <article class="chart-card">
        <h3>Kumulativ utvikling dag for dag</h3>
        <canvas id="month-cumulative-chart"></canvas>
        <p class="chart-caption">Her ser vi hvordan valgt måned og sammenligningsmåned bygger seg opp gjennom perioden.</p>
      </article>
      <article class="chart-card">
        <h3>Butikkvis omsetning</h3>
        <canvas id="month-store-chart"></canvas>
        <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som drar opp eller ned forskjellen mellom periodene.</p>
      </article>
    </div>
  `;
}

function renderMonthChartsStandalone() {
  return `
    <div class="chart-grid chart-grid-standalone">
      <article class="chart-card">
        <h3>Kumulativ utvikling dag for dag</h3>
        <canvas id="month-cumulative-chart"></canvas>
        <p class="chart-caption">Her ser vi hvordan valgt måned og sammenligningsmåned bygger seg opp gjennom perioden.</p>
      </article>
      <article class="chart-card">
        <h3>Butikkvis omsetning</h3>
        <canvas id="month-store-chart"></canvas>
        <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som drar opp eller ned forskjellen mellom periodene.</p>
      </article>
    </div>
  `;
}

function renderWeekChartsBlock() {
  return renderWeekChartsStandaloneClean();
  return `
    <section class="month-block">
      <div class="history-head">
        <p class="section-label">Visualisering</p>
        <h2>Uken som kurver og søyler</h2>
      </div>
      <div class="chart-grid">
        <article class="chart-card">
          <h3>Kumulativ utvikling gjennom uken</h3>
          <canvas id="week-cumulative-chart"></canvas>
          <p class="chart-caption">Her ser vi hvordan valgt uke og sammenligningsuken bygger seg opp dag for dag.</p>
        </article>
        <article class="chart-card">
          <h3>Butikkvis omsetning</h3>
          <canvas id="week-store-chart"></canvas>
          <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som bærer uken og forskjellene mellom ukene.</p>
        </article>
      </div>
    </section>
  `;
}

function renderWeekChartsStandaloneClean() {
  return `
    <div class="chart-grid chart-grid-standalone">
      <article class="chart-card">
        <h3>Kumulativ utvikling gjennom uken</h3>
        <canvas id="week-cumulative-chart"></canvas>
        <p class="chart-caption">Her ser vi hvordan valgt uke og sammenligningsuken bygger seg opp dag for dag.</p>
      </article>
      <article class="chart-card">
        <h3>Butikkvis omsetning</h3>
        <canvas id="week-store-chart"></canvas>
        <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som bærer uken og forskjellene mellom ukene.</p>
      </article>
    </div>
  `;
}

function renderWeekChartsStandalone() {
  return `
    <div class="chart-grid chart-grid-standalone">
      <article class="chart-card">
        <h3>Kumulativ utvikling gjennom uken</h3>
        <canvas id="week-cumulative-chart"></canvas>
        <p class="chart-caption">Her ser vi hvordan valgt uke og sammenligningsuken bygger seg opp dag for dag.</p>
      </article>
      <article class="chart-card">
        <h3>Butikkvis omsetning</h3>
        <canvas id="week-store-chart"></canvas>
        <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som bærer uken og forskjellene mellom ukene.</p>
      </article>
    </div>
  `;
}

function renderYearChartsBlock() {
  return renderYearChartsStandaloneClean();
  return `
    <section class="month-block">
      <div class="history-head">
        <p class="section-label">Visualisering</p>
        <h2>Året som kurver og søyler</h2>
      </div>
      <div class="chart-grid">
        <article class="chart-card">
          <h3>Kumulativ utvikling gjennom året</h3>
          <canvas id="year-cumulative-chart"></canvas>
          <p class="chart-caption">Her sammenligner vi hvordan årene bygger seg opp måned for måned.</p>
        </article>
        <article class="chart-card">
          <h3>Butikkvis omsetning</h3>
          <canvas id="year-store-chart"></canvas>
          <p class="chart-caption">Denne gir en raskere følelse av nivåforskjellene mellom butikkene på årsbasis.</p>
        </article>
      </div>
    </section>
  `;
}

function renderYearChartsStandaloneClean() {
  return `
    <div class="chart-grid chart-grid-standalone">
      <article class="chart-card">
        <h3>Kumulativ utvikling måned for måned</h3>
        <canvas id="year-cumulative-chart"></canvas>
        <p class="chart-caption">Her ser vi hvordan valgt år og sammenligningsåret bygger seg opp gjennom året.</p>
      </article>
      <article class="chart-card">
        <h3>Butikkvis omsetning</h3>
        <canvas id="year-store-chart"></canvas>
        <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som drar opp eller ned forskjellen mellom årene.</p>
      </article>
    </div>
  `;
}

function renderYearChartsStandalone() {
  return `
    <div class="chart-grid chart-grid-standalone">
      <article class="chart-card">
        <h3>Kumulativ utvikling måned for måned</h3>
        <canvas id="year-cumulative-chart"></canvas>
        <p class="chart-caption">Her ser vi hvordan valgt år og sammenligningsåret bygger seg opp gjennom året.</p>
      </article>
      <article class="chart-card">
        <h3>Butikkvis omsetning</h3>
        <canvas id="year-store-chart"></canvas>
        <p class="chart-caption">Dette gjør det lettere å se hvilke butikker som drar opp eller ned forskjellen mellom årene.</p>
      </article>
    </div>
  `;
}

function renderSellerMetricToggle(state) {
  return `
    <div class="mode-picker">
      <button class="${state.sellerMetric === "umomsValue" ? "quick-button is-active" : "quick-button"}" type="button" data-seller-metric="umomsValue">Omsetning u/moms</button>
      <button class="${state.sellerMetric === "dbValue" ? "quick-button is-active" : "quick-button"}" type="button" data-seller-metric="dbValue">DB</button>
    </div>
  `;
}

function renderSellerRows(rows, metric) {
  const metricLabel = metric === "dbValue" ? "DB" : "U/moms";
  const metricField = metric === "dbValue" ? "db" : "umoms";

  return `
    <div class="seller-list">
      ${
        rows.length > 0
          ? rows
              .map(
                (row) => `
                  <article class="seller-row">
                    <div class="seller-rank">#${row.rank}</div>
                    <div class="seller-copy">
                      <h3>${row.navn}</h3>
                      <p>${row.butikk}</p>
                    </div>
                    <div class="seller-metrics">
                      <strong>${row[metricField]}</strong>
                      <span>${metricLabel}</span>
                    </div>
                  </article>
                `
              )
              .join("")
          : `<p class="chart-caption">Ingen treff i denne perioden.</p>`
      }
    </div>
  `;
}

function renderSellerList(title, subtitle, rows, metric, expanded = false, query = "") {
  const previewRows = query ? rows : rows.slice(0, 3);
  const expandedRows = query ? [] : rows.slice(3, 20);
  const hasMore = !query && expandedRows.length > 0;
  const countLabel = query ? `${rows.length} treff` : `Topp ${Math.min(3, rows.length)} av ${Math.min(20, rows.length)}`;

  return `
    <details class="month-block seller-block seller-section" ${(query || expanded) ? "open" : ""}>
      <summary>
        <div class="history-head seller-block-head">
          <div>
            <p class="section-label">${subtitle}</p>
            <h2>${title}</h2>
          </div>
          <p class="seller-count">${countLabel}</p>
        </div>
        ${renderSellerRows(previewRows, metric)}
      </summary>
      ${
        hasMore
          ? `
      <div class="seller-section-body">
        ${renderSellerRows(expandedRows, metric)}
      </div>
      `
          : query
            ? ""
            : `<div class="seller-section-body"><p class="chart-caption">Ingen flere selgere i topp 20.</p></div>`
      }
    </details>
  `;
}

function getSellerRankings(state) {
  return {
    dayRanking: buildSellerRanking(state.sellerDayRows, state.sellerMetric),
    monthRanking: buildSellerRanking(state.sellerMonthRows, state.sellerMetric),
    yearRanking: buildSellerRanking(state.sellerYearRows, state.sellerMetric),
    query: state.sellerQuery.trim(),
  };
}

function renderPeopleCards(state) {
  const { query } = getSellerRankings(state);
  const periodData = buildSellerPeriodData(state);
  const filterRows = (rows) => {
    if (!query) {
      return rows;
    }
    return rows.filter((row) => sellerMatchesQuery(row.navn, query));
  };

  const dayRanking = buildSellerRanking(periodData.dayRows, state.sellerMetric);
  const monthRanking = buildSellerRanking(periodData.monthRows, state.sellerMetric);
  const yearRanking = buildSellerRanking(periodData.yearRows, state.sellerMetric);

  return `
    ${renderSellerList("Dag", formatDateLabel(periodData.selectedDate || state.sellerLatestDay), filterRows(dayRanking), state.sellerMetric, false, query)}
    ${renderSellerList("Måned", monthLabelFromKey(periodData.selectedMonthKey || state.sellerLatestMonthKey), filterRows(monthRanking), state.sellerMetric, false, query)}
    ${renderSellerList("År", String(periodData.selectedYear || state.sellerLatestYear), filterRows(yearRanking), state.sellerMetric, false, query)}
  `;
}

function stockMatchesQuery(row, query) {
  const normalizedQuery = normalizeText(query);
  if (!normalizedQuery) {
    return true;
  }
  return row.searchText.includes(normalizedQuery);
}

function filterStockRows(state) {
  return state.stockRows.filter((row) => {
    const matchesQuery = stockMatchesQuery(row, state.stockQuery);
    if (!matchesQuery) {
      return false;
    }
    if (state.stockFilter === "incoming") {
      return row.palletsIncoming > 0;
    }
    if (state.stockFilter === "empty") {
      return row.stockAmount <= 0;
    }
    return true;
  });
}

function buildStockStats(rows) {
  return rows.reduce(
    (accumulator, row) => {
      accumulator.items += 1;
      accumulator.palletsInStock += row.palletsInStock;
      accumulator.palletsIncoming += row.palletsIncoming;
      if (row.palletsIncoming > 0) {
        accumulator.incomingItems += 1;
      }
      if (row.stockAmount <= 0) {
        accumulator.emptyItems += 1;
      }
      return accumulator;
    },
    { items: 0, incomingItems: 0, emptyItems: 0, palletsInStock: 0, palletsIncoming: 0 }
  );
}

function renderStockMetricCard(label, value, note, modifier = "") {
  return `
    <article class="summary-card ${modifier}">
      <p class="summary-label">${label}</p>
      <h3>${value}</h3>
      <p class="chart-caption">${note}</p>
    </article>
  `;
}

function renderStockFilterToggle(state) {
  const options = [
    ["all", "Alle"],
    ["incoming", "På vei"],
    ["empty", "Tomt lager"],
  ];

  return `
    <div class="mode-picker">
      ${options
        .map(
          ([value, label]) =>
            `<button class="${state.stockFilter === value ? "quick-button is-active" : "quick-button"}" type="button" data-stock-filter="${value}">${label}</button>`
        )
        .join("")}
    </div>
  `;
}

function renderStockOrderSummary(row) {
  if (row.orders.length === 0) {
    return `<span class="stock-empty-note">Ingen registrerte bestillinger</span>`;
  }

  return `
    <div class="stock-order-list">
      ${row.orders
        .map(
          (order) => `
            <span class="stock-order-pill">
              <strong>${order.week}</strong>
              <span>${order.amountLabel}</span>
            </span>
          `
        )
        .join("")}
    </div>
  `;
}

function renderStockDesktopTable(rows) {
  return `
    <div class="table-shell desktop-only">
      <table class="store-table stock-table">
        <thead>
          <tr>
            <th>Prodno</th>
            <th>Beskrivelse</th>
            <th>Antall på lager</th>
            <th>Paller på lager</th>
            <th>Paller på vei</th>
            <th>Bestilling på vei</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map((row) => {
              const className = row.stockAmount <= 0 ? "stock-row stock-row-empty" : row.palletsIncoming > 0 ? "stock-row stock-row-incoming" : "stock-row";
              return `
                <tr class="${className}">
                  <td>${row.prodno}</td>
                  <td class="stock-description-cell">${row.description}</td>
                  <td>${row.stockAmountLabel}</td>
                  <td>${row.palletsInStockLabel}</td>
                  <td>${row.palletsIncomingLabel}</td>
                  <td>${renderStockOrderSummary(row)}</td>
                </tr>
              `;
            })
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderStockMobileCards(rows) {
  return `
    <div class="mobile-only stock-mobile-list">
      ${rows
        .map(
          (row) => `
            <article class="mobile-store-card stock-mobile-card ${row.stockAmount <= 0 ? "stock-mobile-empty" : ""}">
              <div class="mobile-store-head">
                <div>
                  <p class="stock-mobile-code">${row.prodno}</p>
                  <h3>${row.description}</h3>
                </div>
                <strong>${row.stockAmountLabel}</strong>
              </div>
              <div class="mobile-store-meta">
                <div><span>Paller på lager</span><strong>${row.palletsInStockLabel}</strong></div>
                <div><span>Paller på vei</span><strong>${row.palletsIncomingLabel}</strong></div>
                <div><span>Antall pr pall</span><strong>${row.unitsPerPalletLabel}</strong></div>
              </div>
              <div class="stock-mobile-orders">
                ${renderStockOrderSummary(row)}
              </div>
            </article>
          `
        )
        .join("")}
    </div>
  `;
}

function renderStockPage(state) {
  return renderStockPageCompact(state);
  const filteredRows = filterStockRows(state);
  const stats = buildStockStats(filteredRows);

  return `
    <main class="page-shell">
      <header class="masthead">
        <div class="masthead-copy">
          <p class="eyebrow">HIBERNIAN BETA</p>
          <h1>Lager med tydeligere søk og innkommende bestillinger</h1>
          <p class="intro">
            Her ser du grossistlageret i en enklere og mer mobilvennlig form, med tydelig søk på produktnummer og beskrivelse,
            og ukevisning på registrerte bestillinger som er på vei inn.
          </p>
        </div>
        <div class="masthead-actions">
          <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
        </div>
      </header>

      ${renderNav(state.page)}

      <section class="status-strip">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
        <p class="status-context">Treff i visningen: <strong>${formatInteger(stats.items)}</strong></p>
      </section>

      <section class="control-panel month-controls">
        <label class="date-picker seller-search">
          <span>Søk i lager</span>
          <input data-role="stock-search" type="search" value="${state.stockQuery}" placeholder="Produktnummer eller beskrivelse..." />
        </label>
        ${renderStockFilterToggle(state)}
      </section>

      <section class="summary-band month-summary-band">
        ${renderStockMetricCard("Artikler", formatInteger(stats.items), "Antall rader i gjeldende visning", "summary-emphasis")}
        ${renderStockMetricCard("Paller på lager", formatInteger(stats.palletsInStock), "Summerte paller i lagerbeholdningen")}
        ${renderStockMetricCard("På vei", formatInteger(stats.incomingItems), "Artikler med registrert bestilling på vei")}
        ${renderStockMetricCard("Tomt lager", formatInteger(stats.emptyItems), "Artikler uten beholdning akkurat nå")}
      </section>

      <section class="content-grid month-layout">
        <div class="content-main">
          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Lageroversikt</p>
              <h2>Beholdning og innkommende bestillinger</h2>
            </div>
            ${filteredRows.length > 0 ? `${renderStockDesktopTable(filteredRows)}${renderStockMobileCards(filteredRows)}` : `<p class="chart-caption">Ingen treff for dette søket eller filteret.</p>`}
          </section>
        </div>

        <aside class="content-side">
          <section class="side-panel">
            <p class="section-label">Forenkling</p>
            <h2>En normalisert lagerfeed</h2>
            <p>
              Betaen leser lageret fra én sammenslått JSON-kilde og normaliserer felt med ulik tegnkoding i frontend.
              Det gjør visningen enklere å vedlikeholde enn dagens doble oppsett.
            </p>
          </section>

          <section class="side-panel">
            <p class="section-label">Nyttig nå</p>
            <ul class="side-list">
              <li>Søk på produktnummer og beskrivelse samtidig</li>
              <li>Filtrer raskt til varer på vei eller tomt lager</li>
              <li>Se uke og antall på bestillinger som er på vei</li>
              <li>Samme side fungerer på både desktop og mobil</li>
            </ul>
          </section>
        </aside>
      </section>
    </main>
  `;
}

function renderStockToolbar(state) {
  return `
    <section class="control-panel week-toolbar stock-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>
      <div class="stock-toolbar-pickers">
        <label class="date-picker seller-search">
          <span>Søk i lager</span>
          <input data-role="stock-search" type="search" value="${state.stockQuery}" placeholder="Produktnummer eller beskrivelse..." />
        </label>
      </div>
      <div class="week-toolbar-footer">
        ${renderStockFilterToggle(state)}
      </div>
    </section>
  `;
}

function renderStockSection(state, filteredRows, stats) {
  return `
    <details class="day-section stock-section" open>
      <summary>
        <div class="day-summary-copy">
          <p class="section-label">Lageroversikt</p>
          <h2>Beholdning og bestillinger</h2>
        </div>
      </summary>
      ${
        filteredRows.length > 0
          ? `
            <div class="stock-stats-grid">
              <article class="stock-stat-card stock-stat-card-primary">
                <span>Artikler</span>
                <strong>${formatInteger(stats.items)}</strong>
              </article>
              <article class="stock-stat-card">
                <span>Paller på lager</span>
                <strong>${formatInteger(stats.palletsInStock)}</strong>
              </article>
              <article class="stock-stat-card">
                <span>På vei</span>
                <strong>${formatInteger(stats.incomingItems)}</strong>
              </article>
              <article class="stock-stat-card">
                <span>Tomt lager</span>
                <strong>${formatInteger(stats.emptyItems)}</strong>
              </article>
            </div>
            ${renderStockDesktopTable(filteredRows)}
            ${renderStockMobileCards(filteredRows)}
          `
          : `<p class="chart-caption stock-empty-state">Ingen treff for dette søket eller filteret.</p>`
      }
    </details>
  `;
}

function renderStockContent(state) {
  const filteredRows = filterStockRows(state);
  const stats = buildStockStats(filteredRows);
  return renderStockSection(state, filteredRows, stats);
}

function renderStockPageCompact(state) {
  return `
    <main class="page-shell">
      ${renderChrome(state, renderStockToolbarClean(state))}

      <section class="content-main stock-layout">
        ${renderStockContent(state)}
      </section>

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderStockToolbarClean(state) {
  return `
    <section class="control-panel week-toolbar stock-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>
      <div class="week-toolbar-pickers stock-toolbar-pickers">
        <label class="date-picker seller-search">
          <span>Søk i lager</span>
          <input data-role="stock-search" type="search" value="${state.stockQuery}" placeholder="Produktnummer eller beskrivelse..." />
        </label>
      </div>
      <div class="week-toolbar-footer">
        ${renderStockFilterToggle(state)}
      </div>
    </section>
  `;
}

function renderPeoplePage(state) {
  return renderPeoplePageCompact(state);
  const dayRanking = buildSellerRanking(state.sellerDayRows, state.sellerMetric);
  const monthRanking = buildSellerRanking(state.sellerMonthRows, state.sellerMetric);
  const yearRanking = buildSellerRanking(state.sellerYearRows, state.sellerMetric);
  const query = state.sellerQuery.trim();

  const filterRows = (rows) => {
    if (!query) {
      return rows.slice(0, 10);
    }
    return rows.filter((row) => sellerMatchesQuery(row.navn, query));
  };

  return `
    <main class="page-shell">
      <header class="masthead">
        <div class="masthead-copy">
          <p class="eyebrow">HIBERNIAN BETA</p>
          <h1>Selgere med topp 10 og levende navnesøk</h1>
          <p class="intro">
            Her ser du toppselgerne for i dag, denne måneden og dette året, med samme plasseringstall selv når du søker fram navn utenfor topp 10.
          </p>
        </div>
        <div class="masthead-actions">
          <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
        </div>
      </header>

      ${renderNav(state.page)}

      <section class="status-strip">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
        <p class="status-context">Måler på: <strong>${state.sellerMetric === "dbValue" ? "DB" : "Omsetning u/moms"}</strong></p>
      </section>

      <section class="control-panel month-controls">
        <label class="date-picker seller-search">
          <span>Søk etter selger</span>
          <input data-role="seller-search" type="search" value="${state.sellerQuery}" placeholder="Begynn å skrive navn..." />
        </label>
        ${renderSellerMetricToggle(state)}
      </section>

      <section class="content-grid seller-grid">
        <div class="content-main seller-columns">
          ${renderSellerList("Dag", formatDateLabel(state.sellerLatestDay), filterRows(dayRanking), state.sellerMetric)}
          ${renderSellerList("Måned", monthLabelFromKey(state.sellerLatestMonthKey), filterRows(monthRanking), state.sellerMetric)}
          ${renderSellerList("År", String(state.sellerLatestYear), filterRows(yearRanking), state.sellerMetric)}
        </div>

        <aside class="content-side">
          <section class="side-panel">
            <p class="section-label">Søk nå</p>
            <h2>Dynamisk filtrering i alle tre perioder</h2>
            <p>
              Så snart du skriver, oppdateres alle listene. Vi beholder original plassering i perioden, så en selger kan vises som for eksempel <strong>#27</strong> selv om topp 10 er skjult av søket.
            </p>
          </section>

          <section class="side-panel">
            <p class="section-label">Det viktigste</p>
            <ul class="side-list">
              <li>Toppliste for dag, måned og år samtidig</li>
              <li>Bytt mellom omsetning u/moms og DB</li>
              <li>Live søk på navn mens du skriver</li>
              <li>Behold rangering også utenfor topp 10</li>
            </ul>
          </section>
        </aside>
      </section>
    </main>
  `;
}

function renderPeoplePageClean(state) {
  const dayRanking = buildSellerRanking(state.sellerDayRows, state.sellerMetric);
  const monthRanking = buildSellerRanking(state.sellerMonthRows, state.sellerMetric);
  const yearRanking = buildSellerRanking(state.sellerYearRows, state.sellerMetric);
  const query = state.sellerQuery.trim();

  const filterRows = (rows) => {
    if (!query) {
      return rows;
    }
    return rows.filter((row) => sellerMatchesQuery(row.navn, query));
  };

  return `
    <main class="page-shell">
      ${renderNav(state.page)}

      <section class="control-panel week-toolbar seller-toolbar">
        <div class="week-toolbar-meta">
          <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
        </div>
        <div class="seller-toolbar-controls">
          <label class="date-picker seller-search">
            <span>Søk etter selger</span>
            <input data-role="seller-search" type="search" value="${state.sellerQuery}" placeholder="Begynn å skrive navn..." />
          </label>
          ${renderSellerMetricToggle(state)}
        </div>
      </section>

      <section class="content-main seller-columns seller-layout">
        ${renderSellerList("Dag", formatDateLabel(state.sellerLatestDay), filterRows(dayRanking), state.sellerMetric, false, query)}
        ${renderSellerList("Måned", monthLabelFromKey(state.sellerLatestMonthKey), filterRows(monthRanking), state.sellerMetric, false, query)}
        ${renderSellerList("År", String(state.sellerLatestYear), filterRows(yearRanking), state.sellerMetric, false, query)}
      </section>

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderPeoplePageCompact(state) {
  const sellerDate = getSellerSelectedDate(state) || String(state.sellerLatestDay);
  return `
    <main class="page-shell">
      ${renderChrome(
        state,
        `
          <section class="status-strip day-status-strip seller-status-strip">
            <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
            <label class="date-picker inline-date-picker seller-date-picker" aria-label="Velg dato">
              <input
                data-role="seller-date-picker"
                type="date"
                min="${formatInputDate(state.dayDates[state.dayDates.length - 1])}"
                max="${formatInputDate(state.dayDates[0])}"
                value="${formatInputDate(sellerDate)}"
              />
            </label>
          </section>
        `
      )}

      <section class="control-panel seller-toolbar">
        <label class="date-picker seller-search">
          <span>Søk etter selger</span>
          <input data-role="seller-search" type="search" value="${state.sellerQuery}" placeholder="Begynn å skrive navn..." />
        </label>
        ${renderSellerMetricToggle(state)}
      </section>

      <section class="content-main seller-columns seller-layout">
        ${renderPeopleCards(state)}
      </section>

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderDaySection(dateKey, rows, expanded = false, modifier = "") {
  const totals = getTotals(rows);
  const detailContent = `${renderDesktopTable(rows)}${renderDayMobileTable(rows)}`;

  return `
    ${renderWeekExpandableSummaryCard(
      `${formatDayHeading(dateKey)}`,
      totals,
      detailContent,
      expanded,
      modifier,
      `data-day-toggle=\"${dateKey}\"`,
      "u/mva",
      totals.umoms,
      [],
      null,
      buildSummaryMetricsHtml(totals)
    )}
  `;
}

function renderDayPage(state) {
  const selectedIndex = state.dayDates.indexOf(state.selectedDate);
  const visibleDates = state.dayDates.slice(selectedIndex, selectedIndex + 3);
  const grossComparison = buildDayMonthComparison(state, state.selectedDate, "gross");
  const dbComparison = buildDayMonthComparison(state, state.selectedDate, "db");
  const grossComparisonExpanded = state.dayComparisonExpanded.includes("gross");
  const dbComparisonExpanded = state.dayComparisonExpanded.includes("db");

  return `
    <main class="page-shell">
      ${renderChrome(
        state,
        `
          <section class="status-strip day-status-strip">
            <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
            <label class="date-picker inline-date-picker" aria-label="Velg dato">
              <input
                data-role="date-picker"
                type="date"
                min="${formatInputDate(state.dayDates[state.dayDates.length - 1])}"
                max="${formatInputDate(state.dayDates[0])}"
                value="${formatInputDate(state.selectedDate)}"
              />
            </label>
          </section>
        `
      )}

      <section class="day-stack">
        ${visibleDates
          .map((date, index) =>
            renderDaySection(
              date,
              state.dayGrouped.get(date) || [],
              state.dayExpandedDates.includes(date),
              [index === 0 ? "summary-emphasis" : "", "day-summary-card"].filter(Boolean).join(" ")
            )
          )
          .join("")}
      </section>

      ${
        grossComparison || dbComparison
          ? `
            <section class="day-comparison-stack">
              ${renderDayMonthComparisonCard(grossComparison, grossComparisonExpanded)}
              ${renderDayMonthComparisonCard(dbComparison, dbComparisonExpanded)}
            </section>
          `
          : ""
      }

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderMonthControls(state) {
  const compareOptions = state.monthOptions.filter((key) => key !== state.selectedMonthKey);

  return `
    <section class="control-panel month-controls">
      <label class="date-picker select-field">
        <span>Vis måned</span>
        <select data-role="selected-month">
          ${state.monthOptions
            .map(
              (key) => `<option value="${key}" ${key === state.selectedMonthKey ? "selected" : ""}>${monthLabelFromKey(key)}</option>`
            )
            .join("")}
        </select>
      </label>

      <label class="date-picker select-field">
        <span>Sammenlign med</span>
        <select data-role="compare-month">
          ${compareOptions
            .map(
              (key) => `<option value="${key}" ${key === state.compareMonthKey ? "selected" : ""}>${monthLabelFromKey(key)}</option>`
            )
            .join("")}
        </select>
      </label>

      <div class="mode-picker">
        <button class="${state.monthMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-mode="full">Full måned</button>
        <button class="${state.monthMode === "mtd" ? "quick-button is-active" : "quick-button"}" type="button" data-mode="mtd">Hittil samme dag</button>
      </div>

      ${
        state.monthMode === "mtd"
          ? `
      <label class="date-picker select-field">
        <span>Til og med dag</span>
        <select data-role="month-cutoff">
          ${Array.from({ length: state.latestAvailableCutoffDay }, (_, index) => index + 1)
            .map(
              (day) => `<option value="${day}" ${day === state.monthCutoffDay ? "selected" : ""}>Dag ${day}</option>`
            )
            .join("")}
        </select>
      </label>
      `
          : ""
      }
    </section>
  `;
}

function renderWeekControls(state) {
  const compareOptions = state.weekOptions.filter((key) => key !== state.selectedWeekKey);

  return `
    <section class="control-panel week-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>

      <div class="week-toolbar-pickers">
        <label class="date-picker select-field">
          <span>Vis uke</span>
          <select data-role="selected-week">
            ${state.weekOptions
              .map((key) => `<option value="${key}" ${key === state.selectedWeekKey ? "selected" : ""}>${formatWeekLabel(key)}</option>`)
              .join("")}
          </select>
        </label>

        <label class="date-picker select-field">
          <span>Sammenlign med</span>
          <select data-role="compare-week">
            ${compareOptions
              .map((key) => `<option value="${key}" ${key === state.compareWeekKey ? "selected" : ""}>${formatWeekLabel(key)}</option>`)
              .join("")}
          </select>
        </label>

        ${
          state.weekMode === "wtd"
            ? `
        <label class="date-picker select-field">
          <span>Til og med ukedag</span>
          <select data-role="week-cutoff">
            ${state.weekCutoffOptions
              .map(
                (item) =>
                  `<option value="${item.isoDay}" ${item.isoDay === state.weekCutoffIsoDay ? "selected" : ""}>${item.label}</option>`
              )
              .join("")}
          </select>
        </label>
        `
            : ""
        }
      </div>

      <div class="week-toolbar-footer">
        <div class="mode-picker">
          <button class="${state.weekMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-week-mode="full">Full uke</button>
          <button class="${state.weekMode === "wtd" ? "quick-button is-active" : "quick-button"}" type="button" data-week-mode="wtd">Hittil samme ukedag</button>
        </div>
      </div>
    </section>
  `;
}

function renderMonthPage(state) {
  return renderMonthPageCompact(state);
  const selectedRows = resolveMonthRows(state, state.selectedMonthKey);
  const compareRows = resolveMonthRows(state, state.compareMonthKey);
  const selectedTotals = getTotals(selectedRows);
  const compareTotals = getTotals(compareRows);
  const diffRows = buildDiffRows(selectedRows, compareRows);
  const cutoffDay = state.monthMode === "mtd" ? state.monthCutoffDay : null;
  const modeLabel = cutoffDay ? `Hittil dag ${cutoffDay} i begge perioder` : "Full måned";

  return `
    <main class="page-shell">
      <header class="masthead">
        <div class="masthead-copy">
          <p class="eyebrow">HIBERNIAN BETA</p>
          <h1>Månedsvisning med ekte sammenligninger</h1>
          <p class="intro">
            Her kan du velge måned fritt, sammenligne mot en annen måned, og bytte mellom full måned
            og samme daggrense i begge perioder med dagens JSON-grunnlag.
          </p>
        </div>
        <div class="masthead-actions">
          <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
        </div>
      </header>

      ${renderNav(state.page)}

      <section class="status-strip">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
        <p class="status-context">Visning: <strong>${modeLabel}</strong></p>
      </section>

      ${renderMonthControls(state)}

      ${
        cutoffDay
          ? `
      <section class="month-mode-note">
        <p>
          Begge perioder summeres til og med dag <strong>${cutoffDay}</strong>.
          Det hindrer at eldre måneder plutselig blir sammenlignet som hele måneder når du egentlig vil se likt utsnitt.
        </p>
      </section>
      `
          : ""
      }

      <section class="summary-band month-summary-band">
        ${renderSummaryCard(formatMonthHeading(state.selectedMonthKey, cutoffDay), selectedTotals, "summary-emphasis")}
        ${renderSummaryCard(formatMonthHeading(state.compareMonthKey, cutoffDay), compareTotals)}
        ${renderDeltaCard(selectedTotals, compareTotals)}
        ${state.selectedMonthKey === state.monthOptions[0] ? renderProjectionCard(state, state.selectedMonthKey) : ""}
      </section>

      <section class="content-grid month-layout">
        <div class="content-main">
          ${renderMonthChartsBlock()}

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Valgt periode</p>
              <h2>${formatMonthHeading(state.selectedMonthKey, cutoffDay)}</h2>
            </div>
            ${renderDesktopTable(selectedRows)}
            ${renderMobileCards(selectedRows)}
          </section>

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Sammenligningsperiode</p>
              <h2>${formatMonthHeading(state.compareMonthKey, cutoffDay)}</h2>
            </div>
            ${renderDesktopTable(compareRows)}
            ${renderMobileCards(compareRows)}
          </section>

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Differanse per butikk</p>
              <h2>${formatMonthHeading(state.selectedMonthKey, cutoffDay)} mot ${formatMonthHeading(state.compareMonthKey, cutoffDay)}</h2>
            </div>
            ${renderDiffTable(diffRows)}
          </section>
        </div>

        <aside class="content-side">
          <section class="side-panel">
            <p class="section-label">Hva vi bruker nå</p>
            <h2>Bygget direkte på dagens JSON</h2>
            <p>
              Hele månedsvisningen regnes direkte fra dagsfilen. Prognosekortet bruker fortsatt en egen sammenligningsfil,
              men tabeller og grafer er ikke lenger avhengige av egne månedsfiler.
            </p>
          </section>

          <section class="side-panel">
            <p class="section-label">Nyttig nå</p>
            <ul class="side-list">
              <li>Samme måned i fjor</li>
              <li>Forrige måned</li>
              <li>Valgfri måned mot valgfri måned</li>
              <li>Lik daggrense i begge perioder</li>
            </ul>
          </section>
        </aside>
      </section>
    </main>
  `;
}

function renderMonthToolbar(state) {
  const compareOptions = state.monthOptions.filter((key) => key !== state.selectedMonthKey);

  return `
    <section class="control-panel week-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>

      <div class="week-toolbar-pickers">
        <label class="date-picker select-field">
          <span>Vis måned</span>
          <select data-role="selected-month">
            ${state.monthOptions
              .map(
                (key) => `<option value="${key}" ${key === state.selectedMonthKey ? "selected" : ""}>${monthLabelFromKey(key)}</option>`
              )
              .join("")}
          </select>
        </label>

        <label class="date-picker select-field">
          <span>Sammenlign med</span>
          <select data-role="compare-month">
            ${compareOptions
              .map(
                (key) => `<option value="${key}" ${key === state.compareMonthKey ? "selected" : ""}>${monthLabelFromKey(key)}</option>`
              )
              .join("")}
          </select>
        </label>

        ${
          state.monthMode === "mtd"
            ? `
        <label class="date-picker select-field">
          <span>Til og med dag</span>
          <select data-role="month-cutoff">
            ${Array.from({ length: state.latestAvailableCutoffDay }, (_, index) => index + 1)
              .map(
                (day) => `<option value="${day}" ${day === state.monthCutoffDay ? "selected" : ""}>Dag ${day}</option>`
              )
              .join("")}
          </select>
        </label>
        `
            : ""
        }
      </div>

      <div class="week-toolbar-footer">
        <div class="mode-picker">
          <button class="${state.monthMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-mode="full">Full måned</button>
          <button class="${state.monthMode === "mtd" ? "quick-button is-active" : "quick-button"}" type="button" data-mode="mtd">Hittil samme dag</button>
        </div>
      </div>
    </section>
  `;
}

function renderMonthPageCompact(state) {
  const selectedRows = resolveMonthRows(state, state.selectedMonthKey);
  const compareRows = resolveMonthRows(state, state.compareMonthKey);
  const selectedTotals = getTotals(selectedRows);
  const compareTotals = getTotals(compareRows);
  const diffRows = buildDiffRows(selectedRows, compareRows);
  const cutoffDay = state.monthMode === "mtd" ? state.monthCutoffDay : null;
  const grossComparison = buildMonthComparison(state, "gross");
  const dbComparison = buildMonthComparison(state, "db");
  const grossComparisonExpanded = state.monthComparisonExpanded.includes("gross");
  const dbComparisonExpanded = state.monthComparisonExpanded.includes("db");
  const selectedExpanded = state.monthSummaryExpanded.includes("selected");
  const compareExpanded = state.monthSummaryExpanded.includes("compare");
  const diffExpanded = state.monthSummaryExpanded.includes("diff");

  return `
    <main class="page-shell">
      ${renderChrome(state, renderMonthToolbarClean(state))}

      <section class="summary-band week-summary-band">
        ${renderWeekExpandableSummaryCard(
          formatMonthHeading(state.selectedMonthKey, cutoffDay),
          selectedTotals,
          `${renderDesktopTable(selectedRows)}${renderDayMobileTable(selectedRows)}`,
          selectedExpanded,
          "summary-emphasis",
          'data-month-panels-toggle="selected"',
          "u/mva",
          selectedTotals.umoms,
          [],
          null,
          buildSummaryMetricsHtml(selectedTotals)
        )}
        ${renderWeekExpandableSummaryCard(
          formatMonthHeading(state.compareMonthKey, cutoffDay),
          compareTotals,
          `${renderDesktopTable(compareRows)}${renderDayMobileTable(compareRows)}`,
          compareExpanded,
          "",
          'data-month-panels-toggle="compare"',
          "u/mva",
          compareTotals.umoms,
          [],
          null,
          buildSummaryMetricsHtml(compareTotals)
        )}
        ${renderWeekExpandableDeltaCard(
          selectedTotals,
          compareTotals,
          renderDiffTable(diffRows),
          diffExpanded,
          'data-month-panels-toggle="diff"'
        )}
      </section>

      <section class="content-main week-layout">
        ${renderMonthChartsBlock()}
      </section>

      <section class="day-comparison-stack">
        ${renderPeriodComparisonCard(grossComparison, grossComparisonExpanded)}
        ${renderPeriodComparisonCard(dbComparison, dbComparisonExpanded)}
      </section>

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderMonthToolbarClean(state) {
  const compareOptions = state.monthOptions.filter((key) => key !== state.selectedMonthKey);

  return `
    <section class="control-panel week-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>

      <div class="week-toolbar-pickers">
        <label class="date-picker select-field">
          <span>Vis måned</span>
          <select data-role="selected-month">
            ${state.monthOptions
              .map(
                (key) => `<option value="${key}" ${key === state.selectedMonthKey ? "selected" : ""}>${monthLabelFromKey(key)}</option>`
              )
              .join("")}
          </select>
        </label>

        <label class="date-picker select-field">
          <span>Sammenlign med</span>
          <select data-role="compare-month">
            ${compareOptions
              .map(
                (key) => `<option value="${key}" ${key === state.compareMonthKey ? "selected" : ""}>${monthLabelFromKey(key)}</option>`
              )
              .join("")}
          </select>
        </label>

        ${
          state.monthMode === "mtd"
            ? `
        <label class="date-picker select-field">
          <span>Til og med dag</span>
          <select data-role="month-cutoff">
            ${Array.from({ length: state.latestAvailableCutoffDay }, (_, index) => index + 1)
              .map((day) => `<option value="${day}" ${day === state.monthCutoffDay ? "selected" : ""}>Dag ${day}</option>`)
              .join("")}
          </select>
        </label>
        `
            : ""
        }
      </div>

      <div class="week-toolbar-footer">
        <div class="mode-picker">
          <button class="${state.monthMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-mode="full">Full måned</button>
          <button class="${state.monthMode === "mtd" ? "quick-button is-active" : "quick-button"}" type="button" data-mode="mtd">Hittil samme dag</button>
        </div>
      </div>
    </section>
  `;
}

function renderWeekPage(state) {
  return renderWeekPageCompact(state);
  const selectedRows = resolveWeekRows(state, state.selectedWeekKey);
  const compareRows = resolveWeekRows(state, state.compareWeekKey);
  const selectedTotals = getTotals(selectedRows);
  const compareTotals = getTotals(compareRows);
  const diffRows = buildDiffRows(selectedRows, compareRows);
  const cutoffIsoDay = state.weekMode === "wtd" ? state.weekCutoffIsoDay : null;
  const cutoffLabel = cutoffIsoDay
    ? state.weekCutoffOptions.find((item) => item.isoDay === cutoffIsoDay)?.label || ""
    : "";
  const modeLabel = cutoffIsoDay ? `Hittil samme ukedag, til og med ${cutoffLabel}` : "Full uke";

  return `
    <main class="page-shell">
      <header class="masthead">
        <div class="masthead-copy">
          <p class="eyebrow">HIBERNIAN BETA</p>
          <h1>Ukesvisning med samme logikk som måned og år</h1>
          <p class="intro">
            Her kan du velge uke fritt, sammenligne mot en annen uke, og bytte mellom full uke
            og samme ukedag i begge perioder med dagens dagsdata som grunnlag.
          </p>
        </div>
        <div class="masthead-actions">
          <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
        </div>
      </header>

      ${renderNav(state.page)}

      <section class="status-strip">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
        <p class="status-context">Visning: <strong>${modeLabel}</strong></p>
      </section>

      ${renderWeekControls(state)}

      ${
        cutoffIsoDay
          ? `
      <section class="month-mode-note">
        <p>
          Begge ukene summeres til og med <strong>${state.weekCutoffOptions.find((item) => item.isoDay === cutoffIsoDay)?.label || ""}</strong>.
          Det gjør sammenligningen rettferdig når inneværende uke ikke er ferdig.
        </p>
      </section>
      `
          : ""
      }

      <section class="summary-band">
        ${renderSummaryCard(formatWeekHeading(state.selectedWeekKey, cutoffIsoDay), selectedTotals, "summary-emphasis")}
        ${renderSummaryCard(formatWeekHeading(state.compareWeekKey, cutoffIsoDay), compareTotals)}
        ${renderDeltaCard(selectedTotals, compareTotals)}
      </section>

      <section class="content-grid month-layout">
        <div class="content-main">
          ${renderWeekChartsBlock()}

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Valgt uke</p>
              <h2>${formatWeekHeading(state.selectedWeekKey, cutoffIsoDay)}</h2>
            </div>
            ${renderDesktopTable(selectedRows)}
            ${renderMobileCards(selectedRows)}
          </section>

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Sammenligningsuke</p>
              <h2>${formatWeekHeading(state.compareWeekKey, cutoffIsoDay)}</h2>
            </div>
            ${renderDesktopTable(compareRows)}
            ${renderMobileCards(compareRows)}
          </section>

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Differanse per butikk</p>
              <h2>${formatWeekHeading(state.selectedWeekKey, cutoffIsoDay)} mot ${formatWeekHeading(state.compareWeekKey, cutoffIsoDay)}</h2>
            </div>
            ${renderDiffTable(diffRows)}
          </section>
        </div>

        <aside class="content-side">
          <section class="side-panel">
            <p class="section-label">Hva vi bruker nå</p>
            <h2>Bygget direkte på dagsdata</h2>
            <p>
              Ukevisningen regnes direkte fra tilgjengelige dagsrader. Det gir oss fleksibel uke mot uke-sammenligning
              uten å vente på egne ukesfiler.
            </p>
          </section>

          <section class="side-panel">
            <p class="section-label">Nyttig nå</p>
            <ul class="side-list">
              <li>Valgfri uke mot valgfri uke</li>
              <li>Samme uke i fjor</li>
              <li>Forrige uke</li>
              <li>Lik ukedag i begge uker</li>
            </ul>
          </section>
        </aside>
      </section>
    </main>
  `;
}

function renderWeekPageCompact(state) {
  const selectedRows = resolveWeekRows(state, state.selectedWeekKey);
  const compareRows = resolveWeekRows(state, state.compareWeekKey);
  const selectedTotals = getTotals(selectedRows);
  const compareTotals = getTotals(compareRows);
  const diffRows = buildDiffRows(selectedRows, compareRows);
  const cutoffIsoDay = state.weekMode === "wtd" ? state.weekCutoffIsoDay : null;
  const grossComparison = buildWeekComparison(state, "gross");
  const dbComparison = buildWeekComparison(state, "db");
  const grossComparisonExpanded = state.weekComparisonExpanded.includes("gross");
  const dbComparisonExpanded = state.weekComparisonExpanded.includes("db");
  const selectedExpanded = state.weekSummaryExpanded.includes("selected");
  const compareExpanded = state.weekSummaryExpanded.includes("compare");
  const diffExpanded = state.weekSummaryExpanded.includes("diff");

  return `
    <main class="page-shell">
      ${renderChrome(state, renderWeekControls(state))}

      <section class="summary-band week-summary-band">
        ${renderWeekExpandableSummaryCard(
          formatWeekHeading(state.selectedWeekKey, cutoffIsoDay),
          selectedTotals,
          `${renderDesktopTable(selectedRows)}${renderDayMobileTable(selectedRows)}`,
          selectedExpanded,
          "summary-emphasis",
          'data-week-panels-toggle="selected"',
          "u/mva",
          selectedTotals.umoms,
          [],
          null,
          buildSummaryMetricsHtml(selectedTotals)
        )}
        ${renderWeekExpandableSummaryCard(
          formatWeekHeading(state.compareWeekKey, cutoffIsoDay),
          compareTotals,
          `${renderDesktopTable(compareRows)}${renderDayMobileTable(compareRows)}`,
          compareExpanded,
          "",
          'data-week-panels-toggle="compare"',
          "u/mva",
          compareTotals.umoms,
          [],
          null,
          buildSummaryMetricsHtml(compareTotals)
        )}
        ${renderWeekExpandableDeltaCard(
          selectedTotals,
          compareTotals,
          renderDiffTable(diffRows),
          diffExpanded,
          'data-week-panels-toggle="diff"'
        )}
      </section>

      <section class="content-main week-layout">
        ${renderWeekChartsBlock()}
      </section>

      <section class="day-comparison-stack">
        ${renderPeriodComparisonCard(grossComparison, grossComparisonExpanded)}
        ${renderPeriodComparisonCard(dbComparison, dbComparisonExpanded)}
      </section>

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderYearControls(state) {
  const compareOptions = state.yearOptions.filter((year) => year !== state.selectedYear);

  return `
    <section class="control-panel month-controls">
      <label class="date-picker select-field">
        <span>Vis år</span>
        <select data-role="selected-year">
          ${state.yearOptions
            .map((year) => `<option value="${year}" ${year === state.selectedYear ? "selected" : ""}>${year}</option>`)
            .join("")}
        </select>
      </label>

      <label class="date-picker select-field">
        <span>Sammenlign med</span>
        <select data-role="compare-year">
          ${compareOptions
            .map((year) => `<option value="${year}" ${year === state.compareYear ? "selected" : ""}>${year}</option>`)
            .join("")}
        </select>
      </label>

      <div class="mode-picker">
        <button class="${state.yearMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-year-mode="full">Fullt år</button>
        <button class="${state.yearMode === "ytd" ? "quick-button is-active" : "quick-button"}" type="button" data-year-mode="ytd">Hittil samme dato</button>
      </div>

      ${
        state.yearMode === "ytd"
          ? `
      <label class="date-picker select-field">
        <span>Til og med dato</span>
        <select data-role="year-cutoff">
          ${state.yearCutoffOptions
            .map(
              (monthDay) =>
                `<option value="${monthDay}" ${monthDay === state.yearCutoffMonthDay ? "selected" : ""}>${formatMonthDayLabel(monthDay)}</option>`
            )
            .join("")}
        </select>
      </label>
      `
          : ""
      }
    </section>
  `;
}

function renderYearPage(state) {
  return renderYearPageCompact(state);
  const selectedRows = resolveYearRows(state, state.selectedYear);
  const compareRows = resolveYearRows(state, state.compareYear);
  const selectedTotals = getTotals(selectedRows);
  const compareTotals = getTotals(compareRows);
  const diffRows = buildDiffRows(selectedRows, compareRows);
  const cutoffMonthDay = state.yearMode === "ytd" ? state.yearCutoffMonthDay : null;
  const modeLabel = cutoffMonthDay ? `Hittil ${formatMonthDayLabel(cutoffMonthDay)} i begge år` : "Fullt år";

  return `
    <main class="page-shell">
      <header class="masthead">
        <div class="masthead-copy">
          <p class="eyebrow">HIBERNIAN BETA</p>
          <h1>Årsvisning med samme rytme som måned</h1>
          <p class="intro">
            Her kan du sammenligne år mot år, enten som fullt år eller som samme dato i begge år,
            slik at årsvisningen blir like fleksibel og tydelig som månedsvisningen.
          </p>
        </div>
        <div class="masthead-actions">
          <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
        </div>
      </header>

      ${renderNav(state.page)}

      <section class="status-strip">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
        <p class="status-context">Visning: <strong>${modeLabel}</strong></p>
      </section>

      ${renderYearControls(state)}

      ${
        cutoffMonthDay
          ? `
      <section class="month-mode-note">
        <p>
          Begge år summeres til og med dato <strong>${formatMonthDayLabel(cutoffMonthDay)}</strong>.
          Det gjør at du sammenligner lik del av året, ikke en uferdig periode mot et helt år.
        </p>
      </section>
      `
          : ""
      }

      <section class="summary-band">
        ${renderSummaryCard(formatYearHeading(state.selectedYear, cutoffMonthDay), selectedTotals, "summary-emphasis")}
        ${renderSummaryCard(formatYearHeading(state.compareYear, cutoffMonthDay), compareTotals)}
        ${renderDeltaCard(selectedTotals, compareTotals)}
      </section>

      <section class="content-grid month-layout">
        <div class="content-main">
          ${renderYearChartsBlock()}

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Valgt år</p>
              <h2>${formatYearHeading(state.selectedYear, cutoffMonthDay)}</h2>
            </div>
            ${renderDesktopTable(selectedRows)}
            ${renderMobileCards(selectedRows)}
          </section>

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Sammenligningsår</p>
              <h2>${formatYearHeading(state.compareYear, cutoffMonthDay)}</h2>
            </div>
            ${renderDesktopTable(compareRows)}
            ${renderMobileCards(compareRows)}
          </section>

          <section class="month-block">
            <div class="history-head">
              <p class="section-label">Differanse per butikk</p>
              <h2>${formatYearHeading(state.selectedYear, cutoffMonthDay)} mot ${formatYearHeading(state.compareYear, cutoffMonthDay)}</h2>
            </div>
            ${renderDiffTable(diffRows)}
          </section>
        </div>

        <aside class="content-side">
          <section class="side-panel">
            <p class="section-label">Hva vi bruker nå</p>
            <h2>Bygget direkte på dagsdata</h2>
            <p>
              Både fullt år og hittil samme dato regnes direkte fra dagsdata,
              slik at årsvisningen slipper avhengighet til egne årsfiler.
            </p>
          </section>

          <section class="side-panel">
            <p class="section-label">Nyttig nå</p>
            <ul class="side-list">
              <li>Nåværende år mot fjoråret</li>
              <li>Valgfritt år mot valgfritt år</li>
              <li>Lik cutoff-dato i begge år</li>
              <li>Samme butikkrekkefølge som ellers i appen</li>
            </ul>
          </section>
        </aside>
      </section>
    </main>
  `;
}

function renderYearToolbar(state) {
  const compareOptions = state.yearOptions.filter((year) => year !== state.selectedYear);

  return `
    <section class="control-panel week-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>

      <div class="week-toolbar-pickers">
        <label class="date-picker select-field">
          <span>Vis år</span>
          <select data-role="selected-year">
            ${state.yearOptions
              .map((year) => `<option value="${year}" ${year === state.selectedYear ? "selected" : ""}>${year}</option>`)
              .join("")}
          </select>
        </label>

        <label class="date-picker select-field">
          <span>Sammenlign med</span>
          <select data-role="compare-year">
            ${compareOptions
              .map((year) => `<option value="${year}" ${year === state.compareYear ? "selected" : ""}>${year}</option>`)
              .join("")}
          </select>
        </label>

        ${
          state.yearMode === "ytd"
            ? `
        <label class="date-picker select-field">
          <span>Til og med dato</span>
          <select data-role="year-cutoff">
            ${state.yearCutoffOptions
              .map(
                (monthDay) =>
                  `<option value="${monthDay}" ${monthDay === state.yearCutoffMonthDay ? "selected" : ""}>${formatMonthDayLabel(monthDay)}</option>`
              )
              .join("")}
          </select>
        </label>
        `
            : ""
        }
      </div>

      <div class="week-toolbar-footer">
        <div class="mode-picker">
          <button class="${state.yearMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-year-mode="full">Fullt år</button>
          <button class="${state.yearMode === "ytd" ? "quick-button is-active" : "quick-button"}" type="button" data-year-mode="ytd">Hittil samme dato</button>
        </div>
      </div>
    </section>
  `;
}

function renderYearPageCompact(state) {
  const selectedRows = resolveYearRows(state, state.selectedYear);
  const compareRows = resolveYearRows(state, state.compareYear);
  const selectedTotals = getTotals(selectedRows);
  const compareTotals = getTotals(compareRows);
  const diffRows = buildDiffRows(selectedRows, compareRows);
  const cutoffMonthDay = state.yearMode === "ytd" ? state.yearCutoffMonthDay : null;
  const selectedExpanded = state.yearSummaryExpanded.includes("selected");
  const compareExpanded = state.yearSummaryExpanded.includes("compare");
  const diffExpanded = state.yearSummaryExpanded.includes("diff");

  return `
    <main class="page-shell">
      ${renderChrome(state, renderYearToolbarClean(state))}

      <section class="summary-band week-summary-band">
        ${renderWeekExpandableSummaryCard(
          formatYearHeading(state.selectedYear, cutoffMonthDay),
          selectedTotals,
          `${renderDesktopTable(selectedRows)}${renderDayMobileTable(selectedRows)}`,
          selectedExpanded,
          "summary-emphasis",
          'data-year-panels-toggle="selected"',
          "u/mva",
          selectedTotals.umoms,
          [],
          null,
          buildSummaryMetricsHtml(selectedTotals)
        )}
        ${renderWeekExpandableSummaryCard(
          formatYearHeading(state.compareYear, cutoffMonthDay),
          compareTotals,
          `${renderDesktopTable(compareRows)}${renderDayMobileTable(compareRows)}`,
          compareExpanded,
          "",
          'data-year-panels-toggle="compare"',
          "u/mva",
          compareTotals.umoms,
          [],
          null,
          buildSummaryMetricsHtml(compareTotals)
        )}
        ${renderWeekExpandableDeltaCard(
          selectedTotals,
          compareTotals,
          renderDiffTable(diffRows),
          diffExpanded,
          'data-year-panels-toggle="diff"'
        )}
      </section>

      <section class="content-main week-layout">
        ${renderYearChartsBlock()}
      </section>

      <section class="day-page-footer">
        <button class="button button-secondary" type="button" data-action="classic">Bytt til klassisk</button>
      </section>
    </main>
  `;
}

function renderYearToolbarClean(state) {
  const compareOptions = state.yearOptions.filter((year) => year !== state.selectedYear);

  return `
    <section class="control-panel week-toolbar">
      <div class="week-toolbar-meta">
        <p class="updated-line">Oppdatert sist: <strong>${state.updatedAt || "ukjent"}</strong></p>
      </div>

      <div class="week-toolbar-pickers">
        <label class="date-picker select-field">
          <span>Vis år</span>
          <select data-role="selected-year">
            ${state.yearOptions
              .map((year) => `<option value="${year}" ${year === state.selectedYear ? "selected" : ""}>${year}</option>`)
              .join("")}
          </select>
        </label>

        <label class="date-picker select-field">
          <span>Sammenlign med</span>
          <select data-role="compare-year">
            ${compareOptions
              .map((year) => `<option value="${year}" ${year === state.compareYear ? "selected" : ""}>${year}</option>`)
              .join("")}
          </select>
        </label>

        ${
          state.yearMode === "ytd"
            ? `
        <label class="date-picker select-field">
          <span>Til og med dato</span>
          <select data-role="year-cutoff">
            ${state.yearCutoffOptions
              .map(
                (monthDay) =>
                  `<option value="${monthDay}" ${monthDay === state.yearCutoffMonthDay ? "selected" : ""}>${formatMonthDayLabel(monthDay)}</option>`
              )
              .join("")}
          </select>
        </label>
        `
            : ""
        }
      </div>

      <div class="week-toolbar-footer">
        <div class="mode-picker">
          <button class="${state.yearMode === "full" ? "quick-button is-active" : "quick-button"}" type="button" data-year-mode="full">Fullt år</button>
          <button class="${state.yearMode === "ytd" ? "quick-button is-active" : "quick-button"}" type="button" data-year-mode="ytd">Hittil samme dato</button>
        </div>
      </div>
    </section>
  `;
}

function buildStaticChartOptions(overrides = {}) {
  const isMobile = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(max-width: 860px)").matches;
  return {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: overrides.aspectRatio ?? (isMobile ? 1.08 : 2.2),
    animation: false,
    events: [],
    layout: {
      padding: isMobile
        ? { top: 2, right: 2, bottom: 0, left: 0 }
        : { top: 8, right: 8, bottom: 0, left: 0 },
      ...(overrides.layout || {}),
    },
    plugins: {
      legend: {
        position: "top",
        labels: {
          boxWidth: isMobile ? 14 : 18,
          boxHeight: isMobile ? 8 : 10,
          font: { size: isMobile ? 11 : 12 },
        },
      },
      tooltip: { enabled: false },
      ...(overrides.plugins || {}),
    },
    ...overrides,
  };
}

function initMonthCharts(state) {
  if (!window.Chart) {
    return;
  }

  const cumulativeCanvas = document.getElementById("month-cumulative-chart");
  const storeCanvas = document.getElementById("month-store-chart");
  if (!cumulativeCanvas || !storeCanvas) {
    return;
  }

  const cutoffDay = state.monthMode === "mtd" ? state.monthCutoffDay : null;
  const selectedSeries = buildMonthSeries(state, state.selectedMonthKey, cutoffDay);
  const compareSeries = buildMonthSeries(state, state.compareMonthKey, cutoffDay);
  const labels = Array.from(new Set([...selectedSeries.labels, ...compareSeries.labels])).sort(
    (left, right) => Number(left) - Number(right)
  );
  const selectedCumulativeMap = new Map(selectedSeries.labels.map((label, index) => [label, selectedSeries.cumulative[index]]));
  const compareCumulativeMap = new Map(compareSeries.labels.map((label, index) => [label, compareSeries.cumulative[index]]));
  const cumulativeDatasets = sortDatasetsByYear([
    {
      label: monthLabelFromKey(state.selectedMonthKey),
      data: labels.map((label) => selectedCumulativeMap.get(label) ?? null),
      borderColor: "#0f766e",
      backgroundColor: "rgba(15, 118, 110, 0.14)",
      tension: 0.28,
      fill: true,
    },
    {
      label: monthLabelFromKey(state.compareMonthKey),
      data: labels.map((label) => compareCumulativeMap.get(label) ?? null),
      borderColor: "#b48b34",
      backgroundColor: "rgba(180, 139, 52, 0.08)",
      tension: 0.28,
      fill: true,
    },
  ]);

  const cumulativeChart = new window.Chart(cumulativeCanvas, {
    type: "line",
    data: {
      labels,
      datasets: cumulativeDatasets,
    },
    options: buildStaticChartOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1000000,
            maxTicksLimit: 6,
            callback: formatAxisMillions,
          },
        },
      },
    }),
  });
  registerVisual("chartjs", cumulativeChart);

  const selectedRows = getStoreRows(resolveMonthRows(state, state.selectedMonthKey));
  const compareRows = getStoreRows(resolveMonthRows(state, state.compareMonthKey));
  const compareMap = new Map(compareRows.map((row) => [row.butikk, row]));
  const storeDatasets = sortDatasetsByYear([
    {
      label: monthLabelFromKey(state.selectedMonthKey),
      data: selectedRows.map((row) => row.gross),
      backgroundColor: "rgba(15, 118, 110, 0.82)",
      borderRadius: 10,
    },
    {
      label: monthLabelFromKey(state.compareMonthKey),
      data: selectedRows.map((row) => (compareMap.get(row.butikk) ? compareMap.get(row.butikk).gross : 0)),
      backgroundColor: "rgba(180, 139, 52, 0.75)",
      borderRadius: 10,
    },
  ]);
  const storeChart = new window.Chart(storeCanvas, {
    type: "bar",
    data: {
      labels: selectedRows.map((row) => row.butikk),
      datasets: storeDatasets,
    },
    options: buildStaticChartOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1000000,
            maxTicksLimit: 6,
            callback: formatAxisMillions,
          },
        },
      },
    }),
  });
  registerVisual("chartjs", storeChart);
}

function initWeekCharts(state) {
  if (!window.Chart) {
    return;
  }

  const cumulativeCanvas = document.getElementById("week-cumulative-chart");
  const storeCanvas = document.getElementById("week-store-chart");
  if (!cumulativeCanvas || !storeCanvas) {
    return;
  }

  const cutoffIsoDay = state.weekMode === "wtd" ? state.weekCutoffIsoDay : null;
  const selectedSeries = buildWeekSeries(state, state.selectedWeekKey, cutoffIsoDay);
  const compareSeries = buildWeekSeries(state, state.compareWeekKey, cutoffIsoDay);
  const labels = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"].filter(
    (label) => selectedSeries.labels.includes(label) || compareSeries.labels.includes(label)
  );
  const selectedMap = new Map(selectedSeries.labels.map((label, index) => [label, selectedSeries.cumulative[index]]));
  const compareMap = new Map(compareSeries.labels.map((label, index) => [label, compareSeries.cumulative[index]]));
  const cumulativeDatasets = sortDatasetsByYear([
    {
      label: formatWeekLabel(state.selectedWeekKey),
      data: labels.map((label) => selectedMap.get(label) ?? null),
      borderColor: "#0f766e",
      backgroundColor: "rgba(15, 118, 110, 0.14)",
      tension: 0.28,
      fill: true,
    },
    {
      label: formatWeekLabel(state.compareWeekKey),
      data: labels.map((label) => compareMap.get(label) ?? null),
      borderColor: "#b48b34",
      backgroundColor: "rgba(180, 139, 52, 0.08)",
      tension: 0.28,
      fill: true,
    },
  ]);

  const cumulativeChart = new window.Chart(cumulativeCanvas, {
    type: "line",
    data: {
      labels,
      datasets: cumulativeDatasets,
    },
    options: buildStaticChartOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1000000,
            maxTicksLimit: 6,
            callback: formatAxisMillions,
          },
        },
      },
    }),
  });
  registerVisual("chartjs", cumulativeChart);

  const selectedRows = getStoreRows(resolveWeekRows(state, state.selectedWeekKey));
  const compareRows = getStoreRows(resolveWeekRows(state, state.compareWeekKey));
  const compareStoreMap = new Map(compareRows.map((row) => [row.butikk, row]));
  const storeDatasets = sortDatasetsByYear([
    {
      label: formatWeekLabel(state.selectedWeekKey),
      data: selectedRows.map((row) => row.gross),
      backgroundColor: "rgba(15, 118, 110, 0.82)",
      borderRadius: 10,
    },
    {
      label: formatWeekLabel(state.compareWeekKey),
      data: selectedRows.map((row) => (compareStoreMap.get(row.butikk) ? compareStoreMap.get(row.butikk).gross : 0)),
      backgroundColor: "rgba(180, 139, 52, 0.75)",
      borderRadius: 10,
    },
  ]);
  const storeChart = new window.Chart(storeCanvas, {
    type: "bar",
    data: {
      labels: selectedRows.map((row) => row.butikk),
      datasets: storeDatasets,
    },
    options: buildStaticChartOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1000000,
            maxTicksLimit: 6,
            callback: formatAxisMillions,
          },
        },
      },
    }),
  });
  registerVisual("chartjs", storeChart);
}

function initYearCharts(state) {
  if (!window.Chart) {
    return;
  }

  const cumulativeCanvas = document.getElementById("year-cumulative-chart");
  const storeCanvas = document.getElementById("year-store-chart");
  if (!cumulativeCanvas || !storeCanvas) {
    return;
  }

  const selectedSeries = buildYearMonthSeries(state, state.selectedYear);
  const compareSeries = buildYearMonthSeries(state, state.compareYear);
  const cumulativeDatasets = sortDatasetsByYear([
    {
      label: String(state.selectedYear),
      data: selectedSeries.cumulative,
      borderColor: "#0f766e",
      backgroundColor: "rgba(15, 118, 110, 0.14)",
      tension: 0.28,
      fill: true,
    },
    {
      label: String(state.compareYear),
      data: compareSeries.cumulative,
      borderColor: "#b48b34",
      backgroundColor: "rgba(180, 139, 52, 0.08)",
      tension: 0.28,
      fill: true,
    },
  ]);

  const cumulativeChart = new window.Chart(cumulativeCanvas, {
    type: "line",
    data: {
      labels: selectedSeries.labels,
      datasets: cumulativeDatasets,
    },
    options: buildStaticChartOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1000000,
            maxTicksLimit: 6,
            callback: formatAxisMillions,
          },
        },
      },
    }),
  });
  registerVisual("chartjs", cumulativeChart);

  const selectedRows = getStoreRows(resolveYearRows(state, state.selectedYear));
  const compareRows = getStoreRows(resolveYearRows(state, state.compareYear));
  const compareMap = new Map(compareRows.map((row) => [row.butikk, row]));
  const storeDatasets = sortDatasetsByYear([
    {
      label: String(state.selectedYear),
      data: selectedRows.map((row) => row.gross),
      backgroundColor: "rgba(15, 118, 110, 0.82)",
      borderRadius: 10,
    },
    {
      label: String(state.compareYear),
      data: selectedRows.map((row) => (compareMap.get(row.butikk) ? compareMap.get(row.butikk).gross : 0)),
      backgroundColor: "rgba(180, 139, 52, 0.75)",
      borderRadius: 10,
    },
  ]);

  const storeChart = new window.Chart(storeCanvas, {
    type: "bar",
    data: {
      labels: selectedRows.map((row) => row.butikk),
      datasets: storeDatasets,
    },
    options: buildStaticChartOptions({
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1000000,
            maxTicksLimit: 6,
            callback: formatAxisMillions,
          },
        },
      },
    }),
  });
  registerVisual("chartjs", storeChart);
}

function initVisuals(state) {
  if (state.page === "week") {
    initWeekCharts(state);
  }
  if (state.page === "month") {
    initMonthCharts(state);
  }
  if (state.page === "year") {
    initYearCharts(state);
  }
}

function syncUrl(state) {
  const url = new URL(window.location.href);
  url.searchParams.set("ui", "beta");
  if (state.page === "day") {
    url.searchParams.delete("page");
  } else {
    url.searchParams.set("page", state.page);
  }
  if (state.page === "people" && state.sellerSelectedDate) {
    url.searchParams.set("sellerDate", formatInputDate(state.sellerSelectedDate));
  } else {
    url.searchParams.delete("sellerDate");
  }
  window.history.replaceState({}, "", url);
}

function captureViewState() {
  const activeElement = document.activeElement;
  const role = activeElement?.getAttribute?.("data-role");

  return {
    role,
    selectionStart: typeof activeElement?.selectionStart === "number" ? activeElement.selectionStart : null,
    selectionEnd: typeof activeElement?.selectionEnd === "number" ? activeElement.selectionEnd : null,
    scrollX: window.scrollX,
    scrollY: window.scrollY,
  };
}

function restoreViewState(viewState) {
  if (!viewState) {
    return;
  }

  window.scrollTo(viewState.scrollX, viewState.scrollY);

  if (!viewState.role) {
    return;
  }

  const element = document.querySelector(`[data-role='${viewState.role}']`);
  if (!element) {
    return;
  }

  element.focus({ preventScroll: true });
  if (typeof element.setSelectionRange === "function" && viewState.selectionStart !== null && viewState.selectionEnd !== null) {
    element.setSelectionRange(viewState.selectionStart, viewState.selectionEnd);
  }
}

function repaintPreservingViewport(state) {
  paint(state, captureViewState());
}

function refreshSellerResults(state) {
  const sellerLayout = document.querySelector(".seller-layout");
  if (!sellerLayout) {
    paint(state);
    return;
  }
  sellerLayout.innerHTML = renderPeopleCards(state);
}

function refreshStockResults(state) {
  const stockLayout = document.querySelector(".stock-layout");
  if (!stockLayout) {
    paint(state);
    return;
  }
  stockLayout.innerHTML = renderStockContent(state);
}

function bindEvents(state) {
  document.querySelectorAll("[data-action='classic']").forEach((button) => {
    button.addEventListener("click", goClassic);
  });

  document.querySelectorAll("[data-page]").forEach((button) => {
    button.addEventListener("click", () => {
      state.page = button.dataset.page;
      syncUrl(state);
      paint(state);
    });
  });

  document.querySelectorAll("[data-date]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedDate = button.dataset.date;
      paint(state);
    });
  });

  const datePicker = document.querySelector("[data-role='date-picker']");
  if (datePicker) {
    datePicker.addEventListener("change", (event) => {
      const value = event.target.value.replaceAll("-", "");
      if (state.dayGrouped.has(value)) {
        state.selectedDate = value;
        paint(state);
      }
    });
  }

  const selectedMonthSelect = document.querySelector("[data-role='selected-month']");
  if (selectedMonthSelect) {
    selectedMonthSelect.addEventListener("change", (event) => {
      state.selectedMonthKey = event.target.value;
      if (state.compareMonthKey === state.selectedMonthKey) {
        state.compareMonthKey = getDefaultCompareKey(
          state.selectedMonthKey,
          state.monthOptions.filter((key) => key !== state.selectedMonthKey)
        );
      }
      paint(state);
    });
  }

  const compareMonthSelect = document.querySelector("[data-role='compare-month']");
  if (compareMonthSelect) {
    compareMonthSelect.addEventListener("change", (event) => {
      state.compareMonthKey = event.target.value;
      paint(state);
    });
  }

  const monthCutoffSelect = document.querySelector("[data-role='month-cutoff']");
  if (monthCutoffSelect) {
    monthCutoffSelect.addEventListener("change", (event) => {
      state.monthCutoffDay = Number(event.target.value);
      paint(state);
    });
  }

  const selectedWeekSelect = document.querySelector("[data-role='selected-week']");
  if (selectedWeekSelect) {
    selectedWeekSelect.addEventListener("change", (event) => {
      state.selectedWeekKey = event.target.value;
      state.weekCutoffOptions = getWeekCutoffOptions(state, state.selectedWeekKey);
      state.weekCutoffIsoDay = state.weekCutoffOptions[state.weekCutoffOptions.length - 1]?.isoDay || state.weekCutoffIsoDay;
      if (state.compareWeekKey === state.selectedWeekKey) {
        state.compareWeekKey = getDefaultCompareWeekKey(
          state.selectedWeekKey,
          state.weekOptions.filter((key) => key !== state.selectedWeekKey)
        );
      }
      paint(state);
    });
  }

  const compareWeekSelect = document.querySelector("[data-role='compare-week']");
  if (compareWeekSelect) {
    compareWeekSelect.addEventListener("change", (event) => {
      state.compareWeekKey = event.target.value;
      paint(state);
    });
  }

  const weekCutoffSelect = document.querySelector("[data-role='week-cutoff']");
  if (weekCutoffSelect) {
    weekCutoffSelect.addEventListener("change", (event) => {
      state.weekCutoffIsoDay = Number(event.target.value);
      paint(state);
    });
  }

  const selectedYearSelect = document.querySelector("[data-role='selected-year']");
  if (selectedYearSelect) {
    selectedYearSelect.addEventListener("change", (event) => {
      state.selectedYear = Number(event.target.value);
      state.yearCutoffOptions = getYearCutoffOptions(state, state.selectedYear);
      state.yearCutoffMonthDay = state.yearCutoffOptions[state.yearCutoffOptions.length - 1] || state.yearCutoffMonthDay;
      if (state.compareYear === state.selectedYear) {
        state.compareYear = state.yearOptions.find((year) => year !== state.selectedYear) || state.selectedYear;
      }
      paint(state);
    });
  }

  const compareYearSelect = document.querySelector("[data-role='compare-year']");
  if (compareYearSelect) {
    compareYearSelect.addEventListener("change", (event) => {
      state.compareYear = Number(event.target.value);
      paint(state);
    });
  }

  const yearCutoffSelect = document.querySelector("[data-role='year-cutoff']");
  const sellerSearch = document.querySelector("[data-role='seller-search']");
  const stockSearch = document.querySelector("[data-role='stock-search']");
  if (yearCutoffSelect) {
    yearCutoffSelect.addEventListener("change", (event) => {
      state.yearCutoffMonthDay = event.target.value;
      paint(state);
    });
  }

  if (sellerSearch) {
    sellerSearch.addEventListener("input", (event) => {
      state.sellerQuery = event.target.value;
      refreshSellerResults(state);
    });
  }

  const sellerDatePicker = document.querySelector("[data-role='seller-date-picker']");
  if (sellerDatePicker) {
    sellerDatePicker.addEventListener("change", (event) => {
      const value = event.target.value.replaceAll("-", "");
      if (state.dayGrouped.has(value)) {
        state.sellerSelectedDate = value;
        syncUrl(state);
        repaintPreservingViewport(state);
      }
    });
  }

  if (stockSearch) {
    stockSearch.addEventListener("input", (event) => {
      state.stockQuery = event.target.value;
      refreshStockResults(state);
    });
  }

  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.monthMode = button.dataset.mode;
      paint(state);
    });
  });

  document.querySelectorAll("[data-week-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.weekMode = button.dataset.weekMode;
      paint(state);
    });
  });

  document.querySelectorAll("[data-week-panels-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.weekPanelsToggle;
      state.weekSummaryExpanded = state.weekSummaryExpanded.includes(key)
        ? state.weekSummaryExpanded.filter((value) => value !== key)
        : [...state.weekSummaryExpanded, key];
      repaintPreservingViewport(state);
    });
  });

  document.querySelectorAll("[data-day-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.dayToggle;
      state.dayExpandedDates = state.dayExpandedDates.includes(key)
        ? state.dayExpandedDates.filter((value) => value !== key)
        : [...state.dayExpandedDates, key];
      repaintPreservingViewport(state);
    });
  });

  document.querySelectorAll("[data-day-comparison-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.dayComparisonToggle;
      state.dayComparisonExpanded = state.dayComparisonExpanded.includes(key)
        ? state.dayComparisonExpanded.filter((value) => value !== key)
        : [...state.dayComparisonExpanded, key];
      repaintPreservingViewport(state);
    });
  });

  document.querySelectorAll("[data-period-comparison-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.periodComparisonToggle;
      if (state.page === "week") {
        state.weekComparisonExpanded = state.weekComparisonExpanded.includes(key)
          ? state.weekComparisonExpanded.filter((value) => value !== key)
          : [...state.weekComparisonExpanded, key];
      }
      if (state.page === "month") {
        state.monthComparisonExpanded = state.monthComparisonExpanded.includes(key)
          ? state.monthComparisonExpanded.filter((value) => value !== key)
          : [...state.monthComparisonExpanded, key];
      }
      repaintPreservingViewport(state);
    });
  });

  document.querySelectorAll("[data-month-panels-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.monthPanelsToggle;
      state.monthSummaryExpanded = state.monthSummaryExpanded.includes(key)
        ? state.monthSummaryExpanded.filter((value) => value !== key)
        : [...state.monthSummaryExpanded, key];
      repaintPreservingViewport(state);
    });
  });

  document.querySelectorAll("[data-year-panels-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.yearPanelsToggle;
      state.yearSummaryExpanded = state.yearSummaryExpanded.includes(key)
        ? state.yearSummaryExpanded.filter((value) => value !== key)
        : [...state.yearSummaryExpanded, key];
      repaintPreservingViewport(state);
    });
  });

  document.querySelectorAll("[data-year-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.yearMode = button.dataset.yearMode;
      paint(state);
    });
  });

  document.querySelectorAll("[data-seller-metric]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sellerMetric = button.dataset.sellerMetric;
      paint(state);
    });
  });

  document.querySelectorAll("[data-stock-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.stockFilter = button.dataset.stockFilter;
      paint(state);
    });
  });
}

function paint(state, viewState = null) {
  clearVisuals();
  if (state.page === "week") {
    app.innerHTML = renderWeekPage(state);
  } else if (state.page === "month") {
    app.innerHTML = renderMonthPage(state);
  } else if (state.page === "year") {
    app.innerHTML = renderYearPage(state);
  } else if (state.page === "people") {
    app.innerHTML = renderPeoplePage(state);
  } else if (state.page === "stock") {
    app.innerHTML = renderStockPage(state);
  } else {
    app.innerHTML = renderDayPage(state);
  }
  bindEvents(state);
  window.requestAnimationFrame(() => {
    restoreViewState(viewState);
    initVisuals(state);
  });
}

async function render() {
  const params = new URLSearchParams(window.location.search);
  const forcedUi = params.get("ui");
  if (forcedUi === "classic") {
    goClassic();
    return;
  }

  if (forcedUi === "beta") {
    setPreference("beta");
  }

  if (getPreference() === "classic" && forcedUi !== "beta") {
    window.location.replace(CLASSIC_URL);
    return;
  }

  try {
    const [dayData, monthData, sellerData, stockRows, updatedAt] = await Promise.all([
      loadDayData(),
      loadMonthData(),
      loadSellerData(),
      loadStockData(),
      loadUpdatedAt(),
    ]);

    const { canonicalMonths, monthOptions } = buildCanonicalMonths(dayData);
    const { canonicalYears, yearOptions } = buildCanonicalYears(dayData);
    const latestAvailableCutoffDay = Number(String(dayData.dates[0]).slice(6, 8));
    const latestAvailableCutoffMonthDay = formatMonthDayKey(dayData.dates[0]);
    const weekOptions = Array.from(dayData.weekDates.keys()).sort((left, right) => (left < right ? 1 : -1));
    const selectedWeekKey = weekOptions[0];
    const compareWeekKey = getDefaultCompareWeekKey(
      selectedWeekKey,
      weekOptions.filter((key) => key !== selectedWeekKey)
    );
    const weekCutoffOptions = getWeekCutoffOptions({ dayWeekDates: dayData.weekDates }, selectedWeekKey);
    const selectedMonthKey = monthOptions[0];
    const compareMonthKey = getDefaultCompareKey(
      selectedMonthKey,
      monthOptions.filter((key) => key !== selectedMonthKey)
    );
    const selectedYear = yearOptions[0];
    const compareYear = yearOptions.find((year) => year !== selectedYear) || selectedYear;
    const yearCutoffOptions = Array.from(
      new Set(
        dayData.dates
          .filter((dateKey) => String(dateKey).startsWith(String(selectedYear)))
          .map((dateKey) => formatMonthDayKey(dateKey))
      )
    ).sort();

    const state = {
      page: params.get("page") === "week"
        ? "week"
        : params.get("page") === "month"
          ? "month"
          : params.get("page") === "year"
            ? "year"
            : params.get("page") === "people"
              ? "people"
              : params.get("page") === "stock"
                ? "stock"
                : "day",
      chromeExpanded: true,
      updatedAt,
      dayGrouped: dayData.grouped,
      dayDates: dayData.dates,
      dayMonthDates: dayData.monthDates,
      dayWeekDates: dayData.weekDates,
      selectedDate: dayData.dates[0],
      dayExpandedDates: [],
      dayComparisonExpanded: [],
      weekOptions,
      selectedWeekKey,
      compareWeekKey,
      weekMode: "full",
      weekPanelsExpanded: false,
      weekSummaryExpanded: [],
      weekComparisonExpanded: [],
      weekCutoffOptions,
      weekCutoffIsoDay: weekCutoffOptions[weekCutoffOptions.length - 1]?.isoDay || 5,
      monthCanonical: canonicalMonths,
      monthCompareData: monthData.compareRows,
      monthOptions,
      latestAvailableCutoffDay,
      monthCutoffDay: latestAvailableCutoffDay,
      selectedMonthKey,
      compareMonthKey,
      monthMode: "full",
      monthPanelsExpanded: false,
      monthSummaryExpanded: [],
      monthComparisonExpanded: [],
      yearCanonical: canonicalYears,
      yearOptions,
      selectedYear,
      compareYear,
      yearMode: "full",
      yearPanelsExpanded: false,
      yearSummaryExpanded: [],
      yearCutoffOptions,
      latestAvailableCutoffMonthDay,
      yearCutoffMonthDay: latestAvailableCutoffMonthDay,
      sellerRawRows: sellerData.rawRows,
      sellerDayRows: sellerData.dayRows,
      sellerMonthRows: sellerData.monthRows,
      sellerYearRows: sellerData.yearRows,
      sellerLatestDay: sellerData.latestDay,
      sellerLatestMonthKey: sellerData.latestMonthKey,
      sellerLatestYear: sellerData.latestYear,
      sellerSelectedDate: params.get("sellerDate") && dayData.grouped.has(params.get("sellerDate")) ? params.get("sellerDate") : sellerData.latestDay,
      sellerMetric: "umomsValue",
      sellerQuery: "",
      stockRows,
      stockFilter: "all",
      stockQuery: "",
    };

    syncUrl(state);
    paint(state);
  } catch (error) {
    app.innerHTML = `
      <main class="page-shell">
        <section class="error-state">
          <p class="eyebrow">HIBERNIAN BETA</p>
          <h1>Kunne ikke laste beta-visningen</h1>
          <p class="intro">${error instanceof Error ? error.message : "Det oppstod en ukjent feil."}</p>
          <div class="actions">
            <button class="button button-secondary" type="button" data-action="classic">Åpne klassisk visning</button>
          </div>
        </section>
      </main>
    `;

    document.querySelectorAll("[data-action='classic']").forEach((button) => {
      button.addEventListener("click", goClassic);
    });
  }
}

render();
