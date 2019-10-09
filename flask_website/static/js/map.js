// Declare global variable
var myMap;
//listen the event
d3.selectAll("#selDataset").on("change", getValue);
d3.selectAll("#selList").on("change", searchValue);

//call flask api based on the top movies
function getValue() {
  var valueSelect = d3.select("#selDataset").node().value;
  var data = "/filterLessRange_IG_Rank/" + valueSelect;
  d3.selectAll("#valueInt").html("");
  d3.selectAll("#valueNorth").html("");
  // Using d3, fetch the JSON data
  d3.json(data).then(data => {
    // console.log(data);
    populateList(data);
  });
}

//select the list of movies that were populated dynamically
function searchValue() {
  var valueSelect = d3.select("#selList").node().value;
  getMovie(valueSelect);
}

//populated list dynamically based on the top movies
function populateList(data) {
  var selectOpt = d3.select("#selList");
  selectOpt.html("");
  for (var i = 0; i < data.length; i++) {
    var selectValues = data[i].movie_name;
    selectOpt
      .append("option")
      .text("Rank: " + data[i].rank + " - " + selectValues)
      .attr("value", function() {
        return data[i].rank;
      });
  }
}

//pass the rank to flask API to return the json content
function getMovie(rank) {
  var dataMongo = "/filterLessEq_IG_Rank/" + rank;
  d3.json(dataMongo).then(dataMongo => {
    // console.log(data);
    showMap(dataMongo);
  });
}

//clear the map from the webpage
function RemoveExistingMap(myMap) {
  if (myMap != null) {
    myMap.remove();
    myMap = null;
  }
}

// show map and markers
function showMap(data) {
  RemoveExistingMap(myMap);
  // Create a map object
  myMap = L.map("map", {
    center: [15.5994, -28.6731],
    zoom: 3
  });

  L.tileLayer(
    "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}",
    {
      attribution:
        'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      id: "mapbox.streets",
      accessToken: API_KEY
    }
  ).addTo(myMap);

  for (var i = 0; i < data.length; i++) {
    // get the first 10 countries
    var count = 0;
    var totalForeign = data[i].foreign_total_gross;
    var font;
    d3.selectAll("#valueInt").text(
      "International: " + numeral(data[i].foreign_total_gross).format("$0,0")
    );
    d3.selectAll("#valueNorth").text(
      "North America: " + numeral(data[i].domestic_total_gross).format("$0,0")
    );

    for (var j = 0; j < data[i].Foreign.length; j++) {
      var city = data[i].Foreign[j].country;
      var localTotal = data[i].Foreign[j].total_gross;
      var percent = (localTotal / totalForeign) * 100;

      if (percent < 1) {
        font = "red";
      } else {
        font = "blue";
      }

      // Create a new marker cluster group
      var markers = L.markerClusterGroup();

      // Set the data location property to a variable
      var latitude = data[i].Foreign[j].latitude;
      var longitude = data[i].Foreign[j].longitude;
      var population = data[i].Foreign[j].population;
      var language = data[i].Foreign[j].language;

      if (city == "South Korea") {
        latitude = 35.9;
        longitude = 127.76;
      } else if (city == "India") {
        latitude = 20.59;
        longitude = 78.96;
        population = 1339000000;
      }

      // Check for location property
      if (location) {
        // Add a new marker to the cluster group and bind a pop-up
        markers.addLayer(
          L.marker([latitude, longitude]).bindPopup(
            "<table>" +
              "<tr><td>" +
              "<img src=" +
              data[i].img_movie +
              "width='110' height='120'></td>" +
              "<td> <font color = " +
              font +
              "><h3>Country: " +
              city +
              "</h3></font><h4>Language: " +
              language +
              "<p>Total: " +
              numeral(localTotal).format("$0,0") +
              "<p>Global: " +
              percent.toString().substring(0, 4) +
              "%" +
              "<p>Population: " +
              numeral(population).format("0,0") +
              "</h4></td></table>"
          )
        );
      }

      // Add our marker cluster layer to the map
      myMap.addLayer(markers);
    }
  }
}
