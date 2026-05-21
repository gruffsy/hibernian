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
      idagselger: [],
      manedSelger: [],
      aarSelger: [],
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
        rowsPerPage: 300, // current rows per page being displayed
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
      stockColumns: [
        { name: 'expand', label: '', align: 'left' },
        { name: 'Prodno', label: 'Prodno', field: row => row.Prodno, align: 'left', sortable: true },
        { name: 'Beskrivelse', label: 'Beskrivelse', field: row => row.Beskrivelse, align: 'left', sortable: true },
        { name: 'antall_lager', label: 'Antall på lager', field: row => row['antall på lager'], align: 'right', sortable: true },
        { name: 'paller_lager', label: 'Paller på lager', field: row => row['Paller på lager'], align: 'right', sortable: true },
        { name: 'paller_vei', label: 'Paller på vei', field: row => row['Paller på vei'], align: 'right', sortable: true }
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
      fetch("./data/publish/salg_fra_22_pr_dag_med_total.json")
        .then((response) => response.json())
        .then((data) => (this.alldays = data));
    },
    getMonthCurrent() {
      const currentMonth = new Date().getMonth() + 1; // getMonth() returns a 0-based month, so add 1
      const currentYear = new Date().getFullYear();

      fetch("./data/publish/salg_fra_22_pr_mnd_med_total.json")
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
      fetch("./data/publish/salg_fra_22_pr_aar_med_total.json")
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
        "./data/publish/salg_fra_22_pr_mnd_med_total_og_sammenligning.json"
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

    getStock() {
      fetch('./data/json/lager_stock.sql.json')
        .then((response) => response.json())
        .then((data) => {
          this.stock = data; // Lagre lagerbeholdningen
          console.log("Stock Data:", data); // Konsollrapport for lagerdata
        });
    },
    getOrdersStock() {
      fetch('./data/publish/merged_stock_orders.json')
        .then((response) => response.json())
        .then((data) => {
          this.ordersStock = data; // Lagre tilleggsinformasjonen
          console.log("Orders Stock Data:", data); // Konsollrapport for tilleggsdata
         
        });
    },
 
    
    getTime() {
      fetch(
        "./data/publish/tid.json"
      )
        .then((response) => response.json())
        .then((data) => (this.updated = data));
    },
    getIdagSelger() {
      fetch("./data/publish/salg_pr_selger_fra_22_pr_dag.json")
        .then((response) => response.json())
        .then((data) => (this.idagselger = data));
    },
    getManedSelger(){
      fetch("./data/publish/salg_pr_selger_fra_22_pr_måned.json")
        .then((response) => response.json())
        .then((data) => (this.manedSelger = data));
    },
    getAarSelger() {
      fetch("./data/publish/salg_pr_selger_fra_22_pr_år.json")
        .then((response) => response.json())
        .then((data) => (this.aarSelger = data));
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
    this.getStock();
    this.getOrdersStock();
    this.getTime();
    this.getIdagSelger();
    this.getManedSelger();
    this.getAarSelger();
  },
  // ...etc
});
