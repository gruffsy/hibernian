
      /*
        Example kicking off the UI. Obviously, adapt this to your specific needs.
        Assumes you have a <div id="q-app"></div> in your <body> above
       */
     
      new Vue({
        el: '#q-app',
       
        data: function () {
          return {
              today: [],
              todayTot: [],
              pagination: {
                rowsPerPage: 30 // current rows per page being displayed
              },
              columns: [
               {
                 label: "Butikk",
                 align: 'left',
                 field: row => row.name,
                 format: val => `${val}`,
                 style: 'max-width: 50px',
                 },
                 {
                  label: "Beløp m/MV",
                  align: 'left',
                  field: row => row.name,
                  format: val => `${val}`,
                  style: 'max-width: 50px',
                  },
               ]    
          
        },
        methods: {
            getToday() {
                fetch("idag.sql.json")
                  .then(response => response.json())
                  .then(data => (this.today = data));
              },
              getTodayTotal() {
               fetch("idag_totalt.sql.json")
                 .then(response => response.json())
                 .then(data => (this.todayTot = data));
             },

        },
        mounted() {
            this.getToday();
            this.getTodayTotal();
            
          }
        // ...etc
      })
  