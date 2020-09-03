/*
        Example kicking off the UI. Obviously, adapt this to your specific needs.
        Assumes you have a <div id="q-app"></div> in your <body> above
       */

new Vue({
  el: "#q-app",

  data: function () {
    return {
      today: [],
      yesterday: [],
      dayBeforYesterday: [],
      updated: [],
      tab: 'idag',
      pagination: {
        rowsPerPage: 30, // current rows per page being displayed
      },
      columns: [
        {
          label: "Butikk",
          align: "left",
          field: (row) => row.butikk,
          format: (val) => `${val}`,
          style: "max-width: 130px",
          headerStyle: "max-width: 130px",
        },
        {
          label: "Beløp m/moms",
          align: "right",
          field: (row) => row.mmoms,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          label: "Beløp u/moms",
          align: "right",
          field: (row) => row.umoms,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          label: "DB",
          align: "right",
          field: (row) => row.db,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          label: "DG",
          align: "right",
          field: (row) => row.dg,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          label: "Antall kunder",
          align: "right",
          field: (row) => row.antord,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
        {
          label: "Per kunde",
          align: "right",
          field: (row) => row.prord,
          format: (val) => `${val}`,
          style: "max-width: 50px",
          headerStyle: "max-width: 50px",
        },
      ],
    };
  },
  methods: {
    getToday() {
      fetch("./json/idag.sql.json")
        .then((response) => response.json())
        .then((data) => (this.today = data));
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
    
  },
  mounted() {
    this.getToday();
    this.getYesterday();
    this.getDayBeforeYesterday();
    this.getTime();
  },
  // ...etc
});
