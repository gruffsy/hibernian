const R2_BASE_URL = "https://pub-a1dbb638fdc8455c914f9f6c5f5b4564.r2.dev/latest";
const LOCAL_PUBLISH_BASE_URL = "./data/publish";
const LEGACY_JSON_BASE_URL = "./data/json";
const DAY_DATA_URL = {
  local: `${LOCAL_PUBLISH_BASE_URL}/salg_fra_22_pr_dag_med_total.json`,
  remote: `${R2_BASE_URL}/salg_fra_22_pr_dag_med_total.json`,
};
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

const TOTAL_STORE_NAME = "Totalt";
const TOTAL_CLIENT = "99";

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
  const response = await fetch(`${url}${separator}_ts=${Date.now()}`, {
    cache: "no-store",
  });

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

function parseDateKey(value) {
  return Number(String(value).replace(/\D/g, ""));
}

function parseCurrency(value) {
  return Number(String(value || "").replace(/[^\d-]/g, ""));
}

function parsePercent(value) {
  return Number(String(value || "").replace("%", "").replace(",", "."));
}

function parseInteger(value) {
  return Number(String(value || "").replace(/[^\d-]/g, ""));
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

function decodeMojibake(value) {
  if (typeof value !== "string") {
    return value;
  }

  if (!/[\u00C3\u00C2]/.test(value)) {
    return value;
  }

  try {
    const bytes = Uint8Array.from(value, (character) => character.charCodeAt(0));
    const decoded = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    return decoded.includes("\uFFFD") ? value : decoded;
  } catch {
    return value;
  }
}

function normalizeText(value) {
  return String(decodeMojibake(value || "")).trim();
}

function getStoreClientValue(row) {
  const raw = row.Klient == null ? row.client : row.Klient;
  const asText = String(raw == null ? "" : raw).trim();
  const asNumber = Number(asText.replace(/[^\d-]/g, ""));
  return Number.isFinite(asNumber) ? asNumber : 999;
}

function normalizeDayRow(row) {
  return {
    fakturadato: parseDateKey(row.fakturadato),
    butikk: normalizeText(row.butikk),
    Klient: String(row.Klient == null ? row.client || "" : row.Klient),
    mmomsValue: parseCurrency(row.mmoms),
    umomsValue: parseCurrency(row.umoms),
    dbValue: parseCurrency(row.db),
    dgValue: parsePercent(row.dg),
    antordValue: parseInteger(row.antord),
    prordValue: parseCurrency(row.prord),
  };
}

function formatStoreRow(row) {
  return {
    fakturadato: row.fakturadato,
    butikk: row.butikk,
    Klient: row.butikk === TOTAL_STORE_NAME ? 99 : row.Klient,
    mmoms: formatCurrency(row.mmomsValue),
    umoms: formatCurrency(row.umomsValue),
    db: formatCurrency(row.dbValue),
    dg: formatPercent(row.dgValue / 100),
    antord: formatInteger(row.antordValue),
    prord: formatCurrency(row.prordValue),
  };
}

function appendTotals(rows) {
  const totalsByDate = new Map();

  rows.forEach((row) => {
    if (row.butikk === TOTAL_STORE_NAME) {
      return;
    }

    const bucket = totalsByDate.get(row.fakturadato) || {
      mmomsValue: 0,
      umomsValue: 0,
      dbValue: 0,
      antordValue: 0,
    };

    bucket.mmomsValue += row.mmomsValue;
    bucket.umomsValue += row.umomsValue;
    bucket.dbValue += row.dbValue;
    bucket.antordValue += row.antordValue;
    totalsByDate.set(row.fakturadato, bucket);
  });

  const withTotals = rows.slice();
  totalsByDate.forEach((bucket, fakturadato) => {
    withTotals.push({
      fakturadato,
      butikk: TOTAL_STORE_NAME,
      Klient: TOTAL_CLIENT,
      mmomsValue: bucket.mmomsValue,
      umomsValue: bucket.umomsValue,
      dbValue: bucket.dbValue,
      dgValue: bucket.umomsValue ? (bucket.dbValue / bucket.umomsValue) * 100 : 0,
      antordValue: bucket.antordValue,
      prordValue: bucket.antordValue ? bucket.mmomsValue / bucket.antordValue : 0,
    });
  });

  return withTotals;
}

function sortStoreRows(rows) {
  return rows.slice().sort((left, right) => {
    if (left.fakturadato !== right.fakturadato) {
      return right.fakturadato - left.fakturadato;
    }
    return getStoreClientValue(left) - getStoreClientValue(right);
  });
}

function aggregateStoreRows(rows) {
  const grouped = new Map();

  rows.forEach((row) => {
    if (row.butikk === TOTAL_STORE_NAME) {
      return;
    }

    const key = row.Klient || row.butikk;
    if (!grouped.has(key)) {
      grouped.set(key, {
        fakturadato: row.fakturadato,
        butikk: row.butikk,
        Klient: row.Klient,
        mmomsValue: 0,
        umomsValue: 0,
        dbValue: 0,
        antordValue: 0,
      });
    }

    const bucket = grouped.get(key);
    bucket.mmomsValue += row.mmomsValue;
    bucket.umomsValue += row.umomsValue;
    bucket.dbValue += row.dbValue;
    bucket.antordValue += row.antordValue;
  });

  const aggregated = Array.from(grouped.values()).map((row) => ({
    ...row,
    dgValue: row.umomsValue ? (row.dbValue / row.umomsValue) * 100 : 0,
    prordValue: row.antordValue ? row.mmomsValue / row.antordValue : 0,
  }));

  return sortStoreRows(
    appendTotals(aggregated.map((row) => ({ ...row, fakturadato: aggregated[0]?.fakturadato || 0 })))
  ).filter((row, index, allRows) => index === 0 || row.fakturadato === allRows[0].fakturadato);
}

function diffStoreRows(leftRows, rightRows, fakturadato) {
  const leftByStore = new Map(leftRows.filter((row) => row.butikk !== TOTAL_STORE_NAME).map((row) => [row.Klient || row.butikk, row]));
  const rightByStore = new Map(rightRows.filter((row) => row.butikk !== TOTAL_STORE_NAME).map((row) => [row.Klient || row.butikk, row]));
  const keys = new Set([...leftByStore.keys(), ...rightByStore.keys()]);
  const rows = [];

  keys.forEach((key) => {
    const left = leftByStore.get(key) || { butikk: "", Klient: "", mmomsValue: 0, umomsValue: 0, dbValue: 0, antordValue: 0 };
    const right = rightByStore.get(key) || { butikk: left.butikk, Klient: left.Klient, mmomsValue: 0, umomsValue: 0, dbValue: 0, antordValue: 0 };
    const mmomsValue = left.mmomsValue - right.mmomsValue;
    const umomsValue = left.umomsValue - right.umomsValue;
    const dbValue = left.dbValue - right.dbValue;
    const antordValue = left.antordValue - right.antordValue;

    rows.push({
      fakturadato,
      butikk: left.butikk || right.butikk,
      Klient: left.Klient || right.Klient,
      mmomsValue,
      umomsValue,
      dbValue,
      dgValue: umomsValue ? (dbValue / umomsValue) * 100 : 0,
      antordValue,
      prordValue: antordValue ? mmomsValue / antordValue : 0,
    });
  });

  return sortStoreRows(appendTotals(rows));
}

function projectStoreRows(rows, latestDay, daysInMonth, fakturadato) {
  const factor = latestDay > 0 ? daysInMonth / latestDay : 1;
  const projected = rows
    .filter((row) => row.butikk !== TOTAL_STORE_NAME)
    .map((row) => ({
      fakturadato,
      butikk: row.butikk,
      Klient: row.Klient,
      mmomsValue: row.mmomsValue * factor,
      umomsValue: row.umomsValue * factor,
      dbValue: row.dbValue * factor,
      dgValue: row.dgValue,
      antordValue: row.antordValue * factor,
      prordValue: row.prordValue,
    }));

  return sortStoreRows(appendTotals(projected));
}

function rowsForMonth(rows, year, month, latestDay) {
  return rows.filter((row) => {
    const key = String(row.fakturadato);
    const rowYear = Number(key.slice(0, 4));
    const rowMonth = Number(key.slice(4, 6));
    const rowDay = Number(key.slice(6, 8));
    return rowYear === year && rowMonth === month && (latestDay == null || rowDay <= latestDay);
  });
}

function rowsForYear(rows, year, cutoffMonthDay) {
  return rows.filter((row) => {
    const key = String(row.fakturadato);
    const rowYear = Number(key.slice(0, 4));
    const monthDay = key.slice(4, 8);
    return rowYear === year && monthDay <= cutoffMonthDay;
  });
}

function normalizeSellerRow(row) {
  return {
    ukedag: normalizeText(row.ukedag),
    navn: normalizeText(row.navn),
    umomsValue: parseCurrency(row.umoms),
    dbValue: parseCurrency(row.db),
    butikk: normalizeText(row.butikk),
    fakturadato: parseDateKey(row.fakturadato),
  };
}

function formatSellerRow(row) {
  return {
    ukedag: row.ukedag,
    navn: row.navn,
    umoms: formatCurrency(row.umomsValue),
    db: formatCurrency(row.dbValue),
    butikk: row.butikk,
    fakturadato: row.fakturadato,
  };
}

function aggregateSellerRows(rows) {
  const grouped = new Map();

  rows.forEach((row) => {
    const key = `${row.navn}__${row.butikk}`;
    if (!grouped.has(key)) {
      grouped.set(key, {
        ukedag: row.ukedag,
        navn: row.navn,
        butikk: row.butikk,
        fakturadato: row.fakturadato,
        umomsValue: 0,
        dbValue: 0,
      });
    }

    const bucket = grouped.get(key);
    bucket.umomsValue += row.umomsValue;
    bucket.dbValue += row.dbValue;
    bucket.fakturadato = Math.max(bucket.fakturadato, row.fakturadato);
  });

  return Array.from(grouped.values())
    .sort((left, right) => right.umomsValue - left.umomsValue || left.navn.localeCompare(right.navn, "nb"))
    .map(formatSellerRow);
}

function normalizeStockRow(row) {
  const stockCount = parseInteger(row["antall på lager"] ?? row.antall_paa_lager);
  const pallets = parseInteger(row["Paller på lager"]);
  const palletsInbound = parseInteger(row["Paller på vei"]);

  return {
    Prodno: normalizeText(row.Prodno),
    Beskrivelse: normalizeText(row.Beskrivelse),
    "antall på lager": stockCount,
    "Paller på lager": pallets,
    "Paller på vei": palletsInbound,
    "Bestilling på vei": Array.isArray(row["Bestilling på vei"]) ? row["Bestilling på vei"] : [],
  };
}

new Vue({
  el: "#q-app",

  data: function () {
    return {
      selectedDate: null,
      alldays: [],
      MonthCurrent: [],
      MonthLastYear: [],
      CompareLastYearMonth: [],
      DiffLastYearMonth: [],
      ProjectedLastYearMonth: [],
      YearCurrent: [],
      LastYear: [],
      idagselger: [],
      manedSelger: [],
      aarSelger: [],
      sellerDaySource: [],
      updated: [],
      stock: [],
      ordersStock: [],
      filter: "",
      filterselger: "",
      showDatePicker: false,
      tab: "dag",
      selgerTab: "idag_selger",
      tabs: [
        { name: "idag_selger", label: "Dag" },
        { name: "måned_selger", label: "Måned" },
        { name: "år_selger", label: "År" },
      ],
      displayedTables: 3,
      pagination: {
        rowsPerPage: 300,
      },
      paginationSalesPersons: {
        rowsPerPage: 50,
      },
      columns: [
        { name: "butikk", label: "Butikk", align: "left", field: (row) => row.butikk, style: "max-width: 50px", headerStyle: "max-width: 50px" },
        { name: "mmoms", label: "Beløp m/moms", align: "right", field: (row) => row.mmoms, style: "max-width: 50px", headerStyle: "max-width: 50px" },
        { name: "ummoms", label: "Beløp u/moms", align: "right", field: (row) => row.umoms, style: "max-width: 50px", headerStyle: "max-width: 50px" },
        { name: "db", label: "DB", align: "right", field: (row) => row.db, style: "max-width: 50px", headerStyle: "max-width: 50px" },
        { name: "dg", label: "DG", align: "right", field: (row) => row.dg, style: "max-width: 50px", headerStyle: "max-width: 50px" },
        { name: "antord", label: "Antall kunder", align: "right", field: (row) => row.antord, style: "max-width: 50px", headerStyle: "max-width: 50px" },
        { name: "prord", label: "Per kunde", align: "right", field: (row) => row.prord, style: "max-width: 50px", headerStyle: "max-width: 50px" },
      ],
      stockColumns: [
        { name: "expand", label: "", align: "left" },
        { name: "Prodno", label: "Prodno", field: (row) => row.Prodno, align: "left", sortable: true },
        { name: "Beskrivelse", label: "Beskrivelse", field: (row) => row.Beskrivelse, align: "left", sortable: true },
        { name: "antall_lager", label: "Antall på lager", field: (row) => row["antall på lager"], align: "right", sortable: true },
        { name: "paller_lager", label: "Paller på lager", field: (row) => row["Paller på lager"], align: "right", sortable: true },
        { name: "paller_vei", label: "Paller på vei", field: (row) => row["Paller på vei"], align: "right", sortable: true },
      ],
      myLocale: {
        days: "Søndag_Mandag_Tirsdag_Onsdag_Torsdag_Fredag_Lørdag".split("_"),
        daysShort: "Søn_Man_Tir_Ons_Tor_Fre_Lør".split("_"),
        months: "Januar_Februar_Mars_April_Mai_Juni_Juli_August_September_Oktober_November_December".split("_"),
        monthsShort: "Jan_Feb_Mar_Apr_Mai_Jun_Jul_Aug_Sep_Okt_Nov_Des".split("_"),
        firstDayOfWeek: 1,
        format24h: true,
        pluralDay: "dager",
      },
    };
  },

  methods: {
    showMoreTables() {
      this.displayedTables += 7;
    },

    dateOptions(date) {
      const currentDate = new Date(date);
      const startLimitDate = new Date(2022, 0, 1);
      const endLimitDate = new Date();

      return (
        currentDate.getDay() !== 0 &&
        currentDate.getFullYear() >= startLimitDate.getFullYear() &&
        currentDate <= endLimitDate
      );
    },

    tableFormat(name) {
      return name === TOTAL_STORE_NAME ? "bg-grey-4 text-bold" : "bg-grey-3 text-black text-body";
    },

    async getAllDays() {
      const data = await fetchJsonWithFallback(DAY_DATA_URL);
      this.alldays = data;
      this.rebuildLegacyStoreViews();
    },

    async getTime() {
      this.updated = await fetchJsonWithFallback(META_URL);
    },

    async getOrdersStock() {
      const data = await fetchJsonWithFallback(STOCK_DATA_URL);
      const normalized = data.map(normalizeStockRow);
      this.ordersStock = normalized;
      this.stock = normalized;
    },

    async getIdagSelger() {
      const data = await fetchJsonWithFallback(SELLER_DAY_DATA_URL);
      this.sellerDaySource = data;
      this.rebuildLegacySellerViews();
    },

    getStock() {
      return Promise.resolve();
    },

    getMonthCurrent() {
      this.rebuildLegacyStoreViews();
    },

    getCompareLastYearMonth() {
      this.rebuildLegacyStoreViews();
    },

    getYearCurrent() {
      this.rebuildLegacyStoreViews();
    },

    getManedSelger() {
      this.rebuildLegacySellerViews();
    },

    getAarSelger() {
      this.rebuildLegacySellerViews();
    },

    rebuildLegacyStoreViews() {
      if (!Array.isArray(this.alldays) || this.alldays.length === 0) {
        return;
      }

      const normalizedRows = this.alldays.map(normalizeDayRow);
      const latestDateKey = Math.max(...normalizedRows.map((row) => row.fakturadato));
      const latestDateText = String(latestDateKey);
      const currentYear = Number(latestDateText.slice(0, 4));
      const currentMonth = Number(latestDateText.slice(4, 6));
      const latestDay = Number(latestDateText.slice(6, 8));
      const currentMonthRows = aggregateStoreRows(rowsForMonth(normalizedRows, currentYear, currentMonth, latestDay));
      const lastYearFullRows = aggregateStoreRows(rowsForMonth(normalizedRows, currentYear - 1, currentMonth));
      const lastYearMtdRows = aggregateStoreRows(rowsForMonth(normalizedRows, currentYear - 1, currentMonth, latestDay));
      const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
      const cutoffMonthDay = latestDateText.slice(4, 8);
      const currentYearRows = aggregateStoreRows(rowsForYear(normalizedRows, currentYear, cutoffMonthDay));
      const lastYearRows = aggregateStoreRows(rowsForYear(normalizedRows, currentYear - 1, "1231"));

      this.MonthCurrent = currentMonthRows.map(formatStoreRow);
      this.MonthLastYear = lastYearFullRows.map(formatStoreRow);
      this.DiffLastYearMonth = diffStoreRows(currentMonthRows, lastYearFullRows, latestDateKey).map(formatStoreRow);
      this.CompareLastYearMonth = diffStoreRows(currentMonthRows, lastYearMtdRows, latestDateKey).map(formatStoreRow);
      this.ProjectedLastYearMonth = projectStoreRows(currentMonthRows, latestDay, daysInMonth, latestDateKey).map(formatStoreRow);
      this.YearCurrent = currentYearRows.map(formatStoreRow);
      this.LastYear = lastYearRows.map(formatStoreRow);
    },

    rebuildLegacySellerViews() {
      if (!Array.isArray(this.sellerDaySource) || this.sellerDaySource.length === 0) {
        return;
      }

      const normalizedRows = this.sellerDaySource.map(normalizeSellerRow);
      const latestDateKey = Math.max(...normalizedRows.map((row) => row.fakturadato));
      const latestDateText = String(latestDateKey);
      const currentYear = Number(latestDateText.slice(0, 4));
      const currentMonth = Number(latestDateText.slice(4, 6));

      this.idagselger = normalizedRows
        .filter((row) => row.fakturadato === latestDateKey)
        .sort((left, right) => right.umomsValue - left.umomsValue)
        .map(formatSellerRow);
      this.manedSelger = aggregateSellerRows(rowsForMonth(normalizedRows, currentYear, currentMonth));
      this.aarSelger = aggregateSellerRows(
        normalizedRows.filter((row) => String(row.fakturadato).startsWith(String(currentYear)))
      );
    },
  },

  computed: {
    displayedDataArray() {
      return this.groupedDataArray.slice(0, this.displayedTables);
    },

    groupedDataArray() {
      const groupedData = this.groupedData;
      return Object.keys(groupedData)
        .filter((date) => this.selectedDate === null || date === this.selectedDate)
        .map((date) => {
          const year = parseInt(date.substring(0, 4), 10);
          const month = parseInt(date.substring(4, 6), 10) - 1;
          const day = parseInt(date.substring(6, 8), 10);
          const dateObject = new Date(year, month, day);

          const formattedDate = new Intl.DateTimeFormat("nb-NO", {
            weekday: "long",
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
          }).format(dateObject);

          return {
            date: formattedDate,
            rows: groupedData[date],
            originalDate: dateObject,
          };
        })
        .sort((left, right) => right.originalDate - left.originalDate)
        .map(({ date, rows }) => ({ date, rows }));
    },

    groupedData() {
      return this.alldays.reduce((acc, row) => {
        const date = row.fakturadato;
        if (!acc[date]) {
          acc[date] = [];
        }
        acc[date].push(row);
        return acc;
      }, {});
    },
  },

  mounted() {
    this.sellerDaySource = [];
    this.getAllDays();
    this.getStock();
    this.getOrdersStock();
    this.getTime();
    this.getIdagSelger();
    this.getManedSelger();
    this.getAarSelger();
  },
});
