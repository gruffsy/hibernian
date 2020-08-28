
      /*
        Example kicking off the UI. Obviously, adapt this to your specific needs.
        Assumes you have a <div id="q-app"></div> in your <body> above
       */
     
      new Vue({
        el: '#q-app',
       
        data: function () {
          return {
              jsonfil: "test",
              results: []
          }
        },
        methods: {
            getWeatherData() {
                fetch("jsonlist.json")
                  .then(response => response.json())
                  .then(data => (this.results = data));
              }

        },
        mounted() {
            this.getWeatherData()
          }
        // ...etc
      })
  