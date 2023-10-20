/*
        Example kicking off the UI. Obviously, adapt this to your specific needs.
        Assumes you have a <div id="q-app"></div> in your <body> above
       */

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
      today: [],
      bamble: [],
      yesterday: [],
      dayBeforYesterday: [],
      manedNaa: [],
      manedIfjor: [],
      manedSammen: [],
      lordagselger: [],
      idagselger: [],
      igarselger: [],
      manednaaselger: [],
      iaarselger: [],
      iaar: [],
      ifjor: [],
      aarSammen: [],
      updated: [],
      stock: [],
      filter: "",
      filterselger: "",
      showDatePicker: false,
      tab: "dag",
      displayedTables: 3,
      pagination: {
        rowsPerPage: 30, // current rows per page being displayed
      },
      paginationSalesPersons: {
        rowsPerPage: 50, // current rows per page being displayed
      },
      columns: [
        {
          name: "butikk",
          label: "Butikk",
          align: "left",
          field: (row) => row.butikk,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          name: "mmoms",
          label: "Beløp m/moms",
          align: "right",
          field: (row) => row.mmoms,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          name: "ummoms",
          label: "Beløp u/moms",
          align: "right",
          field: (row) => row.umoms,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          name: "db",
          label: "DB",
          align: "right",
          field: (row) => row.db,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          name: "dg",
          label: "DG",
          align: "right",
          field: (row) => row.dg,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          name: "antord",
          label: "Antall kunder",
          align: "right",
          field: (row) => row.antord,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          name: "prord",
          label: "Per kunde",
          align: "right",
          field: (row) => row.prord,
          // format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
      ],
      myLocale: {
        /* starting with Sunday */
        days: "Søndag_Mandag_Tirsdag_Onsdag_Torsdag_Fredag_Lørdag".split("_"),
        daysShort: "Søn_Man_Tir_Ons_Tor_Fre_Lør".split("_"),
        months:
          "Januar_Februar_Mars_April_Mai_Juni_Juli_August_September_Oktober_November_December".split(
            "_"
          ),
        monthsShort: "Jan_Feb_Mar_Apr_Mai_Jun_Jul_Aug_Sep_Okt_Nov_Des".split(
          "_"
        ),
        firstDayOfWeek: 1, // 0-6, 0 - Sunday, 1 Monday, ...
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
      const startLimitDate = new Date(2022, 0, 1); // January 1, 2022
      const endLimitDate = new Date(); // Today's date

      return (
        currentDate.getDay() !== 0 && // Disable Sundays
        currentDate.getFullYear() >= startLimitDate.getFullYear() && // Disable years before 2022
        currentDate <= endLimitDate
      ); // Disable future dates
    },
    tableFormat(name) {
      if (name === "Totalt") {
        return "bg-grey-4 text-bold";
      } else {
        return "bg-grey-3 text-black text-body";
      }
    },
    getAllDays() {
      fetch("./revamp/publish/salg_fra_22_pr_dag_med_total.json")
        .then((response) => response.json())
        .then((data) => (this.alldays = data));
    },
    getMonthCurrent() {
      const currentMonth = new Date().getMonth() + 1; // getMonth() returns a 0-based month, so add 1
      const currentYear = new Date().getFullYear();

      fetch("./revamp/publish/salg_fra_22_pr_mnd_med_total.json")
        .then((response) => response.json())
        .then((data) => {
          this.MonthCurrent = data.filter(
            (entry) =>
              entry.month === currentMonth && entry.year === currentYear
          );
          this.MonthLastYear = data.filter(
            (entry) =>
              entry.month === currentMonth && entry.year === currentYear - 1
          );
        });
    },
    getYearCurrent(){
      const currentYear = new Date().getFullYear()
      fetch("./revamp/publish/salg_fra_22_pr_aar_med_total.json")
      .then((response) => response.json())
      .then((data) => {
        this.YearCurrent = data.filter(
          (entry) =>
            entry.year === currentYear
        );
        this.LastYear = data.filter(
          (entry) =>
            entry.year === currentYear - 1
        );
      });

    },
    getCompareLastYearMonth() {
      const currentMonth = new Date().getMonth() + 1; // getMonth() returns a 0-based month, so add 1
      const currentYear = new Date().getFullYear();

      fetch(
        "./revamp/publish/salg_fra_22_pr_mnd_med_total_og_sammenligning.json"
      )
        .then((response) => response.json())
        .then((data) => {
          this.CompareLastYearMonth = data.filter(
            (entry) =>
              entry.month === currentMonth &&
              entry.incomplete === true &&
              entry.this_year === currentYear
          );
          this.DiffLastYearMonth = data.filter(
            (entry) =>
              entry.month === currentMonth &&
              entry.incomplete === false &&
              entry.this_year === currentYear
          );
          this.ProjectedLastYearMonth = data.filter(
            (entry) =>
              entry.month === currentMonth &&
              entry.incomplete === null &&
              entry.this_year === currentYear
          );
        });
    },

    getToday() {
      fetch("./json/kombinertSalg.json")
        .then((response) => response.json())
        .then((data) => (this.today = data));
    },
    getBamble() {
      fetch("./salg.json")
        .then((response) => response.json())
        .then((data) => (this.bamble = data));
    },
    getStock() {
      fetch("./json/lager_stock.sql.json")
        .then((response) => response.json())
        .then((data) => (this.stock = data));
    },
    getYesterday() {
      fetch("./json/igar.sql.json")
        .then((response) => response.json())
        .then((data) => (this.yesterday = data));
    },
    getDayBeforeYesterday() {
      fetch("./json/iforgar.sql.json")
        .then((response) => response.json())
        .then((data) => (this.dayBeforYesterday = data));
    },
    getTime() {
      fetch("./json/tid.sql.json")
        .then((response) => response.json())
        .then((data) => (this.updated = data));
    },
    getMonthNow() {
      fetch("./json/manednaa.sql.json")
        .then((response) => response.json())
        .then((data) => (this.manedNaa = data));
    },
    getMonthLastYear() {
      fetch("./json/manedifjor.sql.json")
        .then((response) => response.json())
        .then((data) => (this.manedIfjor = data));
    },
    getMonthCompare() {
      fetch("./json/manedsammen.sql.json")
        .then((response) => response.json())
        .then((data) => (this.manedSammen = data));
    },
    // getLordagSelger() {
    //   fetch("./json/lordagselger.sql.json")
    //     .then((response) => response.json())
    //     .then((data) => (this.lordagselger = data));
    // },
    getIdagSelger() {
      fetch("./revamp/publish/salg_pr_selger_fra_22_pr_dag.json")
        .then((response) => response.json())
        .then((data) => (this.idagselger = data));
    },
    // getIgarSelger() {
    //   fetch("./json/igarselger.sql.json")
    //     .then((response) => response.json())
    //     .then((data) => (this.igarselger = data));
    // },
    // getManedNaaSelger() {
    //   fetch("./json/manednaaselger.sql.json")
    //     .then((response) => response.json())
    //     .then((data) => (this.manednaaselger = data));
    // },
    // getIaarSelger() {
    //   fetch("./json/iaarselger.sql.json")
    //     .then((response) => response.json())
    //     .then((data) => (this.iaarselger = data));
    // },
    getIaar() {
      fetch("./json/iaar.sql.json")
        .then((response) => response.json())
        .then((data) => (this.iaar = data));
    },
    getIfjor() {
      fetch("./json/ifjor.sql.json")
        .then((response) => response.json())
        .then((data) => (this.ifjor = data));
    },
    getYearCompare() {
      fetch("./json/aarsammen.sql.json")
        .then((response) => response.json())
        .then((data) => (this.aarSammen = data));
    },
  },
  computed: {
    displayedDataArray() {
      return this.groupedDataArray.slice(0, this.displayedTables);
    },
    groupedDataArray() {
      const groupedData = this.groupedData;
      return Object.keys(groupedData)
        .filter(
          (date) => this.selectedDate === null || date === this.selectedDate
        )
        .map((date) => {
          const year = parseInt(date.substring(0, 4));
          const month = parseInt(date.substring(4, 6)) - 1;
          const day = parseInt(date.substring(6, 8));
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
        .sort((a, b) => b.originalDate - a.originalDate)
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
    this.getAllDays();
    this.getMonthCurrent();
    this.getCompareLastYearMonth();
    this.getYearCurrent();
    // this.getToday();
    // this.getBamble();
    this.getStock();
    // this.getYesterday();
    // this.getDayBeforeYesterday();
    this.getTime();
    this.getMonthNow();
    this.getMonthLastYear();
    this.getMonthCompare();
    // this.getLordagSelger();
    this.getIdagSelger();
    // this.getIgarSelger();
    // this.getManedNaaSelger();
    // this.getIaarSelger();
    // this.getIaar();
    // this.getIfjor();
    // this.getYearCompare();
  },
  // ...etc
});
