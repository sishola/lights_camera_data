const filePath = "/json";



//Read samples data file
d3.json(filePath,data =>{

    
    var genres = data.map(movie => movie.Genre);

    //Since each movie's genre is an array of multiple actual genres, merge the arrays into one
    var mergedGenres = genres.join(",").split(",");


   //Split the array into objects to be grouped by count of each genre
    var splitObjects = mergedGenres.map(genre => ({'genre': genre, 'count' : 1}));

    //Group by count of each genre
    var groupedGenres = [];//array to store grouped genres

    splitObjects.reduce(function(res, value) {
        if (!res[value.genre]) {
            res[value.genre] = { genre: value.genre, count: 0 };
            groupedGenres.push(res[value.genre])
        }
        res[value.genre].count += value.count;
        return res;
    }, {});



    //Rename object key to match keys required by the AnyChart function
    groupedGenres = groupedGenres.map(function(obj) { 
        obj['x'] = obj['genre']; // Assign new key 
        delete obj['genre']; // Delete old key 
        
        obj['value'] = obj['count']; // Assign new key 
        delete obj['count']; // Delete old key 

        
        obj['category'] = obj['x']; // Assign new key for the legend

        return obj; 
    }); 
        
    

    //delete result["closure_uid_554144084"];


    anychart.onDocumentReady(function() {
       // create a tag (word) cloud chart
        var chart = anychart.tagCloud(groupedGenres);
      
         // set a chart title
        chart.title('Top Genres')
        // set an array of angles at which the words will be laid out
        chart.angles([0])
        // enable a color range
        chart.colorRange(true);
        // set the color range length
        chart.colorRange().length('80%');
      
        // display the word cloud chart
        chart.container("WordCloud_Container");
        chart.draw();
      });
   
})