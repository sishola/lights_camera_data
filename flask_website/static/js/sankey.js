const filePath = "/json"


//Read samples data file
d3.json(filePath,data => {


    var studioTitle = data.map(movie => [movie.Studio, movie.Title, 1]);

      

    google.charts.load("current", {packages:["sankey"]});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'From');
        data.addColumn('string', 'To');
        data.addColumn('number', 'Weight');
        data.addRows(            
          studioTitle//.slice(1,100)
        );
        
        var colors = ['#a6cee3', '#b2df8a', '#fb9a99', '#fdbf6f',
                  '#cab2d6', '#ffff99', '#1f78b4', '#33a02c'];


        // Set chart options
        var options = {
            width: 1000,
            height: 1000,
            sankey: {
                node: {
                  colors: colors
                },
                link: {
                  colorMode: 'gradient',
                  colors: colors
                }
              }
        
        };

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.Sankey(document.getElementById('sankey_multiple'));
        chart.draw(data, options);
   }
})