/*
        Example kicking off the UI. Obviously, adapt this to your specific needs.
        Assumes you have a <div id="q-app"></div> in your <body> above
       */

new Vue({
  el: "#q-app",

  data: function () {
    return {
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
      filter: '',
      tab: 'dag',
      pagination: {
        rowsPerPage: 30, // current rows per page being displayed
      },
      columns: [
        {
          name: "butikk",
          label: "Butikk",
          align: "left",
          field: (row) => row.butikk,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        },
        {
          name: "mmoms",
          label: "Beløp m/moms",
          align: "right",
          field: (row) => row.mmoms,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        },
        {
          name: "ummoms",
          label: "Beløp u/moms",
          align: "right",
          field: (row) => row.umoms,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        },
        {
          name: "db",
          label: "DB",
          align: "right",
          field: (row) => row.db,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        },
        {
          name: "dg",
          label: "DG",
          align: "right",
          field: (row) => row.dg,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        },
        {
          name: "antord",
          label: "Antall kunder",
          align: "right",
          field: (row) => row.antord,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        },
        {
          name: "prord",
          label: "Per kunde",
          align: "right",
          field: (row) => row.prord,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px"
        }
      ],
    };
  },
  methods: {
    tableFormat(name) {
      if (
        name === "Totalt" 
      ) {
        return "bg-grey-4 text-bold";
      } else {
        return "bg-grey-3 text-black text-body";
      }
    },
    getToday() {
      fetch("./json/idag.sql.json")
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
    getLordagSelger() {
      fetch("./json/lordagselger.sql.json")
        .then((response) => response.json())
        .then((data) => (this.lordagselger = data));
    },
    getIdagSelger() {
      fetch("./json/idagselger.sql.json")
        .then((response) => response.json())
        .then((data) => (this.idagselger = data));
    },
    getIgarSelger() {
      fetch("./json/igarselger.sql.json")
        .then((response) => response.json())
        .then((data) => (this.igarselger = data));
    },
    getManedNaaSelger() {
      fetch("./json/manednaaselger.sql.json")
        .then((response) => response.json())
        .then((data) => (this.manednaaselger = data));
    },
    getIaarSelger() {
      fetch("./json/iaarselger.sql.json")
        .then((response) => response.json())
        .then((data) => (this.iaarselger = data));
    },
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
  mounted() {
    this.getToday();
    this.getBamble();
    this.getStock();
    this.getYesterday();
    this.getDayBeforeYesterday();
    this.getTime();
    this.getMonthNow();
    this.getMonthLastYear();
    this.getMonthCompare();
    this.getLordagSelger();
    this.getIdagSelger();
    this.getIgarSelger();
    this.getManedNaaSelger();
    this.getIaarSelger();
    this.getIaar();
    this.getIfjor();
    this.getYearCompare();
   

  },
  // ...etc
});
