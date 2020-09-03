
      /*
        Example kicking off the UI. Obviously, adapt this to your specific needs.
        Assumes you have a <div id="q-app"></div> in your <body> above
       */
     
      new Vue({
        el: '#q-app',
       
        data: function () {
          return {
              today: [],
              todayTot: {"Totalt":"Totalt","Beløp m\/mva":" 170 415 kr","Beløp u\/mva":" 136 332 kr","DB":" 39 586 kr","DG":"29.04%","Antall ordre":"  169","per kunde":" 1 008 kr"},
              pagination: {
                rowsPerPage: 30 // current rows per page being displayed
              },
              
          }
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
            
          }
        // ...etc
      })
  