const filePath = "/json"


//Read samples data file
d3.json(filePath,data => {


    var studioTitle = data.map(movie => [movie.Title, movie.Studio, 1]);


    function onlyUnique(value, index, self) { 
      return self.indexOf(value) === index;
    }
  
  // usage example:
    var studioList = data.map(movie => movie.Studio);
  var distinctStudios = studioList.filter( onlyUnique ); // returns ['a', 1, 2, '1']

  var studioHeader =  distinctStudios.map(studio => [studio, "Global", 0])

    var tableheader = [['Studio', 'Title', 'Value'], ['Global',null, 0]]

    var all = tableheader.concat(studioHeader).concat(studioTitle)
      console.log(all)

    google.charts.load("current", {packages:["treemap"]});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        var data = new google.visualization.arrayToDataTable(        
          all//.slice(1,100)
        );
        
        tree = new google.visualization.TreeMap(document.getElementById('TreeMap_Container'));

        var options = {
          highlightOnMouseOver: true,
          maxDepth: 1,
          maxPostDepth: 2,
          minHighlightColor: '#8c6bb1',
          midHighlightColor: '#9ebcda',
          maxHighlightColor: '#edf8fb',
          minColor: '#009688',
          midColor: '#f7f7f7',
          maxColor: '#ee8100',
          headerHeight: 15,
          showScale: true,
          height: 500,
          useWeightedAverageForAggregation: true
        };
  
        

        tree.draw(data, options);

   }
})